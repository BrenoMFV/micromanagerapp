from flask import Flask, current_app, flash, redirect, render_template, session, url_for
from flask_login import current_user, login_required
from flask_sqlalchemy import get_debug_queries
from markupsafe import Markup
from datetime import date, timedelta

from .. import db
from ..auth.forms import LoginForm, PasswordResetStep1Form, RegisterUserForm
from ..models import Client, Product, User, Production, Sale, Unit, units_default
from . import main



# @main.after_app_request
# def after_request(response):
#     for query in get_debug_queries():
#         print("{}".format(query.duration))
#         if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
#             current_app.logger.warning(
#                 'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n' %
#                 (query.statement, query.parameters, query.duration, query.context))
#     return response


@main.route('/')
def index():
    loginForm = LoginForm()
    passwordResetStep1Form = PasswordResetStep1Form()
    if current_user.is_authenticated:
        client_count = Client.query.options(db.load_only('name')).filter_by(
            user_id_fk=current_user.get_id()).count()
        last_production = Production.query.join(Product, Product.product_id == Production.product_id_fk)\
                                    .add_columns(
                                        Production.production_date,
                                        Product.product_name,
                                        Production.amount_produced
        )\
            .filter(Production.user_id_fk == current_user.user_id)\
            .order_by(Production.production_date.asc()).first()
        product_count = Product.query.options(db.load_only('product_id')).filter_by(
            user_id_fk=current_user.user_id).count()
        stock_alert_count = 0
        if product_count > 0:
            for product in Product.query.options(db.load_only('amount', 'stock_alert')).filter_by(user_id_fk=current_user.user_id).all():
                if product.amount <= product.stock_alert:
                    stock_alert_count += 1
        last_sale = Sale.query.join(Client, Sale.client_id_fk == Client.client_id)\
                        .add_columns(
                            Client.name,
                            Sale.total_value,
                            Sale.sale_id,
                            Sale.date
                    )\
                        .filter(Sale.user_id_fk == current_user.user_id)\
                        .order_by(Sale.date.desc()).first()
        next_delivery = Sale.query.join(Client, Sale.client_id_fk == Client.client_id)\
            .add_columns(
            Client.name,
            Sale.total_value,
            Sale.sale_id,
            Sale.delivery_date
        )\
            .filter(Sale.user_id_fk == current_user.user_id, Sale.delivery_date >= date.today())\
            .order_by(Sale.delivery_date.desc()).first()

        next_delivery_count = 0
        if next_delivery is not None:
            next_delivery_count = Sale.query.filter_by(
                delivery_date=next_delivery.delivery_date).count()

        income = dict()
        income_today = [ sale.total_value for sale.total_value in Sale.query.filter(Sale.date >= (date.today() - timedelta(7))).all()]
        income['today'] = sum(income_today)  
        income_week =  [ sale.total_value for sale.total_value in Sale.query.filter(Sale.date >= (date.today() - timedelta(weeks=1))).all()]
        income['week'] = sum(income_week)
        income_month = [ sale.total_value for sale.total_value in Sale.query.filter(Sale.date >= (date.today() - timedelta(30))).all() ]
        income['month'] = sum(income_month)

        return render_template('index.html', client_count=client_count,
                               last_production=last_production,
                               product_count=product_count,
                               stock_alert_count=stock_alert_count,
                               last_sale=last_sale,
                               next_delivery=next_delivery,
                               next_delivery_count=next_delivery_count,
                               income=income,
                               )
    return render_template('index.html')

