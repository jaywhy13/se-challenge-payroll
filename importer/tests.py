from io import StringIO
from datetime import datetime

from django.test import TestCase

from importer import Importer, CSVImporter, ImporterConfiguration
from importer import (
    DateField, IntegerField, DecimalField, StringField
)

TEST_DATA_STRING = """date,hours_worked,employee_id,job_group
14/11/2016,7.5,1,A
9/11/2016,4,2,B"""
DATE_FORMAT = "%d/%m/%Y"


class SimpleImporter(Importer):
    """ A simple importer that takes data and just returns what it gets
    """

    def __init__(self, *args, **kwargs):
        self.data = kwargs.pop("data", [])
        super().__init__(*args, **kwargs)

    def get_data(self):
        return self.data


class TestImporterConfiguration(TestCase):

    def get_importer(self, configuration=None, data=[]):
        """ Returns a SimpleImporter
        """
        if not configuration:
            configuration = self.get_importer_configuration()
        simple_importer = SimpleImporter(
            configuration=configuration, data=data)
        return simple_importer

    def get_importer_configuration(self):
        """ Returns a test configuration
        """
        fields = [
            DateField("date", format=DATE_FORMAT, required=True),
            DateField("end_date", format=DATE_FORMAT, required=False),
            DecimalField("hours_worked", minimum_exclusive=0, required=True),
            IntegerField("employee_id", ignore_sign=True, required=True),
            StringField("job_group", required=True)
        ]
        configuration = ImporterConfiguration(fields=fields)
        return configuration

    def test_field_attributes(self):
        """ Ensures that fields are properly registered on the Importer
            and also ensures common properties work.
        """
        importer = self.get_importer()
        field_names = [
            "date", "end_date", "hours_worked", "employee_id", "job_group"]
        for field_name in field_names:
            self.assertIsNotNone(importer)
            self.assertIn(field_name, importer)
        required_field_names = [
            "date", "hours_worked", "employee_id", "job_group"]
        for field_name in required_field_names:
            field = importer[field_name]
            self.assertTrue(field.required)
        self.assertFalse(importer["end_date"].required)

    def test_field_validation(self):
        """ Tests to ensure our fields validate data properly
        """
        importer = self.get_importer()
        for data in self.get_invalid_test_data():
            with self.assertRaises(Exception):
                importer.validate(data)
        for data in self.get_valid_test_data():
            self.assertTrue(importer.validate(data))

    def get_invalid_test_data(self):
        """ Returns invalid test data
        """
        return [
            # Do some general test cases
            dict(),  # required fields should be filled out
            # Date-based errors
            dict(date="abc", hours_worked=1, employee_id=1, job_group="A"),
            dict(date="10/44/2018", hours_worked=1,
                 employee_id=1, job_group="A"),
            dict(date="01/01/18", hours_worked=1,
                 employee_id=1, job_group="A"),
            # Decimal based errors for date
            dict(date="01/01/2018", hours_worked="abc",
                 employee_id=1, job_group="A"),
            dict(date="10/44/2018", hours_worked=-1,
                 employee_id=1, job_group="A"),
            dict(date="10/44/2018", hours_worked=0,  # violates the min
                 employee_id=1, job_group="A"),
            # Integer based errors using employee_id
            dict(date="01/01/2018", hours_worked=1,
                 employee_id="2A", job_group="A"),
            dict(date="01/01/2018", hours_worked=1,
                 employee_id="abc", job_group="A"),
        ]

    def get_valid_test_data(self):
        return [
            dict(data="01/01/2018", hours_worked=1,
                 employee_id=1, job_group="A"),
            dict(data="01/01/2018", hours_worked=1.5,
                 employee_id=1, job_group="A"),
            dict(data="01/01/2018", end_date="10/01/2018", hours_worked=1,
                 employee_id=1, job_group="A"),
        ]


class TestCSVImporter(TestCase):

    def test_csv_importer(self):
        csv_importer = self.get_test_csv_importer()
        csv_data = list(csv_importer.get_data())
        expected_data = self.get_expected_data()
        self.assertEquals(len(csv_data), len(expected_data))
        for i, row in enumerate(csv_data):
            expected_row = expected_data[i]
            actual_row = csv_data[i]
            self.assertTrue(isinstance(actual_row, dict))
            for field_name, expected_value in expected_row.items():
                self.assertEqual(actual_row.get(field_name), expected_value)

    def get_test_csv_importer(self):
        return CSVImporter(
            file=self.get_test_csv_file(),
            configuration=self.get_importer_test_configuration())

    def get_test_csv_file(self):
        return StringIO(TEST_DATA_STRING)

    def get_importer_test_configuration(self):
        """ Returns a test CSV configuration
        """
        fields = [
            DateField("date", format=DATE_FORMAT, required=True),
            DateField("end_date", format=DATE_FORMAT),
            DecimalField("hours_worked", minimum_exclusive=0, required=True),
            IntegerField("employee_id", ignore_sign=True, required=True),
            StringField("job_group", required=True)
        ]
        importer_configuration = ImporterConfiguration(fields=fields)
        return importer_configuration

    def get_expected_data(self):
        rows = []
        for line in TEST_DATA_STRING.splitlines()[1:]:
            pieces = line.split(",")
            rows.append({
                "date": datetime.strptime(pieces[0], DATE_FORMAT),
                "hours_worked": float(pieces[1]),
                "employee_id": int(pieces[2]),
                "job_group": pieces[3],
            })
        return rows
