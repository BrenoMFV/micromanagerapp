from app.email import send_email
from flask import flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from markupsafe import Markup

from . import account
from .. import db
from ..models import User, Utilities
from ..auth.forms import PasswordResetStep1Form
from .forms import EditUserForm, ChangePasswordForm, ChangeEmailForm, ResendEmailConfirmationForm


@account.route('/', methods=['GET', 'POST'])
@login_required
def user_account():
    passwordResetStep1Form = PasswordResetStep1Form()
    form = EditUserForm()
    resendEmailConfirmationForm = ResendEmailConfirmationForm()
    changePasswordForm = ChangePasswordForm()
    changeEmailForm = ChangeEmailForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.company_name = form.company_name.data
        current_user.cnpj = form.cnpj.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        return redirect(url_for('.user_account'))
    elif form.errors:
        Utilities.flash_error_messages(form)
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name
    form.company_name.data = current_user.company_name
    form.cnpj.data = current_user.cnpj
    return render_template('account/user_info.html', editUserForm=form,
                                                changePasswordForm=changePasswordForm, 
                                                changeEmailForm=changeEmailForm,
                                                resendEmailConfirmationForm=resendEmailConfirmationForm)

@account.route('/change-email/step-1', methods=['POST'])
@login_required
def change_email():
    form = ChangeEmailForm()
    passwordResetStep1Form = PasswordResetStep1Form()
    if form.validate_on_submit():
        new_email = form.new_email.data.lower()
        if User.query.filter(User.email == new_email, User.new_email == new_email, User.user_id != current_user.user_id).scalar():
            flash("Este email já está em uso. Por favor, escolha outro")
            return redirect(url_for('.user_account'))
        if current_user.email == new_email:
            flash("O novo email não pode ser igual ao anterior.")
            return redirect(url_for('.user_account'))
        current_user.new_email = new_email
        db.session.add(current_user)
        db.session.commit()
        token = current_user.generate_confirmation_token(expiration=86400)
        send_email(new_email, "Confirmação de Email",
                   'auth/email/change_email_confirmation', token=token, user=current_user)
        flash("Por favor, acesse o seu email e clique no link para validar o novo email. O link expira em 24 horas.")
        return redirect(url_for('.user_account'))


@account.route('/change-email/step-2/<token>')
@login_required
def change_email_confirmation(token):
    if current_user.confirm(token) and current_user.new_email:
        current_user.email = current_user.new_email
        current_user.new_email = ""
        db.session.add(current_user)
        db.session.commit()
        flash("Seu email foi atualizado com sucesso.")
        return redirect(url_for('.user_account'))
    current_user.new_email = None
    db.session.add(current_user)
    db.session.commit()
    flash("O Token enviado não é válido. Por favor, reinicie o processo")
    redirect(url_for('.user_account'))

@account.route('/resend-email-confirmation', methods=['POST'])
@login_required
def resend_email_confirmation():
    form = ResendEmailConfirmationForm()
    if form.validate_on_submit():
        if current_user.new_email:
            current_user.generate_confirmation_token(expiration=86400)
            send_email(current_user.new_email, "Confirmação de Email",
                        'auth/email/change_email_confirmation', token=token, user=user)
            flash("Um novo email foi enviado para {}. O link expirará em 24 horas".format(current_user.new_email))
        flash("Você ainda não cadastrou nenhum novo email para mudança")