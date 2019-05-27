import datetime

from asyncorm.exceptions import *


class Field:
    def __init__(self, f_type, blank=False, dbtype=None, required=True, default=None):
        self.f_type = f_type
        self.blank = blank
        self.dbtype = dbtype
        self.required = required
        self.default = default
    def validate(self, value):
        if value is None and not self.required:
            return None
        elif value is None and self.required:
            raise InputError('Need to input required fields in {}s'.format(type(self).__name__))
        if self.f_type == datetime.date:
            if isinstance(value, datetime.date):
                return value.strftime('%Y-%m-%d')
            elif isinstance(value, list) or isinstance(value, tuple):
                return datetime.date(*value).strftime('%Y-%m-%d')
            elif isinstance(value, dict):
                return datetime.date(**value).strftime('%Y-%m-%d')
            elif isinstance(value, str):
                return datetime.datetime.strptime(value, '%Y-%m-%d').strftime('%Y-%m-%d')
        return self.f_type(value)


class IntField(Field):
    def __init__(self, blank=False, dbtype="INT", required=False, default=None):
        super().__init__(int, blank, dbtype, required, default)


class StringField(Field):
    def __init__(self, blank=False, dbtype="VARCHAR(255)", required=False, default=None):
        super().__init__(str, blank, dbtype, required, default)


class DateField(Field):
    def __init__(self, blank=False, dbtype="DATE", required=False, default=None):
        super().__init__(datetime.date, blank, dbtype, required, default)


class FloatField(Field):
    def __init__(self, blank=False, dbtype="FLOAT", required=False, default=None,references=None):
        super().__init__(float, blank, dbtype, required, default)


class BooleanField(Field):
    def __init__(self, blank=False, dbtype="BOOL", required=False, default=None):
        super().__init__(bool, blank, dbtype, required, default)

class ForeignKey(Field):
    def __init__(self, blank=False,dbtype="INT",required=False, default=None,references=None):
        self.references=references
        super().__init__(int, blank,dbtype,required, default)