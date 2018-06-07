import csv

from importer.base import Importer


class CSVImporter(Importer):

    def __init__(self, **kwargs):
        self.file = kwargs.pop("file", None)
        self.delimiter = kwargs.pop("delimeter", ",")
        super().__init__(**kwargs)

    def get_data(self):
        csvreader = csv.DictReader(self.file)
        for row in csvreader:
            row = self.sanitize_field_names(row)
            print("Yielding row: {}".format(row))
            yield row

    def sanitize_field_names(self, row):
        """ Removes spaces from field names
        """
        sanitized_row = {}
        for field_name in row.keys():
            val = row[field_name]
            if " " in field_name:
                field_name = field_name.replace(" ", "_")
            sanitized_row[field_name] = val
        return sanitized_row
