import os

from flask import Flask
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import config

mail = Mail()
migrate = Migrate(compare_type=True)
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    if app.config['SSL_REDIRECT']:
        try:
            from flask_sslify import SSLify
            sslify = SSLify(app)
        except ModuleNotFoundError or ImportError:
            print("Please, install flask-sslify first.")

    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .clients import clients as clients_blueprint
    app.register_blueprint(clients_blueprint, url_prefix='/clients')

    from .sales import sales as sales_blueprint
    app.register_blueprint(sales_blueprint, url_prefix='/sale')

    from .products import products as products_blueprint
    app.register_blueprint(products_blueprint, url_prefix='/products')

    from .account import account as account_blueprint
    app.register_blueprint(account_blueprint, url_prefix='/account')

    return app
