from collections import namedtuple

CSVConfiguration = \
    namedtuple(
        'CSVConfiguration',
        ['allowed_fields', 'mandatory_field_names', 'delimeter'])

CSVField = namedtuple('CSVField', ['field_name', 'title', 'datatype'])


class CSVImporter(object):

    def __init__(self, configuration=None, filename=None):
        self.configuration = configuration
        if filename:
            self.load(filename=filename)

    def load(self, filename=None):
        if not hasattr(self, "_data"):
            self._data = open(filename).read().splitlines()
        return self._data

    def get_data(self):
        data = []
        for i, row in enumerate(self._data):
            if i == 0 or i == len(self._data) - 1:
                continue  # skip the header and footer
            data.append(self.get_row_from_str(row))
        return data

    def get_row_from_str(self, row=None):
        columns = row.split(self.configuration.delimeter)


    def get_header(self):
        pass

    def get_footer(self):
        pass
