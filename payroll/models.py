from django.db import models

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

    start_date = models.DateField()
    end_date = models.DateField()
    unit = models.CharField(max_length=255, choices=TIMESHEET_UNITS)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    timesheet = models.ForeignKey(
        "EmployeeTimesheet", blank=True, null=True, on_delete=models.CASCADE)


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
