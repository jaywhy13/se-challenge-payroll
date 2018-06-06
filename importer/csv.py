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
            yield row
