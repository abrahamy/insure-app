from enum import Enum

from django.db import models


class DataType(Enum):
    BOOL = "Boolean"
    CURRENCY = "Currency"
    DATE = "Date"
    ENUM = "Enum"
    NUMBER = "Number"
    TEXT = "Text"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class ListField(models.Field):
    """The ListField is used to serialize a python list into a string in the database
    and deserialize it back to a python list in python."""

    def __init__(self, *args, **kwargs):
        self.separator = "||"
        super().__init__(*args, *kwargs)

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def to_python(self, value):
        if isinstance(value, list):
            return value

        if value is None:
            return value

        return [i.strip() for i in str(value).split(self.separator)]


class Field(models.Model):
    name = models.CharField("Name", max_length=75)
    data_type = models.CharField("Data Type", max_length=10, choices=DataType.choices())
    enum_choices = ListField("Options", null=True)


class Attribute(models.Model):
    field = models.ForeignKey(Field, on_delete=models.PROTECT, related_name="values")

    boolean = models.NullBooleanField("Boolean", null=True)
    currency = models.DecimalField("Currency", null=True)
    date = models.DateTimeField("Date", null=True)
    enum = models.CharField("Enum", max_length=500)
    number = models.IntegerField("Number", null=True)
    text = models.CharField("Text", max_length=500, null=True)

    @property
    def value(self):
        """Get the actual value of the field."""
        attrs = {i.name: i.value.lower() for i in DataType}
        return getattr(self, attrs[self.field.data_type])

    def __str__(self):
        """Get a string representation of the Value object."""
        field = self.field.name
        value = self.value

        return f"Value({field}: {value!r})"


class RiskType(models.Model):
    name = models.CharField("Risk Type", max_length=100, unique=True)
    fields = models.ManyToManyField(Field, related_name="risk_types")


class Risk(models.Model):
    risk_type = models.ForeignKey(
        RiskType, on_delete=models.PROTECT, verbose_name="Risk Type"
    )
    attributes = models.ManyToManyField(Attribute)
