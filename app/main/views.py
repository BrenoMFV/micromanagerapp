from flask import Flask, current_app, flash, redirect, render_template, session, url_for
from flask_login import current_user, login_required
from flask_sqlalchemy import get_debug_queries
from markupsafe import Markup
from datetime import date, timedelta
import pprint

from .. import db
from ..auth.forms import LoginForm, PasswordResetStep1Form, RegisterUserForm
from ..models import Client, Product, User, Production, Sale, Unit, units_default
from . import main
from ..helpers import get_current_monday, get_week_days


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

        data = dict()
        # get current amount of clients registered
        data['client_count'] = Client.query.options(db.load_only('name')).filter_by(
            user_id_fk=current_user.get_id()).count()

        # last production registered
        data['last_production'] = Production.query.join(Product, Product.product_id == Production.product_id_fk) \
            .add_columns(
            Production.production_date,
            Product.product_name,
            Production.amount_produced
        ) \
            .filter(Production.user_id_fk == current_user.user_id) \
            .order_by(Production.production_date.asc()).first()

        # counting products registered
        data['product_count'] = Product.query.options(db.load_only('product_id')).filter_by(
            user_id_fk=current_user.user_id).count()

        # sends an alert if a product stock is lower than it should be 
        data['stock_alert_count'] = 0
        if data['product_count'] > 0:
            for product in Product.query.options(db.load_only('amount', 'stock_alert')).filter_by(
                    user_id_fk=current_user.user_id).all():
                if product.amount <= product.stock_alert:
                    data['stock_alert_count'] += 1

        # last sale made
        data['last_sales'] = Sale.query.join(Client, Sale.client_id_fk == Client.client_id) \
            .add_columns(
            Sale.sale_id,
            Client.name,
            Sale.total_value,
            Sale.date,
            Sale.delivery_date,

        ) \
            .filter(db.and_(Sale.user_id_fk == current_user.user_id,
                            Sale.date >= (datetime.date.today() - datetime.timedelta(15)))) \
            .limit(10) \
            .order_by(Sale.date.desc())

        # next delivery to be made
        data['next_delivery'] = Sale.query.join(Client, Sale.client_id_fk == Client.client_id) \
            .add_columns(
            Client.name,
            Sale.total_value,
            Sale.sale_id,
            Sale.delivery_date
        ) \
            .filter(Sale.user_id_fk == current_user.user_id, Sale.delivery_date >= date.today()) \
            .order_by(Sale.delivery_date.desc()).first()
        data['next_delivery_count'] = 0
        if data['next_delivery'] is not None:
            data['next_delivery_count'] = Sale.query.filter_by(
                delivery_date=data['next_delivery'].delivery_date).count()

        data['periodic_income'] = dict()
        periodic_income_today = [sale.total_value for sale in
                                 Sale.query.filter(Sale.date >= (date.today() - timedelta(7))).all()]
        data['periodic_income']['today'] = sum(periodic_income_today)
        periodic_income_week = [sale.total_value for sale in
                                Sale.query.filter(Sale.date >= (date.today() - timedelta(weeks=1))).all()]
        data['periodic_income']['week'] = sum(periodic_income_week)
        periodic_income_month = [sale.total_value for sale in
                                 Sale.query.filter(Sale.date >= (date.today() - timedelta(30))).all()]
        data['periodic_income']['month'] = sum(periodic_income_month)

        # count of sales made by day
        # this data is stored in a list of tuples
        # so it will be [(MONDAY, value), (TUESDAY, value)...], being the day of the week an integer
        data['sales_per_day'] = dict()

        weekdays = get_week_days()

        # iterates over each day of 
        # the week starting by monday, thus the reverse range() use
        today = date.weekday(date.today())
        for day in range(today, -1, -1):

            # gets the monday's date
            date_query = date.today() - timedelta(day)
            query = Sale.query.filter_by(user_id_fk=current_user.user_id, date=date_query)

            # gets the total value sold that day
            total_daily_income_value = list()
            if query.count():
                total_daily_income_value = [sale.total_value for sale in query.all()]

            # uṕdate the value in the already made list
            data['sales_per_day'][weekdays[day]] = (query.count(), sum(total_daily_income_value))

        pprint.pprint(data)
        return render_template('index.html',
                               data=data,
                               weekdays=weekdays
                               )
    return render_template('index.html')

#  {'client_count': 1,
#  'last_production': None,
#  'last_sale': (<Sale 2>, 'fdf', 1000.0, 2, datetime.date(2021, 7, 19)),
#  'next_delivery': None,
#  'next_delivery_count': 0,
#  'periodic_income': {'month': 1225.0, 
#                      'today': 1000.0, 
#                      'week': 1000.0},
#  'product_count': 1,
#  'sales_per_day': [
#                    {'19-07-2021': (1, 1000.0)}, 
#                    {'20-07-2021': (0, 0)}
#                   ],
#  'stock_alert_count': 1}
