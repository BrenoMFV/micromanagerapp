from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (PasswordField, SelectField, StringField, SubmitField,
                     TextAreaField)
from wtforms.fields.html5 import TelField
from wtforms.validators import Regexp, Optional, DataRequired, Email, EqualTo, Length
from wtforms_sqlalchemy.fields import QuerySelectField

from ..helpers import COMMON_REGEX, CommaDecimalField
from .. import db
from ..models import ClientCategory


class EditUserForm(FlaskForm):
    first_name = StringField("Nome", validators=[Regexp(COMMON_REGEX, 0, message='Nome e sobrenome devem conter apenas letras, dígitos e hífens.'), DataRequired(
        message="Nome e sobrenome não podem ficar em branco")])
    last_name = StringField("Sobrenome", validators=[Regexp(COMMON_REGEX, 0, message='Nome e sobrenome devem conter apenas letras, dígitos e hífens.'), DataRequired(
        message="Nome e sobrenome não podem ficar em branco")])
    company_name = StringField("Empresa", validators=[Optional()])
    cnpj = StringField("CNPJ", validators=[Optional()])
    submit = SubmitField("Salvar alterações")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(
        "Senha atual", validators=[DataRequired()])
    new_password = PasswordField('Senha', validators=[
        DataRequired(), Length(min=8, message="Sua senha deve ter no mínimo 8 caractéres"),
        EqualTo('confirm', message="As senhas inseridas não são correspondentes")])
    confirm = PasswordField("Confirmar senha nova",
                            validators=[DataRequired()])
    submit = SubmitField("Salvar alterações")


class ChangeEmailForm(FlaskForm):
    new_email = StringField("Novo email", validators=[
                            DataRequired(), Email(message="Insira um email válido"),
                            Length(max=64, message="Máximo de 64 caractéres para o email")])
    submit = SubmitField("Mudar Email")

class ResendEmailConfirmationForm(FlaskForm):
    class Meta:
        csrf = False 
    submit = SubmitField("Reenviar Email de Confirmação")
