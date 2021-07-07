import datetime

from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (IntegerField, SelectField,
                     StringField, SubmitField, TextAreaField)
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Email, Regexp, EqualTo, Length
from wtforms_sqlalchemy.fields import QuerySelectField


from .. import db
from ..helpers import (current_date, expiration_default, 
                       CommaDecimalField, COMMON_REGEX,)  
from ..models import Product, ProductCategory, Unit


def user_product_categories():
    return ProductCategory.query.filter_by(user_id_fk=current_user.user_id).order_by(ProductCategory.category_id)

def get_units():
    return Unit.query.filter_by(user_id_fk=current_user.user_id)

def user_products():
    return Product.query.filter_by(user_id_fk=current_user.user_id)


class RegisterProductForm(FlaskForm):
    product_name = StringField("Nome do Produto", validators=[DataRequired(message="Deve conter o nome do produto")])
    product_category = QuerySelectField("Categoria do Produto", query_factory=user_product_categories, get_label="category_name")
    stock_alert = CommaDecimalField("Alerta de Estoque Baixo")
    unit = QuerySelectField("Unidade", query_factory=get_units, get_label='unit')
    submit = SubmitField("Salvar")


class EditProductForm(FlaskForm):
    product_name = StringField("Nome do Produto", validators=[DataRequired()])
    product_category = QuerySelectField("Categoria do Produto", query_factory=user_product_categories, get_label="category_name")
    stock_alert = CommaDecimalField("Alerta de Estoque Baixo")
    amount = CommaDecimalField("Em estoque")
    submit = SubmitField("Salvar")


class RegisterProductCategoryForm(FlaskForm):
    category_name = StringField("Categoria de Produtos", validators=[DataRequired()])
    submit = SubmitField("Cadastrar Categoria")


class EditProductCategoryForm(FlaskForm):
    old_category = QuerySelectField("Categoria Antiga", query_factory=user_product_categories, get_label="category_name") 
    new_category = StringField("Nova Categoria", validators=[DataRequired(), Regexp(COMMON_REGEX, 0, "A Categoria pode conter apenas letras, números, hífens.")])
    submit = SubmitField("Salvar alterações")


class RegisterProductionForm(FlaskForm):
    product = QuerySelectField("Produto", query_factory=user_products, get_label='product_name')
    amount_produced = IntegerField("Quantidade", validators=[DataRequired()])
    production_date = DateField("Fabricação")
    expiration_date = DateField("Validade", default=expiration_default)
    submit = SubmitField("Cadastrar Produção")
