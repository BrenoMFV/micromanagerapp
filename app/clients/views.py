from app.email import send_email
from flask import flash, redirect, render_template, request, session, url_for, jsonify
from flask_login import current_user, login_required
from markupsafe import Markup

from .. import db
from ..models import Client, ClientCategory, Address, Utilities
from . import clients
from .forms import RegisterClientCategoryForm, RegisterClientForm, EditCategoryForm


@clients.route('/')
@login_required
def main():
    editCategoryForm = EditCategoryForm()
    registerClientForm = RegisterClientForm()
    registerClientCategoryForm = RegisterClientCategoryForm()

    if ClientCategory.query.options(db.load_only('category_id')).filter_by(user_id_fk=current_user.user_id).count() == 0:
        default = ClientCategory(
            category_name='Sem Categoria', user_id_fk=current_user.user_id)
        Utilities.save(default)

    clients = Client.query\
        .join(ClientCategory,
              Client.category_id_fk == ClientCategory.category_id)\
        .join(Address,
              Client.client_id == Address.client_id_fk)\
        .add_columns(
            Client.client_id,
            Client.name,
            Client.ddd,
            Client.phonenumber,
            Client.email,
            ClientCategory.category_name,
            Address.address,
            Address.city,
            Address.state,
            Address.observations,
        )\
        .filter(Client.user_id_fk == current_user.user_id)

    return render_template('clients/main.html',
                           registerClientForm=registerClientForm,
                           registerClientCategoryForm=registerClientCategoryForm,
                           editCategoryForm=editCategoryForm,
                           clients=clients)


@clients.route('/profile/')
@login_required
def client_profile():
    if client_id := request.args.get('id'):

        client = Client.query\
            .join(ClientCategory, Client.category_id_fk == ClientCategory.category_id)\
            .join(Address, Client.client_id == Address.client_id_fk)\
            .add_columns(
                Client.client_id,
                Client.name,
                Client.ddd,
                Client.phonenumber,
                Client.email,
                ClientCategory.category_id,
                ClientCategory.category_name,
                Address.address,
                Address.city,
                Address.state,
                Address.observations,
                Client.cpf,
                Client.cnpj,
                Client.added,
            )\
            .filter(Client.user_id_fk == current_user.user_id, Client.client_id == client_id)\
            .one_or_none()

        if not client:
            return jsonify({'message': 'client not found.'}), 404

        client_data = {
            'id': client.client_id,
            'name': client.name,
            'ddd': client.ddd,
            'phonenumber': client.phonenumber,
            'email': client.email,
            'category_id': client.category_id,
            'category': client.category_name,
            'address': client.address,
            'city': client.city,
            'state': client.state,
            'observations': client.observations,
            'cpf': client.cpf,
            'cnpj': client.cnpj,
            'added': client.added,
        }
        return jsonify(client_data), 200
    return jsonify({'message': 'not usable data'}), 400


@clients.route('/register/', methods=['POST'])
@login_required
def register_client():
    form = RegisterClientForm()
    if form.validate_on_submit():
        new_client = Client(name=form.name.data,
                            email=form.email.data.lower(),
                            ddd=form.ddd.data,
                            phonenumber=form.phonenumber.data,
                            category_id_fk=form.category_name.data.category_id,
                            cpf=form.cpf.data,
                            cnpj=form.cnpj.data,
                            user_id_fk=current_user.user_id
                            )
        
        Utilities.save(new_client)

        client_address = Address(client_id_fk=new_client.client_id,
                                 address=form.address.data,
                                 city=form.city.data,
                                 state=form.state.data,
                                 observations=form.observations.data)
        if not Utilities.save(client_address):
            flash("Não foi possível concluir a operação")
            return redirect(url_for('.main'))
        flash("{} foi adicionado(a) com sucesso.".format(new_client.name))
        return redirect(url_for('.main'))
    if form.errors:
        Utilities.flash_error_messages(form)
    return redirect(url_for('.main'))


@clients.route('/register_category', methods=['POST'])
@login_required
def register_client_category():
    form = RegisterClientCategoryForm()
    if form.validate_on_submit():
        c_category = form.category_name.data
        new_category = ClientCategory(category_name=c_category,
                                      user_id_fk=current_user.user_id)
        if Utilities.save(new_category):
            flash("Nova categoria de cliente: {}".format(c_category), "success")
            return redirect(url_for('.main'))
    if form.errors:
        Utilities.flash_error_messages(form)
    return redirect(url_for('.main'))


@clients.route('/edit_category/', methods=['POST'])
@login_required
def edit_client_category():
    form = EditCategoryForm()
    if form.validate_on_submit():
        id = form.old_category.data.category_id
        old_name = form.old_category.data.category_name
        new_name = form.new_category.data
        if exists := ClientCategory.query.filter_by(user_id_fk=current_user.user_id, category_name=new_name).one_or_none():
            flash(f"A categoria {new_name} já está cadastrada")
            return redirect(url_for('.main'))
        category_upt = ClientCategory.query.filter_by(
            user_id_fk=current_user.user_id, category_id=id)
        if category_upt.count() == 1:
            category_upt.update({
                ClientCategory.category_name: new_name
            })
            db.session.commit()
            flash(f"A categoria {old_name} foi atualizada para {new_name}")
            return redirect(url_for('.main'))
        flash(f"Não foi possível editar a categoria {old_name}")
        return redirect(url_for('.main'))
    if form.errors:
        Utilities.flash_error_messages(form)
    return redirect(url_for('.main'))


@clients.route('/update/', methods=['POST'])
@login_required
def update_client():
    form = RegisterClientForm()
    if form.validate_on_submit():
        client_id = request.form.get('id')
        client_upt = Client.query.filter_by(
            client_id=client_id, user_id_fk=current_user.user_id)
        if client_upt.count() == 1:
            # update clients table
            client_upt.update({
                Client.name: form.name.data,
                Client.email: form.email.data.lower(),
                Client.ddd: form.ddd.data,
                Client.phonenumber: form.phonenumber.data,
                Client.category_id_fk: form.category_name.data.category_id,
                Client.cpf: form.cpf.data,
                Client.cnpj: form.cnpj.data,
                Client.user_id_fk: current_user.user_id
            })

            # update addresses table
            Address.query.filter_by(client_id_fk=client_id).update({
                Address.address: form.address.data,
                Address.city: form.city.data,
                Address.state: form.state.data,
                Address.observations: form.observations.data
            })

            try:
                db.session.commit()
            except Exception as e:
                flash("Erro")
                return redirect(url_for('.main'))

            flash("O cliente {} foi atualizado com sucesso!".format(form.name.data))
            return redirect(url_for('.main'))

        # if there is no client to be found
        flash("Não foi possível encontrar o seu cliente (ID: {}).".format(client_id))
        return redirect(url_for('.main'))
    # if there is any error in the forms
    if form.errors:
        Utilities.flash_error_messages(form)
    return redirect(url_for('.main'))


@clients.route('/delete/<int:client_id>')
@login_required
def delete(client_id):
    client = Client.query.filter_by(
        client_id=client_id, user_id_fk=current_user.user_id).first_or_404()

    if not client.deleted:
        client.deleted = True
        db.session.commit()
        flash("{} excluído com sucesso.".format(client.name))
        return redirect(url_for('.main'))

    flash("O cadastro do cliente {} já foi deletado.".format(client.name))
    return redirect(url_for(".main"))


@clients.route('/statistics')
@login_required
def statistics():
    """ dashboard with all client data """
    return '<h1>TO DO</h1>'
