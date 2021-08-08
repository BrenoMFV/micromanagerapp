from flask import flash, redirect, render_template, request, session, url_for, jsonify
from flask_login import current_user, login_required
from markupsafe import Markup
from datetime import date

from ..helpers import CommaDecimalField
from .. import db
from ..models import (Price, Unit, Product, ProductCategory, ClientCategory, Production,
                      Sale, PartialSale, User, Utilities, units_default)
from . import products
from .forms import (RegisterProductCategoryForm, RegisterProductForm,
                    RegisterProductionForm, EditProductForm, EditProductCategoryForm)


@products.route('/')
@login_required
def main():
    # instanciating forms 
    if not Unit.query.filter_by(user_id_fk=current_user.user_id).count() > 0: 
        for unit in units_default:
            db.session.add(Unit(unit=unit, user_id_fk=current_user.user_id))
        db.session.commit()
    registerProductionForm = RegisterProductionForm()
    registerProductCategoryForm = RegisterProductCategoryForm()
    editProductCategoryForm = EditProductCategoryForm()
    
    # information for main table
    products = Product.query\
        .join(ProductCategory, ProductCategory.category_id == Product.product_category_fk)\
        .filter(Product.user_id_fk == current_user.user_id)\
        .add_columns(
            Product.product_id,
            Product.product_name,
            Product.amount,
            ProductCategory.category_id,
            ProductCategory.category_name,
        )\
        .all()

    # gives me the amount of products already reserved for delivery in the future
    product_reserved = dict()
    for product in products:
        id = product.product_id
        product_amount_query = PartialSale.query.join(Sale, Sale.sale_id == PartialSale.sale_id_fk)\
                        .add_columns(db.func.sum(PartialSale.product_amount))\
                        .filter(PartialSale.user_id_fk == current_user.user_id,
                                Sale.delivery_date >= date.today(),
                                PartialSale.product_id_fk == id)\
                        .group_by(PartialSale.product_id_fk).all()
        product_reserved[id] = product_amount_query[0][1] if product_amount_query else 0
    
    client_categories = ClientCategory.query.filter_by(
        user_id_fk=current_user.user_id)
    cc_fields = list()
    
    for cc in client_categories.all():
        fieldname = 'cprice_' + str(cc.category_id)
        cc_fields.append(fieldname)
        setattr(RegisterProductForm, fieldname, CommaDecimalField(
            'Preço ({})' .format(cc.category_name.lower().title())))
        setattr(EditProductForm, fieldname, CommaDecimalField(
            'Preço ({})' .format(cc.category_name.lower().title())))
    editProductForm = EditProductForm()
    registerProductForm = RegisterProductForm()
    return render_template("products/main.html",
                           products=products,
                           products_reserved=product_reserved,
                           cc_fields=cc_fields,
                           registerProductionForm=registerProductionForm,
                           registerProductForm=registerProductForm,
                           registerProductCategoryForm=registerProductCategoryForm,
                           editProductForm=editProductForm,
                           editProductCategoryForm=editProductCategoryForm)


@products.route('/register', methods=['POST'])
@login_required
def register_product():
    client_categories = ClientCategory.query.filter_by(
        user_id_fk=current_user.user_id)
    cc_fields = list()
    for cc in client_categories.all():
        fieldname = 'cprice_' + str(cc.category_id)
        cc_fields.append(fieldname)
        setattr(RegisterProductForm, fieldname, CommaDecimalField(
            'Preço para ' + cc.category_name.lower().title()))
    form = RegisterProductForm()
    if form.validate_on_submit():
        field_default_ids = ('product_name', 'product_category',
                             'stock_alert', 'unit', 'submit')

        new_product = Product(
            user_id_fk=current_user.user_id,
            product_name=form.product_name.data,
            product_category_fk=form.product_category.data.category_id,
            stock_alert=form.stock_alert.data,
            unit=form.unit.data.unit_id)

        if Utilities.save(new_product):
            flash("{} foi cadastrado com sucesso.".format(
                new_product.product_name))

        for field in form:
            if field.id.split('_')[0] == 'cprice' and field.data:
                category_id = int(field.id.split('_')[1])
                product_prices = Price(
                    user_id_fk=current_user.user_id,
                    category_id_fk=category_id,
                    product_id_fk=new_product.product_id,
                    price=field.data
                )
                if not Utilities.save(product_prices):
                    flash("não foi possível cadastrar o preço para a categoria {}".format(
                        int(field.id.split('_')[1])))
        return redirect(url_for('.main'))
    if form.errors:
        Utilities.flash_error_messages(form)
    return redirect(url_for('.main'))


@products.route('/register/category', methods=['GET', 'POST'])
@login_required
def register_product_category():
    registerProductCategoryForm = RegisterProductCategoryForm()
    if registerProductCategoryForm.validate_on_submit():
        # makes sure it's not a duplicate inside the user's data
        category_check = ProductCategory.query.filter_by(
            category_name=registerProductCategoryForm.category_name.data, user_id_fk=current_user.user_id)
        if category_check.count() == 1:
            flash("Você já possui essa categoria cadastrada.")
            return redirect(url_for('.main'))
        # if unique, instances and saves into db
        new_category = ProductCategory(
            category_name=registerProductCategoryForm.category_name.data,
            user_id_fk=current_user.user_id
        )
        if Utilities.save(new_category):
            flash("Categoria {} criada com sucesso".format(
                new_category.category_name.lower().title()))
            return redirect(url_for('.main'))
        flash("Não foi possível criar a categoria.")
        return redirect(url_for('.main'))
    return redirect(url_for('.main'))


@products.route('product-category/edit', methods=['POST'])
@login_required
def edit_product_category():
    form = EditProductCategoryForm()
    if form.validate_on_submit():
        old_category_name = form.old_category.data.category_name
        product_category_obj = ProductCategory.query.filter(ProductCategory.category_id == form.old_category.data.category_id,
                                                            ProductCategory.user_id_fk == current_user.user_id)
        if product_category_obj.scalar():
            product_category_obj.update({
                ProductCategory.category_name: form.new_category.data
            })
            db.session.commit()
            flash("A categoria {} foi alterada para {}.".format(
                old_category_name, form.new_category.data))
            return redirect(url_for('.main'))
    return redirect(url_for('.main'))


@products.route('/get/')
@login_required
def get_product():
    if product_id := request.args.get('id'):
        product = Product.query.filter_by(
            product_id=product_id, user_id_fk=current_user.user_id).first_or_404()
        product_json = {
            'id': product.product_id,
            'name': product.product_name,
            'category_id': product.product_category_fk,
            'amount': product.amount,
        }
        product_json['prices'] = dict()
        for category in ClientCategory.query.filter_by(user_id_fk=current_user.user_id).all():
            price = Price.query.filter_by(
                product_id_fk=product_id, category_id_fk=category.category_id, user_id_fk=current_user.user_id).first()
            product_json['prices'][category.category_id] = '{:.2f}'.format(
                price.price) if price else 0
        return jsonify(product_json)
    return jsonify({'message': 'invalid request'})


@products.route('/update/', methods=['POST'])
@login_required
def update_product():
    client_categories = ClientCategory.query.filter_by(
        user_id_fk=current_user.user_id)
    cc_fields = list()
    for cc in client_categories.all():
        fieldname = 'cprice_' + str(cc.category_id)
        cc_fields.append(fieldname)
        setattr(EditProductForm, fieldname, CommaDecimalField(
            'Preço para ' + cc.category_name.lower().title()))
    form = EditProductForm()
    if form.validate_on_submit():
        product_id = request.form.get('id')
        product_upt = Product.query.filter_by(
            product_id=product_id,
            user_id_fk=current_user.user_id
        )
        if not product_upt.count() == 1:
            flash("Não foi possível modificar o produto {}.".format(
                form.product_name.data))
            return redirect(url_for('.main'))

        product_upt.update({
            Product.product_name: form.product_name.data,
            Product.amount: form.amount.data,
            Product.product_category_fk: form.product_category.data.category_id,
        })

        db.session.commit()

        for field in form:
            price_field = field.id.split("_")[0] if field.id.split("_")[0] == 'cprice' else None
            if price_field:
                category_id = int(field.id.split('_')[1])
                price_query_obj = Price.query.filter_by(
                    user_id_fk=current_user.user_id, category_id_fk=category_id)
                if not price_query_obj.first():
                    new_price = Price(product_id_fk=product_id, category_id_fk=category_id,
                                      user_id_fk=current_user.user_id, price=field.data)
                    db.session.add(new_price)
                    db.session.commit()
                    continue
                elif price_field and field.data != price_query_obj.first().price:
                    price_query_obj.update({
                        Price.price: field.data
                    })
                    db.session.commit()
            else:
                continue
        return redirect(url_for('.main'))
        flash("As informações de {} foram atualizadas."
              .format(product_upt.first().product_name))
        return redirect(url_for('.main'))
    if form.errors:
        Utilities.flash_error_messages(form)
    return redirect(url_for('.main'))


@products.route('/production/records')
@login_required
def production_record():
    registerProductionForm = RegisterProductionForm()
    productions = Production.query\
        .join(Product, Product.product_id == Production.product_id_fk)\
        .join(ProductCategory, Product.product_category_fk == ProductCategory.category_id)\
        .add_columns(
            Production.production_id,
            Production.product_id_fk,
            Production.amount_produced,
            Production.production_date,
            Production.expiration_date,
            Production._batch,
            Product.product_name,
            ProductCategory.category_name
        )\
        .filter(Production.user_id_fk==current_user.user_id)\
        .order_by(Production.production_date.asc()).all()
    return render_template('products/production_record.html',
                           productions=productions,
                           registerProductionForm=registerProductionForm)


# @products.route('production/delete/<id>', methods=['GET', 'POST'])
# @login_required
# def production_delete(id):
#     production = Production.query.filter_by(
#         production_id=id, user_id_fk=current_user.user_id).first_or_404()
#     product_query_obj = Product.query.filter_by(
#         product_id=production.product_id_fk,  user_id_fk=current_user.user_id)
#     current_amount = product_query_obj.first().amount
#     product_query_obj.update({
#         Product.amount: current_amount - production.amount_produced
#     })
#     try:
#         db.session.delete(production)
#         db.session.commit()
#         flash("A produção foi removida com sucesso")
#         return redirect(url_for('.main'))
#     except Exception:
#         db.session.rollback()
#         raise
#     return redirect(url_for(".production_record"))


@products.route('/production/register', methods=['POST'])
@login_required
def register_production():
    form = RegisterProductionForm()
    if form.validate_on_submit():
        if form.amount_produced.data < 1:
            flash("""A produção deve possuir pelo menos uma unidade do produto
                  para ser cadastrada. Por favor, preencha corretamente o formulário""")
            return redirect(url_for('.main'))
        new_production = Production(
            product_id_fk=form.product.data.product_id,
            amount_produced=form.amount_produced.data,
            production_date=form.production_date.data,
            expiration_date=form.expiration_date.data,
            # the product id is the only param we must pass to generate the batch number
            batch=form.product.data.product_id,
            user_id_fk=current_user.user_id
        )
        if Utilities.save(new_production):
            update_stock = Product.query.options(db.load_only('amount'))\
                .filter_by(
                product_id=new_production.product_id_fk,
                user_id_fk=current_user.user_id)
            # if the product has been really found, update it
            if update_stock.count() == 1:
                update_stock.update({
                    Product.amount: (update_stock.first().amount +
                                     new_production.amount_produced)
                })
                db.session.commit()
                flash("A produção foi atualizada com sucesso!")
            else:
                stock = Production(
                    product_id_fk=new_production.product_id_fk,
                    amount=new_production.amount_produced,
                    user_id_fk=current_user.user_id
                )
                if Utilities.save(stock):
                    flash(
                        f"O seu estoque para o produto {new_production.product_id_fk} foi inaugurado!")
    if form.errors:
        Utilities.flash_error_messages(form)
    return redirect(url_for('.main'))


@products.route('/production/get')
@login_required
def get_production():
    if id := request.args.get('id'):
        production = Production.query\
            .join(Product, Product.product_id == Production.product_id_fk)\
            .join(ProductCategory, Product.product_category_fk == ProductCategory.category_id)\
            .add_columns(
                Production.production_id,
                Production.product_id_fk,
                Production.amount_produced,
                Production.production_date,
                Production.expiration_date,
                Production._batch,
                Product.product_name,
                ProductCategory.category_name
            )\
            .filter(Production.user_id_fk == current_user.user_id,
                    Production.production_id == id).first_or_404()
        production_json = {
            'id': production.production_id,
            'amount_produced': production.amount_produced,
            'production_date': production.production_date,
            'expiration_date': production.expiration_date,
            '_batch': production._batch,
            'product_name': production.product_name,
            'product_id': production.product_id_fk,
        }
        return jsonify(production_json), 200
    flash("Erro! Produção não encontrada!")
    return jsonify({'message': 'id não encontrado'}), 404

@products.route('production/update', methods=['POST'])
@login_required
def update_production():
    form = RegisterProductionForm()
    message = "Produção atualizada com sucesso."
    if form.validate_on_submit():
        production_query_obj = Production.query.filter_by(
            production_id=request.form.get('production_id'))

        if production_query_obj.count() != 1:
            flash(
                """Não foi possível atualizar o produto. 
                Por favor, atualize a paǵina e tente novamente.""")
            return redirect(url_for('.main'))
        production_query = production_query_obj.first()
        if production_query.product_id_fk != form.product.data.product_id\
                and production_query.amount_produced != form.amount_produced.data:

            # update old stock in 'products' table
            old_product = Product.query.filter_by(
                product_id_fk=production_query.product_id_fk)
            previous_amount = old_product.first().amount
            old_product.update({
                Product.amount: previous_amount + (production_query.amount_produced - form.amount_produced.data),
            })

            # update new stock in 'products' table
            next_product = Product.query.filter_by(
                product_id_fk=form.product.data.product_id)
            current_amount = next_product.first().amount_produced
            next_product.update({
                Product.amount: current_amount + form.amount_produced.data
            })
            production_query_obj.update({
                Production.product_id_fk: form.product.data.product_id,
                Production.amount_produced: form.amount_produced.data,
                Production.production_date: form.production_date.data,
                Production.expiration_date: form.expiration_date.data,
            })

            db.session.commit()
            flash(message)

        elif production_query.product_id_fk == form.product.data.product_id\
                and production_query.amount_produced != form.amount_produced.data:

            product = Product.query.filter_by(
                product_id=production_query.product_id_fk)
            current_amount = product.first().amount

            product.update({
                Product.amount: current_amount -
                (production_query.amount_produced - form.amount_produced.data)
            })

            production_query_obj.update({
                Production.product_id_fk: form.product.data.product_id,
                Production.amount_produced: form.amount_produced.data,
                Production.production_date: form.production_date.data,
                Production.expiration_date: form.expiration_date.data,
            })
            db.session.commit()
            flash(message)

        elif production_query.product_id_fk != form.product.data.product_id\
                and production_query.amount_produced == form.amount_produced.data:

            previous_product = Product.query.options(db.load_only('amount'))\
                .filter_by(product_id=production_query.product_id_fk)
            previous_amount = previous_product.first().amount
            previous_product.update({
                Product.amount: previous_amount - production_query.amount_produced
            })

            next_product = Product.query.options(db.load_only('amount'))\
                .filter_by(product_id=form.product.data.product_id)
            previous_amount = next_product.first().amount
            next_product.update({
                Product.amount: previous_amount + production_query.amount_produced
            })

            production_query_obj.update({
                Production.product_id_fk: form.product.data.product_id,
                Production.amount_produced: form.amount_produced.data,
                Production.production_date: form.production_date.data,
                Production.expiration_date: form.expiration_date.data,
            })
            db.session.commit()
            flash(message)
        return redirect(url_for('.production_record'))
    if form.errors:
        Utilities.flash_error_messages(form)
    return redirect(url_for('.production_record'))
