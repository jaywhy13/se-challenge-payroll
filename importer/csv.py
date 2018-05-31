import csv

from importer.base import Importer


class CSVImporter(Importer):

    def __init__(self, **kwargs):
        self.file = kwargs.pop("file", None)
        self.delimiter = kwargs.pop("delimeter", ",")
        super().__init__(**kwargs)

    def get_data(self):
        csvreader = csv.reader(self.file)
        for row in csvreader:
            field_names = ["date", "hours_worked", "employee_id", "job_group"]
            row_dict = dict(zip(field_names, row))
            yield row_dict
