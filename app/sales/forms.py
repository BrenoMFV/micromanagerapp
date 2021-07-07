from datetime import datetime, date
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (DecimalField, IntegerField, SelectField, StringField,
                     SubmitField, TextAreaField,  FieldList, FormField)
from wtforms.fields.html5 import DateField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange, Length, Optional
from wtforms_sqlalchemy.fields import (
    QuerySelectField, QuerySelectMultipleField)

from .. import db
from ..helpers import current_date, CommaDecimalField
from ..models import Client, Product, Sale


def get_clients():
    return Client.query.options(db.load_only('client_id', 'name'))\
        .filter_by(user_id_fk=current_user.user_id).all()


def get_delivery_dates():
    return Sale.query.options(db.load_only('delivery_date'))\
        .filter(Sale.user_id_fk == current_user.user_id, Sale.delivery_date >= current_date)\
        .group_by(Sale.sale_id)\
        .order_by(db.asc(Sale.delivery_date)).all()


def get_products():
    return Product.query.options(db.load_only('product_id', 'product_name'))\
                        .filter_by(user_id_fk=current_user.user_id).all()


class PdfForm(FlaskForm):
    delivery_date = QuerySelectField("Selecione o dia de entrega para gerar o relatório",
                                     query_factory=get_delivery_dates,
                                     get_label='delivery_date')
    accept = SubmitField('Gerar Relatório')


class ProductSaleForm(FlaskForm):
    class Meta:
        csrf = False
    partial_sale_id = IntegerField(default=0)
    product = QuerySelectField("Produto", query_factory=get_products,
                               get_label='product_name',
                               allow_blank=True)
    amount = CommaDecimalField("Quantidade", default=0, validators=[NumberRange(min=0)])
    price = CommaDecimalField("Preço", default=0, validators=[NumberRange(min=0)])


class RegisterSaleForm(FlaskForm):
    sale_id = IntegerField()
    client = QuerySelectField(
        "Cliente", query_factory=get_clients, get_label='name')
    products = FieldList(FormField(ProductSaleForm), min_entries=1)
    date = DateField("Data de lançamento", default=date.today)
    delivery_date = DateField(
        "Dia da entrega (se houver)", validators=[Optional()])
    accept = SubmitField("Registrar Venda")
