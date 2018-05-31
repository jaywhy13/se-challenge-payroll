from io import StringIO

from django.db import IntegrityError, transaction, DatabaseError
from django.db import models
from django.db.models import F, Min, Max, Sum

from payroll.constants import (
    DATE_FORMATS, COUNTRIES, PAY_PERIODS, TIMESHEET_UNITS,
    DEFAULT_DATE_FORMAT,
)
from importer import CSVImporter, ImporterConfiguration
from importer import DateField, StringField, IntegerField, DecimalField


class Partner(models.Model):

    name = models.CharField(max_length=255)
    default_profile = models.OneToOneField(
        "PartnerProfile", related_name="+", blank=True, null=True)


class PartnerProfile(models.Model):

    name = models.CharField(max_length=255)
    partner = models.ForeignKey("Partner", related_name='profiles')
    date_format = models.CharField(max_length=255, choices=DATE_FORMATS)
    country = models.CharField(max_length=255, choices=COUNTRIES)
    pay_period = models.CharField(max_length=255, choices=PAY_PERIODS)


class EmployeeGroup(models.Model):

    class Meta:
        unique_together = ['name', 'partner_profile']

    name = models.CharField(max_length=255)
    rate = models.DecimalField(max_digits=11, decimal_places=2)
    partner_profile = models.ForeignKey(
        "PartnerProfile", related_name="employee_groups")


class EmployeeTime(models.Model):
    """ A record of units of time that an employee has worked. The time
        worked is generally tied to a timesheet.
    """
    start_date = models.DateField()
    end_date = models.DateField()
    unit = models.CharField(max_length=255, choices=TIMESHEET_UNITS)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    timesheet = models.ForeignKey(
        "EmployeeTimesheet", blank=True, null=True, on_delete=models.CASCADE,
        related_name="employee_time_records")
    employee_id = models.IntegerField()
    employee_group = models.ForeignKey(
        "EmployeeGroup", related_name="employee_time_records")


class EmployeeTimesheet(models.Model):

    class Meta:
        unique_together = ['partner', 'key']

    partner = models.ForeignKey(
        "Partner", blank=True, null=True, related_name="timesheets")
    partner_profile = models.ForeignKey(
        "PartnerProfile", blank=True, null=True, related_name='timesheets')
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    source = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{} Timesheet (key={})".format(self.partner, self.key)

    @classmethod
    def create_timesheet(
            cls, partner=None, partner_profile=None,
            report_id=None, data=None, source=None, name=None):
        """ Creates a timesheet given a report id and a list of dicts of data
        """
        timesheet_exists = \
            EmployeeTimesheet.timesheet_exists(
                partner=partner, partner_profile=partner_profile,
                report_id=report_id)
        if timesheet_exists:
            raise Exception(
                "Cannot create timesheet with ID {} for {}. "
                "One already exists".format(report_id, partner_profile))
        timesheet = \
            EmployeeTimesheet.objects.create(
                partner=partner,
                partner_profile=partner_profile,
                name=name,
                key=report_id,
                source=source)
        for row in data:
            print("Creating time for row: {}".format(row))
            start_date = row.get("date")
            end_date = row.get("end_date") or start_date
            employee_id = row.get("employee_id")
            hours_worked = row.get("hours_worked")
            job_group = row.get("job_group")
            employee_group = EmployeeGroup.objects.get(
                partner_profile=partner_profile,
                name=job_group)
            EmployeeTime.objects.create(timesheet=timesheet,
                                        start_date=start_date,
                                        end_date=end_date,
                                        unit="hour",
                                        quantity=hours_worked,
                                        employee_group=employee_group,
                                        employee_id=employee_id)
        return timesheet

    @classmethod
    def timesheet_exists(
            cls, partner=None, partner_profile=None, report_id=None):
        filter_kwargs = {}
        if partner:
            filter_kwargs["partner"] = partner
        if partner_profile:
            filter_kwargs["partner_profile"] = partner_profile
        if report_id:
            filter_kwargs["key"] = report_id
        return EmployeeTimesheet.objects.filter(**filter_kwargs).exists()

    @classmethod
    def get_report_id_and_data_from_csv(cls, file=None):
        filedata = EmployeeTimesheet._get_csv_as_str(file)
        header_line, *lines, report_id_line = filedata.splitlines()
        csv_data = StringIO("\n".join(map(str, lines)))
        configuration = \
            EmployeeTimesheet.get_csv_importer_configuration()
        importer = CSVImporter(configuration=configuration, file=csv_data)
        report_id = EmployeeTimesheet.parse_report_id(str(report_id_line))
        imported_data = [row for row in importer]
        return report_id, imported_data

    @classmethod
    def _get_csv_as_str(cls, file=None):
        return file.read().decode("utf-8")

    @classmethod
    def get_csv_importer_configuration(cls):
        """ This tells the importer what fields we want from the CSV file
        """
        fields = [
            DateField("date", format=DEFAULT_DATE_FORMAT, required=True),
            DateField("end_date", format=DEFAULT_DATE_FORMAT),
            DecimalField("hours_worked", minimum_exclusive=0, required=True),
            IntegerField("employee_id", ignore_sign=True, required=True),
            StringField("job_group", required=True)
        ]
        return ImporterConfiguration(fields=fields)

    @classmethod
    def get_timesheet_report(cls, partner=None, partner_profile=None):
        """ Returns a report for display of employee hours
        """
        filter_kwargs = {}
        if partner:
            filter_kwargs["timesheet__partner"] = partner
        if partner_profile:
            filter_kwargs["timesheet__partner_profile"] = partner_profile
        records = \
            EmployeeTime.objects.\
                filter(**filter_kwargs).\
                order_by("employee_id").\
                values("employee_id").\
                annotate(
                    total_quantity=Sum("quantity"),
                    amount_paid=(F("total_quantity") * \
                                           F("employee_group__rate")),
                    start_of_period=Min("start_date"),
                    end_of_period=Max("start_date")).\
                values(
                    "total_quantity", "amount_paid", "start_of_period",
                    "end_of_period", "employee_id")
        return EmployeeTimesheet._combine_employee_group_pay(records)

    @classmethod
    def _combine_employee_group_pay(cls, records):
        """ This function summarizes the employees pays across the different
            groups they may have been apart of.
        """
        employee_cache = {}
        for record in records:
            employee_id = record.get("employee_id")
            if employee_id not in employee_cache:
                employee_cache[employee_id] = record
            else:
                employee_record = employee_cache.get(employee_id)
                employee_record["start_of_period"] = \
                    min(employee_record["start_of_period"],
                        record["start_of_period"])
                employee_record["end_of_period"] = \
                    max(employee_record["end_of_period"],
                        record["end_of_period"])
                employee_record["amount_paid"] += record["amount_paid"]
        employee_ids = sorted(employee_cache.keys())
        return [
            employee_cache.get(employee_id) for employee_id in employee_ids]



    @classmethod
    def parse_report_id(cls, report_id_line):
        return report_id_line.split(",")[1].strip()
