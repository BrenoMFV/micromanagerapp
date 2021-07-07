from datetime import datetime, date, timedelta
import re

from flask_sqlalchemy import BaseQuery, SQLAlchemy
from wtforms import DecimalField
from jinja2 import contextfilter, Template
from markupsafe import Markup
from app import db


COMMON_REGEX_ERROR_MESSAGE = "Apenas números, letras e hífens."
COMMON_REGEX = re.compile('^[A-Za-zà-úÀ-Ú][\\s\\-\\,A-Za-z0-9à-úÀ-Ú]*$')

current_date = date.today()
expiration_default = date.today() + timedelta(days=90)

def date_brz(dt):
    if dt:
        date = dt.strftime('%d-%m-%Y')
        return date
    return None

def phone_number(value:str):
    return f'{value[:5]}-{value[5:]}'

def brl(value):
    a = f"R$ {value:,.2f}"
    b = a.replace(',', 'v')
    c = b.replace('.', ',')
    return c.replace('v', '.') 


class CommaDecimalField(DecimalField):
    def process_formdata(self, valuelist):
        if valuelist:
            valuelist[0] = valuelist[0].replace(",", ".")
        return super(CommaDecimalField, self).process_formdata(valuelist)


# implemeting a query with deleted = true elements out
class QueryWithSoftDelete(BaseQuery): 
    def __new__(cls, *args, **kwargs):
        obj = super(QueryWithSoftDelete, cls).__new__(cls)
        with_deleted = kwargs.pop('_with_deleted', False)
        if len(args) > 0:
            super(QueryWithSoftDelete, obj).__init__(*args, **kwargs)
            return obj.filter_by(deleted=False) if not with_deleted else obj
        return obj

    def __init__(self, *args, **kwargs):
        pass

    def with_deleted(self):
        return self.__class__(db.class_mapper(self._mapper_zero().class_),
                              session=db.session(), _with_deleted=True)


# customizing a type of column to strip every data stored
class StrippedString(db.TypeDecorator):
    impl = db.String

    def process_bind_param(self, value, dialect):
        # In case there are nullable string fields
        return value.strip() if value else value

    def copy(self, **kw):
        return StrippedString(self.impl.length)
