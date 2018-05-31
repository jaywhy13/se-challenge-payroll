from datetime import datetime


class Field(object):
    """ A field that receives some data and may be validated
    """

    def __init__(self, name=None, required=True):
        self.name = name
        self.required = required

    def validate(self, data):
        if self.required and not data:
            raise ValueError(
                "{} is required, cannot provide: {}".format(self.name, data))
        return True

    def to_python(self, data=None):
        return data


class DateField(Field):

    def __init__(self, *args, **kwargs):
        self.format = kwargs.pop("format", "%d/%m/%Y")
        super().__init__(*args, **kwargs)

    def validate(self, data=None):
        super().validate(data=data)
        if data:
            self.to_python(data=data)

    def to_python(self, data=None):
        if data:
            return datetime.strptime(data, self.format)


class IntegerField(Field):

    def __init__(
            self, *args, **kwargs):
        self.minimum_inclusive = kwargs.pop("minimum_inclusive", None)
        self.minimum_exclusive = kwargs.pop("minimum_exclusive", None)
        self.maximum_inclusive = kwargs.pop("maximum_inclusive", None)
        self.maximum_exclusive = kwargs.pop("maximum_exclusive", None)
        self.ignore_sign = kwargs.pop("ignore_sign", True)
        super().__init__(*args, **kwargs)

    def validate(self, data=None):
        # We will do required checks ourselves, so don't call super
        self.validate_required(data=data)
        self.validate_format(data=data)
        self.validate_minimum_and_maximum(data=data)

    def validate_required(self, data=None):
        if not self.required:
            return
        if data is None:
            raise ValueError("Data for {} cannot be None".format(self.name))

    def validate_format(self, data=None):
        self.to_python(data)  # try to cast it to an int

    def validate_minimum_and_maximum(self, data=None):
        if self.minimum_inclusive and data < self.minimum_inclusive:
            raise ValueError(
                "{} must be greater than {}".format(
                data, self.minimum_inclusive))
        if self.minimum_exclusive and data <= self.minimum_exclusive:
            raise ValueError(
                "{} must be greater than {}".format(
                data, self.minimum_exclusive))
        if self.maximum_inclusive and data < self.maximum_inclusive:
            raise ValueError(
                "{} must be greater than {}".format(
                data, self.maximum_inclusive))
        if self.maximum_inclusive and data < self.maximum_exclusive:
            raise ValueError(
                "{} must be greater than {}".format(
                data, self.maximum_exclusive))

    def to_python(self, data=None):
        if data:
            return int(data)


class DecimalField(IntegerField):

    def validate_format(self, data=None):
        float(data)  # try to cast to a float


    def to_python(self, data=None):
        if data:
            return float(data)


class StringField(Field):

    def validate(self, data=None):
        super().validate(data=data)
        if not isinstance(data, basestring):
            raise ValueError(
                "{} is not a valid string".format(data))
