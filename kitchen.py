import os

import click
import jinja2
from flask import url_for
from flask_migrate import Migrate, upgrade
from flask_script import Manager
from dotenv import load_dotenv

from app import create_app, db
from app.helpers import brl, phone_number, date_brz
from app.clients.forms import RegisterClientForm
from app.models import (User, Client, ClientCategory, Ingredient, Product, ProductCategory,
                        Production, Sale, Supplier, User, Recipe, RecipeStep,
                        Measurement, Quantity, PartialSale, Address, Unit)

load_dotenv()

config_name = os.getenv('FLASK_CONFIG') or 'default'

app = create_app(config_name)
migrate = Migrate(app, db)

jinja2.filters.FILTERS["PHONE"] = phone_number
jinja2.filters.FILTERS["BRL"] = brl
jinja2.filters.FILTERS['dir'] = dir
jinja2.filters.FILTERS['DATEBR'] = date_brz


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Client=Client, ClientCategory=ClientCategory,
                Ingredient=Ingredient, Product=Product, ProductCategory=ProductCategory,
                Recipe=Recipe, RecipeStep=RecipeStep, Measurement=Measurement, Address=Address,
                Production=Production, Sale=Sale, Supplier=Supplier, PartialSale=PartialSale,
                Unit=Unit
                )


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


@app.cli.command()
@click.argument('test_names', nargs=-1)
def test(test_names):
    """Run the unit tests."""
    import unittest
    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.cli.command()
@click.option('-h', '--host', default='127.0.0.1', help='The interface to bind to.')
@click.option('-p', '--port', default=5000, help='The port to bind to.')
@click.option('--length', default=25, help='Number of functions to include in the profiler report.')
@click.option('--profile-dir', default=None, help='Directory where profiler data files are saved.')
def profile(host, port, length, profile_dir):
    """Start the application under the code profiler."""
    from werkzeug.middleware.profiler import ProfilerMiddleware
    from werkzeug.serving import run_simple
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    run_simple(host, port, app, use_debugger=False)  # use run_simple instead of app.run()


def create_test_account():
    test = User(first_name="Breno",
                last_name="Veríssimo",
                company_name="Admin",
                password=os.environ.get('ADMIN_PASS'),
                email='brenomfv@gmail.com',
                confirmed=True)
    test2 = User(first_name="Conta",
                 last_name="Teste",
                 company_name="Teste",
                 password=os.environ.get('TEST_PASS'),
                 email="teste@gmail.com",
                 confirmed=True)
    db.session.add_all([test, test2])
    try:
        db.session.commit()
        print("{} e {}".format(test.first_name, test2.first_name))
    except:
        raise


@app.cli.command()
def deploy():
    upgrade()
    create_test_account()
