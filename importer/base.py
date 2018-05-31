from collections import namedtuple

ImporterConfiguration = namedtuple('ImporterConfiguration', ['fields'])

class Importer(object):

    def __init__(self, configuration=None):
        if not isinstance(configuration, ImporterConfiguration):
            raise ValueError(
                "Invalid configuration provided: {}".format(configuration))
        if not configuration:
            raise Exception(
                "Please provide a valid configuration "
                "for the Importer")
        self.configuration = configuration
        self.fields = {
            field.name: field for field in self.configuration.fields
        }

    def __contains__(self, field_name):
        return field_name in self.fields

    def __getitem__(self, field_name):
        return self.fields.get(field_name)

    def __len__(self):
        return len(self.fields)

    def __iter__(self):
        for row in self.get_data():
            yield self.prepare_row(row)

    @property
    def required_fields(self):
        return [field for field in self.fields.values() if field.required]

    def prepare_row(self, row):
        formatted_row = {}
        for field_name, field in self.fields.items():
            formatted_row[field_name] = field.to_python(row.get(field_name))
        return formatted_row

    def get_data(self):
        raise NotImplementedError(
            "Please implement the Importer.get_data function")

    def validate(self, data=None):
        """ Validates a single row of data passed to importer. This raises an
            exception if the data is not valid

            :param dict data - a single row of data passed to the validator
        """
        if not data.keys() and self.required_fields:
            raise Exception(
                "Please fill in the missing required fields")
        for field_name in data.keys():
            if field_name not in self:
                raise Exception(
                    "Invalid field found in data: {}".format(field_name))
                field = self[field_name]
                field_data = data.get(field_name)
                field.validate(field_data)
        return True

    def is_valid(self):
        """ Runs through each row of data and tells us if it's valid. Throws
            an exception otherwise
        """
        for row in self.get_data():
            self.validate(data=row)
        return True
