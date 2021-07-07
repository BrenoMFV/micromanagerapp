from app.email import send_email
from flask import flash, redirect, get_flashed_messages, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from markupsafe import Markup
from time import sleep

from .. import db
from ..models import User, Unit
from . import auth
from .forms import PasswordResetStep1Form, LoginForm, RegisterUserForm, ResetPasswordForm, PasswordResetStep1Form
from ..account.forms import ChangePasswordForm

UNCONFIRMED_EMAIL_MESSAGE = "Você cadastrou um novo email que ainda não foi confirmado. Por favor, confirme o email"


@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint \
            and request.blueprint != 'auth'\
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.before_app_request
def new_unconfirmed_email():
    if current_user.is_authenticated:
        if current_user.new_email:
            if UNCONFIRMED_EMAIL_MESSAGE not in get_flashed_messages():
                flash(UNCONFIRMED_EMAIL_MESSAGE)
                return
            return 
        return


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    loginForm = LoginForm()
    passwordResetStep1Form = PasswordResetStep1Form()
    if loginForm.validate_on_submit():
        user = User.query.filter_by(email=loginForm.email.data.lower()).first()
        if user is not None and user.verify_password(loginForm.password.data):
            login_user(user, loginForm.remember_me.data)
            flash("Olá, {}!".format(user.first_name), 'success')
            if next := request.args.get('next'):
                return redirect(next)
            return redirect(url_for('main.index'))
        sleep(2)
        flash("Email ou senha incorretos", "danger")
        return redirect(url_for('main.index'))
    for err in loginForm.errors:
        for message in loginForm.errors[err]:
            flash(message)
    return render_template('auth/login.html', loginForm=loginForm, passwordResetStep1Form=passwordResetStep1Form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterUserForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        if db.session.query(User.query.filter(User.email == email).exists()).scalar():
            flash("O email {} já possui cadastro. Por favor, escolha outro.".format(email), 'danger')
            return redirect(url_for('main.index'))
        new_user = User(first_name=form.first_name.data.capitalize(),
                        last_name=form.last_name.data.capitalize(),
                        password=form.password.data,
                        email=email,
                        company_name=form.company_name.data
                        )
        db.session.add(new_user)
        db.session.commit()
        token = new_user.generate_confirmation_token()
        send_email(form.email.data, 'Confirme sua Conta',
                   'auth/email/confirm', token=token, user=new_user)
        flash("Olá, {}! Por favor, \
                     confirme seu e-mail para prosseguir!".format(new_user.first_name),
              'success')
        return redirect(url_for('main.index'))
    for err in form.errors:
        for message in form.errors[err]:
            flash(message)
    return redirect(url_for('main.index'))


@auth.route('/confirm/<token>', methods=['GET', 'POST'])
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        register_user_units()
        db.session.commit()
        flash('Você confirmou sua conta com sucesso. Já pode acessar todos os nossos recursos disponíveis. Muito obrigado!', 'success')
    else:
        flash('O link de confirmação é inválido ou expirou.', 'danger')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirme sua Conta',
               'auth/email/confirm', token=token, user=current_user)
    flash('Um novo email de confirmação foi enviado para você.')
    return redirect(url_for('main.index'))


@auth.route('/pass/change', methods=['POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.current_password.data):
            current_user.password = form.new_password.data
            try:
                db.session.add(current_user)
                db.session.commit()
            except Exception as e:
                print(e.with_traceback())
                db.session.rollback()
                return redirect(url_for('account.user_account'))
            flash("Senha alterada com sucesso.")
            return redirect(url_for('account.user_account'))
        flash('Senha incorreta. Tente novamente.')
        return redirect(url_for('account.user_account'))
    for err in form.errors:
        for message in form.errors[err]:
            flash(message)
    return redirect(url_for('account.user_account'))


# reseting password process
@auth.route('/reset/step-1', methods=['POST'])
def reset_password_email():
    if not current_user.is_anonymous: 
        return redirect(url_for('main.index'))
    form = PasswordResetStep1Form()
    if form.validate_on_submit():
        email = form.email.data.lower()
        if not db.session.query(User.query.filter(User.email == email).exists()).scalar():
            flash("O email solicitado não está cadastrado no nosso sistema.")
            return redirect(url_for('main.index'))
        user = User.query.filter_by(email=email).first()
        token = user.generate_reset_token()
        send_email(email, 'Confirme sua Conta',
                   'auth/email/reset', token=token, user=current_user)
        flash(Markup("Um email foi enviado para {}. Acesse o link enviado para redefinir sua senha.<br>O link expirará em 1 hora.".format(email)))
        return redirect(url_for('main.index'))


@auth.route('/reset/step-2/<token>', methods=['POST', 'GET'])
def reset_password(token):
    if not current_user.is_anonymous: 
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.new_password.data):
            db.session.commit()
            flash("Sua senha foi modificada com sucesso")
            return redirect(url_for('main.index'))
        else: 
            flash("O token apresentado não existe ou não é mais válido. Por favor, recomece o processo.", 'danger')
            return redirect(url_for('main.index'))
    for message in form.errors.items():
        flash(message)
    return render_template('auth/reset_password.html', resetPasswordForm=form, token=token)
# end


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado.', 'success')
    return redirect(url_for('main.index'))
