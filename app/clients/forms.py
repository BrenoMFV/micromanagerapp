from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (PasswordField, SelectField, StringField, SubmitField,
                     TextAreaField)
from wtforms.fields.html5 import TelField
from wtforms.validators import Regexp, Optional, DataRequired, Email, EqualTo, Length
from wtforms_sqlalchemy.fields import QuerySelectField

from ..helpers import COMMON_REGEX
from .. import db
from ..models import ClientCategory

brazilian_states = [('AC', 'Acre'),
                    ('AL', 'Alagoas'),
                    ('AP', 'Amapá'),
                    ('AM', 'Amazonas'),
                    ('BA', 'Bahia'),
                    ('CE', 'Ceará'),
                    ('DF', 'Distrito Federal'),
                    ('ES', 'Espírito Santo'),
                    ('GO', 'Goiás'),
                    ('MA', 'Maranhão'),
                    ('MT', 'Mato Grosso'),
                    ('MS', 'Mato Grosso do Sul'),
                    ('MG', 'Minas Gerais'),
                    ('PA', 'Pará'),
                    ('PB', 'Paraíba'),
                    ('PR', 'Paraná'),
                    ('PE', 'Pernambuco'),
                    ('PI', 'Piauí'),
                    ('RJ', 'Rio de Janeiro'),
                    ('RN', 'Rio Grande do Norte'),
                    ('RS', 'Rio Grande do Sul'),
                    ('RO', 'Rondônia'),
                    ('RR', 'Roraima'),
                    ('SC', 'Santa Catarina'),
                    ('SP', 'São Paulo'),
                    ('SE', 'Sergipe'),
                    ('TO', 'Tocantins')]


def get_client_category():
    return ClientCategory.query.options(db.load_only('category_id', 'category_name')).filter_by(user_id_fk=current_user.user_id)


class EditCategoryForm(FlaskForm):
    old_category = QuerySelectField("Selecione uma Categoria",
                                    query_factory=get_client_category,
                                    get_label="category_name")
    new_category = StringField("Nova Categoria", validators=[DataRequired()])
    submit = SubmitField("Editar")


class RegisterClientForm(FlaskForm):
    name = StringField("Nome", validators=[DataRequired(message="O cliente deve possuir ao menos o nome."),
                                           Regexp(COMMON_REGEX, 0,
                                           message='O nome do cliente deve possuir apenas letras, dígitos, espaços e hífens.')])

    email = StringField(
        "E-mail", validators=[Optional(), Email(message="Endereço de email inválido.")])
    ddd = StringField("DDD", validators=[Optional(), Length(
        min=4, message='DDD incorreto'), Regexp(r"^\(\d{2}\)*$", 0, message="Telefone e DDD recebem apenas dígitos.")])
    phonenumber = TelField("Número", validators=[Optional(), Length(
        min=10, max=10, message='9 dígitos, apenas números.'), Regexp(r"^(\d{5}\-\d{4})*$", 0, message="Telefone e DDD recebem apenas dígitos.")])
    category_name = QuerySelectField("Categoria do Cliente",
                                     query_factory=get_client_category,
                                     get_label='category_name')
    address = StringField("Endereço", validators=[Optional()])
    city = StringField("Cidade", validators=[Optional()])
    observations = StringField("Complemento", validators=[Optional()])
    state = SelectField("Estado", choices=brazilian_states)
    cpf = StringField("CPF", validators=[Optional()])
    cnpj = StringField("CNPJ", validators=[Optional()])
    submit = SubmitField("Confirmar")


class RegisterClientCategoryForm(FlaskForm):
    category_name = StringField("Nova Categoria de Cliente", validators=[DataRequired(),
                                                                         Length(
                                                                             max=32, message="A Categoria de Cliente pode ter no máximo 32 caractéres."),
                                                                         Regexp(COMMON_REGEX, 0,
                                                                                message='Categorias de clientes podem possuir apenas letras e dígitos.')])
    submit = SubmitField("Cadastrar Novo Tipo")
