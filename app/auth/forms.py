from flask_wtf import FlaskForm
from wtforms import (BooleanField, PasswordField, SelectField, StringField,
                     SubmitField, TextAreaField)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp

from ..helpers import COMMON_REGEX, CommaDecimalField


login_regex_error_message = "Nome e sobrenome devem conter apenas letras, números e hífens, por favor."


class LoginForm(FlaskForm):
    email = StringField(
        'E-mail', validators=[DataRequired(message="Preencha seu e-mail de acesso"), Email()])
    password = PasswordField('Senha', validators=[
                             DataRequired(message='Registre')])
    remember_me = BooleanField("Mantenha-me logado", default=False)
    submit = SubmitField("Entrar")


class RegisterUserForm(FlaskForm):
    first_name = StringField('Nome', validators=[DataRequired(message="Insira nome e sobrenome"), Regexp(
        COMMON_REGEX, 0, message=login_regex_error_message)])
    last_name = StringField("Sobrenome", validators=[DataRequired(message="Insira nome e sobrenome"), Regexp(
        COMMON_REGEX, 0, message=login_regex_error_message)])
    email = StringField('E-mail', validators=[DataRequired(
        message="Insira seu e-mail"), Email(message="Esse não é um e-mail válido!")])
    company_name = StringField('Nome da empresa', validators=[
                               DataRequired(message="Insira o nome da sua empresa."), Length(1, 24)])
    password = PasswordField('Senha', validators=[
                             DataRequired(), Length(min=8, message="Sua senha deve ter no mínimo 8 caractéres"),
                             EqualTo('confirm', message="As senhas inseridas não são correspondentes")])
    confirm = PasswordField('Confirme a senha')
    submit = SubmitField("Registrar")


class PasswordResetStep1Form(FlaskForm):
    email = StringField("Seu email cadastrado", validators=[DataRequired(), Email("Por favor, insira um email válido")])
    submit = SubmitField("Iniciar Recuperação de Senha")


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('Nova senha', validators=[
                             Length(min=8, message="Sua senha deve ter no mínimo 8 caractéres"),
                             EqualTo('confirm', message="As senhas inseridas não são correspondentes"), DataRequired()])
    confirm = PasswordField("Digite novamente")
    submit = SubmitField("Salvar")

