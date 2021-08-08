import pdfkit
from flask import (flash, jsonify, make_response, redirect, render_template,
                   request, session, url_for)
from flask_login import current_user, login_required
from markupsafe import Markup

from .. import db
from ..models import (Client, Address, Sale, PartialSale,
                      Price, Product, Production, User, Utilities)
from . import sales
from .forms import RegisterSaleForm, PdfForm


@sales.route('/')
@login_required
def main():
    registerSaleForm = RegisterSaleForm()
    pdfForm = PdfForm()
    products = Product.query.options(db.load_only(
        'product_id')).filter_by(user_id_fk=current_user.user_id)
    if products.count() > 1:
        for product in products.all()[1:]:
            registerSaleForm.products.append_entry()
    sales = Sale.query\
        .outerjoin(Client, Sale.client_id_fk == Client.client_id) \
        .add_columns(
        Sale.sale_id,
        Client.name,
        Sale.total_value,
        Sale.date,
        Sale.delivery_date,
    )\
    .filter(Sale.user_id_fk == current_user.user_id).all()

    # creating data in dictionary to store the products sold per sale
    sale_products = dict()

    # parsing all sales registered by the user
    for sale in Sale.query.options(db.load_only('sale_id')).filter_by(user_id_fk=current_user.user_id).all():
        sale_products[sale.sale_id] = list()
        for product in PartialSale.query.options(db.load_only('product_id_fk', 'product_amount', 'price')).filter_by(
                sale_id_fk=sale.sale_id).all():
            product_dict = dict()
            product_dict[product.product_id_fk] = {
                'name': Product.query.options(db.load_only('product_name')).filter_by(
                    product_id=product.product_id_fk).first().product_name,
                'amount': product.product_amount,
                'price': product.price
            }
            sale_products[sale.sale_id].append(
                product_dict[product.product_id_fk])
    return render_template('sales/main.html', sales=sales,
                           registerSaleForm=registerSaleForm,
                           sale_products=sale_products,
                           pdfForm=pdfForm)


@sales.route('/register_sale', methods=['GET', 'POST'])
@login_required
def register_sale():
    form = RegisterSaleForm()

    if form.validate_on_submit():
        total = 0.00

        sale = Sale()

        sale.client_id_fk = form.data['client'].client_id
        sale.date = form.date.data
        sale.delivery_date = form.delivery_date.data if form.delivery_date.data else None

        # total_value is a not nullable field, so I just fill it as 0 at first
        sale.total_value = 0.00
        sale.user_id_fk = current_user.user_id

        Utilities.save(sale)

        partials = list()
        for product in form.products.data:

            # if there is any product
            if product and product['amount'] > 0 and product['price'] > 0:

                current_amount = Product.query.options(db.load_only('amount')).filter_by(
                    product_id=product['product'].product_id).first_or_404()

                partialSale = PartialSale()

                partialSale.sale_id_fk = sale.sale_id
                partialSale.product_id_fk = product['product'].product_id
                partialSale.product_amount = product['amount']
                partialSale.price = product['price']
                partialSale.partial_total = float(
                    product['amount'] * product['price'])
                partialSale.user_id_fk = current_user.user_id

                total += float(partialSale.partial_total)

                if current_amount.amount - float(partialSale.product_amount) < 0:
                    flash(
                        "O seu estoque de {} está baixo."
                            .format(product['product'].product_name))

                current_amount.amount = current_amount.amount - float(partialSale.product_amount)
                partials.append(current_amount)
                partials.append(partialSale)

        try:
            db.session.add_all(partials)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        sale.total_value = total
        if Utilities.save(sale):
            name = Client.query.filter_by(client_id=sale.client_id_fk).first().name
            flash("Venda para {} no valor de {} realizada com sucesso.".format(name, sale.total_value), 'success')
            return redirect(url_for('.main'))
    if form.errors:
        Utilities.flash_error_messages(form)
    return redirect(url_for('.main'))


@sales.route('/get_sale/')
@login_required
def get_sale():
    sale_id = request.args.get('id')
    sale = Sale.query \
        .outerjoin(Client, Sale.client_id_fk == Client.client_id) \
        .outerjoin(PartialSale, PartialSale.sale_id_fk == Sale.sale_id) \
        .add_columns(
        Sale.sale_id,
        Client.client_id,
        Sale.date,
        Sale.delivery_date,
    )\
        .filter(Sale.user_id_fk == current_user.user_id,
                Sale.sale_id == sale_id).first()

    if sale:
        data = dict()
        data['sale_id'] = sale.sale_id
        data['client_id'] = sale.client_id
        data['date'] = sale.date
        data['delivery_date'] = sale.delivery_date
        data['products'] = list()
        for partial in PartialSale.query.filter_by(user_id_fk=current_user.user_id, sale_id_fk=sale.sale_id).all():
            product = {
                'partial_id': partial.partial_sale_id,
                'product_id': partial.product_id_fk,
                'amount': partial.product_amount,
                'price': partial.price,
            }
            data['products'].append(product)
        return jsonify(data), 200
    else:
        return jsonify({'message': 'id não encontrado'}), 404
    return jsonify({'message': 'não foi possível realizar a operação', 'id': sale_id}), 503


@sales.route('/update/', methods=['POST'])
@login_required
def update_sale():
    form = RegisterSaleForm()
    if form.validate_on_submit():
        sale_id = form.sale_id.data

        sale_upt = Sale.query.filter_by(
            user_id_fk=current_user.user_id, sale_id=sale_id)

        if sale_upt.count() == 1:
            sale_total_value = 0.00  # float

            # accessing partial sale for each field
            for product_fields in form.products.data:

                partial_base_obj = PartialSale.query.filter_by(
                    partial_sale_id=product_fields['partial_sale_id'])

                print(partial_base_obj.count(), partial_base_obj.first())

                if product_fields['product'] is None and partial_base_obj.count() == 0:
                    continue

                if partial_base_obj.count() == 0 and \
                        product_fields['product'] is not None and \
                        product_fields['amount'] != 0 and \
                        product_fields['price'] != 0.00:
                    new_partial = PartialSale(
                        product_id_fk=product_fields['product'].product_id,
                        product_amount=product_fields['amount'],
                        price=product_fields['price'],
                        partial_total=float(product_fields['amount'] * product_fields['price']),
                        sale_id_fk=sale_id,
                        user_id_fk=current_user.user_id
                    )
                    # update stock in 'products' table
                    p_current_stock = Product.query.options(db.load_only('amount')).filter_by(
                        product_id=new_partial.product_id_fk).first_or_404().amount

                    Product.query.options(db.load_only('amount')).filter_by(
                        product_id=new_partial.product_id_fk).update({
                        Product.amount: (p_current_stock -
                                         float(new_partial.product_amount))
                    })
                    Utilities.save(new_partial)
                    continue

                partial_query = partial_base_obj.first()

                # if product has been deleted
                if product_fields['product'] is None and partial_base_obj.count() == 1:
                    Utilities.delete(partial_query)
                    continue

                partial_total = (
                        product_fields['amount'] * product_fields['price'])

                sale_total_value += float(partial_total)

                # if there hasn't been any change
                if product_fields['product'].product_id == partial_query.product_id_fk and \
                        product_fields['amount'] == partial_query.product_amount:
                    continue

                # if only the product has been changed, but not the amount
                elif product_fields['product'].product_id != partial_query.product_id_fk and \
                        product_fields['amount'] == partial_query.product_amount:

                    current_product_id = partial_query.product_id_fk
                    new_product_id = product_fields['product'].product_id

                    # correcting the value of the previous product
                    p1_current_stock = Product.query.filter_by(
                        product_id=current_product_id).first().amount
                    Product.query.filter_by(product_id=product_fields['product'].product_id).update({
                        Product.amount: p1_current_stock + partial_query.product_amount
                    })

                    # updating the value of the current product
                    p2_current_stock = Product.query.filter_by(
                        product_id=new_product_id).first().amount
                    Product.query.filter_by(product_id=new_product_id).update({
                        Product.amount: p2_current_stock -
                                        product_fields['amount']
                    })

                    partial_base_obj.update({
                        PartialSale.product_id_fk: product_fields['product'].product_id,
                        PartialSale.price: product_fields['price']
                    })

                    db.session.commit()
                    continue

                # if only the amount has been changed, but not product
                elif product_fields['product'].product_id == partial_query.product_id_fk and \
                        product_fields['amount'] != partial_query.product_amount:

                    p_current_stock = Product.query.filter_by(
                        product_id=partial_query.product_id_fk).first().amount
                    ps_previous_amount = partial_query.product_amount
                    ps_new_amount = product_fields['amount']

                    # updating stock in 'products' table
                    Product.query.filter_by(product_id=product_fields['product'].product_id).update({
                        Product.amount: (p_current_stock -
                                         (ps_new_amount - ps_previous_amount))
                    })

                    # updating 'partial_sales' table
                    partial_base_obj.update({
                        PartialSale.product_amount: ps_new_amount,
                        PartialSale.price: product_fields['price']
                    })

                    db.session.commit()
                    continue

                # if both product and amount has changed
                else:

                    previous_product_id = partial_query.product_id_fk
                    ps_previous_amount = partial_query.product_amount

                    new_product_id = product_fields['product'].product_id
                    ps_new_amount = product_fields['amount']

                    p1_current_stock = Product.query.option(db.load_only('amount')).filter_by(
                        product_id=previous_product_id).first().amount

                    # updating previous product stock in 'products' table
                    Product.query.filter_by(product_id=previous_product_id).update({
                        Product.amount: (
                                p1_current_stock - ps_previous_amount)
                    })

                    p2_current_stock = Product.query.option(db.load_only('amount')).filter_by(
                        product_id=new_product_id).first().amount

                    # updating new product stock in 'products' table
                    Product.query.options(db.load_only('amount')).filter_by(product_id=new_product_id).update({
                        Product.amount: (p2_current_stock - ps_new_amount)
                    })

                    partial_base_obj.update({
                        PartialSale.product_id_fk: new_product_id,
                        PartialSale.product_amount: ps_new_amount,
                        PartialSale.price: product_fields['price']
                    })

                    db.session.commit()

            sale_upt.update({
                Sale.client_id_fk: form.client.data.client_id,
                Sale.date: form.date.data,
                Sale.delivery_date: form.delivery_date.data,
                Sale.total_value: sale_total_value,
            })
            db.session.commit()
            flash(
                'A venda foi atualizada com sucesso.', 'success')
            return redirect(url_for('.main'))
        flash("Não foi possível encontrar essa venda. Por favor, atualize a ṕágina e tente novamente", 'error')
        return redirect(url_for('.main'))
    if form.errors:
        Utilities.flash_error_messages(form)
    return redirect(url_for('.main'))


@sales.route('/generate_pdf/', methods=['GET', 'POST'])
@login_required
def generate_pdf():
    form = PdfForm()
    if not form.validate_on_submit():
        flash('Houve um erro no envio do formulário. Por favor, tente novamente ou entre em contato com o suporte.')
        return redirect(url_for('.main'))

    delivery_date = form.delivery_date.data.delivery_date

    # creating data in dictionary to store the products sold per sale
    sales_delivery = dict()

    # get date from user's input through a form 
    sales = Sale.query.options(db.load_only('sale_id', 'total_value', 'delivery_date')) \
        .filter(Sale.user_id_fk == current_user.user_id,
                Sale.delivery_date == delivery_date)

    # current delivery date
    sales_delivery['delivery_date'] = 'data de entrega'

    # amount of orders to delivery
    sales_delivery['amount_of_orders'] = sales.count()

    sales_delivery['orders'] = dict()

    # dict list of orders
    # parsing all sales registered by the user
    for sale in sales.all():

        sales_delivery['orders'][sale.sale_id] = dict()

        sales_delivery['orders'][sale.sale_id]['sale_info'] = {
            'value': sale.total_value
        }

        # current client information
        current_client = Client.query \
            .join(Sale, Client.client_id == Sale.client_id_fk) \
            .join(Address, Client.client_id == Address.client_id_fk) \
            .add_columns(
            Client.client_id,
            Client.name,
            Client.ddd,
            Client.phonenumber,
            Address.address,
            Address.city,
            Address.state,
            Address.observations) \
            .filter(Client.user_id_fk == current_user.user_id) \
            .first_or_404()

        sales_delivery['orders'][sale.sale_id]['client'] = {
            'name': current_client.name,
            'ddd': current_client.ddd,
            'phonenumber': current_client.phonenumber,
            'address': current_client.address,
            'city': current_client.city,
            'state': current_client.state,
            'observations': current_client.observations,
        }

        sales_delivery['orders'][sale.sale_id]['products'] = list()

#=================================================================#
        # information for each product
        for product in PartialSale.query.options(db.load_only('product_id_fk', 'product_amount', 'price')).filter_by(
                sale_id_fk=sale.sale_id).all():
            product_dict = dict()

            sales_delivery['orders'][sale.sale_id]['products'].append({
                'id': product.product_id_fk,
                'name': Product.query.options(db.load_only('product_name')).filter_by(
                    product_id=product.product_id_fk).first().product_name,
                'amount': product.product_amount,
                'price': product.price
            })

            # current format 
            """ 
            {
                'delivery_date': delivery_date (date),
                'amount_of_orders': amount (float),
                'orders': {
                    sale_id: {
                        sale_infos :{
                            'total_value' : sale_total_value (float)
                        },
                        'client': {
                            'name': name,
                            'ddd': ddd,
                            'phonenumber': phonenumber,
                            'address': address,
                            'city': city,
                            'state': state
                        },
                        'products': [
                            {
                                'id' : id (integer)
                                'name': product_name,
                                'amount': product_amount (float),
                                'price': product_price (float) 
                            },
                            {
                                'id2' : id2 (integer)
                                'name': product_name,
                                'amount': product_amount (float),
                                'price': product_price (float)
                            },
                            ...
                        ],
                    },
                    sale.sale_id2 : {...},
                        ...
                } """

#=================================================================#

    rendered = render_template('pdf_template.html', sales=sales_delivery)
    pdf = pdfkit.from_string(rendered, False)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    # other option: attachment (tries to download)
    response.headers['Content-Disposition'] = 'inline; filename={}_entregas_{}.pdf'.format(current_user.company_name,
                                                                                           sales_delivery['delivery_date'])
    return response


@sales.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_sale(id):
    sale = Sale.query.options(db.load_only('sale_id', 'client_id_fk', 'total_value', 'date')).filter_by(
        sale_id=id, user_id_fk=current_user.user_id).first_or_404()
    name = Client.query.options(db.load_only('name')).filter_by(
        client_id=sale.client_id_fk).first().name
    for ps in sale.partial_sale_rl:
        product = Product.query.options(db.load_only('product_id', 'amount')).filter_by(
            product_id=ps.product_id_fk).first_or_404()
        product.amount = product.amount + ps.product_amount
        db.session.commit()
    if Utilities.delete(sale):
        flash("A venda de {} ({} - {}) foi deletada".format(name, sale.date, sale.total_value))
        return redirect(url_for('.main'))
    return redirect(url_for('.main'))
