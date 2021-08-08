import uuid
from datetime import datetime

from flask import current_app, flash
from flask_login import UserMixin
from flask_login._compat import text_type
from sqlalchemy.dialects.postgresql import UUID
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login_manager
from app.helpers import QueryWithSoftDelete, StrippedString

units_default = ('kg', 'g', 'mg', 'l', 'ml', 'oz', 'unidade', 'pacote')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(StrippedString(32), nullable=False)
    last_name = db.Column(StrippedString(64), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(StrippedString(64), unique=True, nullable=False)
    new_email = db.Column(StrippedString(64))
    company_name = db.Column(StrippedString(24))
    cnpj = db.Column(StrippedString(32))
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed = db.Column(db.Boolean, default=False)

    # relationships with other tables, most all are one-to-many
    clients = db.relationship('Client', back_populates='user')
    clients_categories = db.relationship('ClientCategory', back_populates='user')
    products = db.relationship('Product', back_populates='user')
    stock = db.relationship('Production', backref='user')
    prices = db.relationship('Price', backref='user')
    partial_sales = db.relationship('PartialSale', back_populates="user")
    sales = db.relationship('Sale', back_populates='user')

    # not yet implemented
    # recipes = db.relationship('Recipe', backref='user')
    # recipe_steps = db.relationship('RecipeStep', back_populates='user')
    # ingredients = db.relationship('Ingredient', backref='user')
    # measurements = db.relationship('Measurement', back_populates='user')

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute.")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.user_id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.user_id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        data = {'reset': self.user_id}
        print(data)
        return s.dumps(data).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        db.session.commit()
        return True

    def get_id(self):
        try:
            return text_type(self.user_id)
        except AttributeError:
            raise NotImplementedError('No `user_id` attribute - override `get_id`')

    def __repr__(self):
        return '<User {}>'.format(self.first_name)


class Client(db.Model):
    __tablename__ = 'clients'

    query_class = QueryWithSoftDelete

    client_id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    name = db.Column(StrippedString(32), nullable=False, index=True)
    email = db.Column(StrippedString(64), index=True)
    ddd = db.Column(db.String(4))
    phonenumber = db.Column(db.String(10))
    cpf = db.Column(StrippedString(14))
    cnpj = db.Column(StrippedString(18))
    added = db.Column(db.DateTime, default=datetime.utcnow)
    user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    category_id_fk = db.Column(db.Integer, db.ForeignKey('clients_categories.category_id'))
    user = db.relationship('User', back_populates='clients')
    addresses = db.relationship('Address', backref='client', lazy='dynamic')
    purchases = db.relationship('Sale', backref='client', lazy='dynamic')

    deleted = db.Column(db.Boolean(), default=False)

    def __repr__(self):
        return '<{}:{}>'.format(self.__class__.__name__, self.name)


class Address(db.Model):
    __tablename__ = 'addresses'

    address_id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(1024))
    city = db.Column(db.String(32))
    state = db.Column(db.String(2))
    observations = db.Column(db.String(128))
    client_id_fk = db.Column(UUID(as_uuid=True), db.ForeignKey('clients.client_id'))
    user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __repr__(self):
        return '<Address: {}>'.format(self.address_id)


class ClientCategory(db.Model):
    __tablename__ = 'clients_categories'

    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(32), nullable=False, index=True)
    clients = db.relationship("Client", backref='category')
    products_prices = db.relationship('Price', backref='category')
    user = db.relationship('User', back_populates='clients_categories')
    user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __repr__(self):
        return '<Categoria de Cliente {}>'.format(self.category_name)


class Product(db.Model):
    __tablename__ = 'products'

    query_class = QueryWithSoftDelete

    product_id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    product_name = db.Column(StrippedString(64), nullable=False, index=True)
    product_category_fk = db.Column(db.Integer, db.ForeignKey('products_categories.category_id'), nullable=False)
    amount = db.Column(db.Float(precision=2), nullable=False, default=0.00)
    stock_alert = db.Column(db.Float(precision=2), default=0.00)
    unit_id_fk = db.Column(db.Integer, db.ForeignKey('units.unit_id'))
    productions = db.relationship('Production', back_populates="product")
    prices = db.relationship('Price', back_populates='product')
    partial_sales = db.relationship('PartialSale', back_populates='product')
    # recipes = db.relationship('Recipe', back_populates='product')
    user = db.relationship("User", back_populates='products')
    user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    deleted = db.Column(db.Boolean(), default=False)

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.product_id)


class Price(db.Model):
    __tablename__ = 'prices'

    price_id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float(precision=2), nullable=False)
    product_id_fk = db.Column(UUID(as_uuid=True), db.ForeignKey('products.product_id'))
    category_id_fk = db.Column(db.Integer, db.ForeignKey('clients_categories.category_id'))
    product = db.relationship('Product', back_populates='prices')
    user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __repr__(self):
        return '<{} R$ {}>' \
            .format(self.product_id_fk.product_name,
                    self.category_id_fk,
                    self.price)


class Unit(db.Model):
    __tablename__ = 'units'

    unit_id = db.Column(db.Integer, primary_key=True)
    unit = db.Column(db.String)
    product = db.relationship('Product', backref='unit')
    user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __repr__(self):
        return '<{}>'.format(self.unit)


class ProductCategory(db.Model):
    __tablename__ = 'products_categories'

    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String, nullable=False)
    products = db.relationship('Product', backref='category')
    user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __repr__(self):
        return '<category {}>'.format(self.category_name)


class Production(db.Model):
    __tablename__ = 'productions'

    production_id = db.Column(db.Integer, primary_key=True)
    product_id_fk = db.Column(UUID(as_uuid=True), db.ForeignKey('products.product_id'), index=True)
    amount_produced = db.Column(db.Integer, nullable=False)
    production_date = db.Column(db.Date, nullable=False)
    expiration_date = db.Column(db.Date)
    product = db.relationship('Product', back_populates='productions')
    _batch = db.Column(db.String())
    user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    @property
    def batch(self):
        return self._batch

    @batch.setter
    def batch(self, product_id):
        product_id = str("00" + product_id) if product_id < 100 else str("0" + product_id)
        week = str(datetime.date(datetime.today()).isocalendar()[1])
        year = str(datetime.date(datetime.today()).isocalendar()[0])[2:]
        second = datetime.time(datetime.now()).strftime("%S")
        self._batch = f'{product_id}{week}{year}{second}'

    def __repr__(self):
        return '<{} of {} in the day {}>'.format(
            self.amount_produced,
            self.product_id_fk,
            self.production_date.strftime('%d:%m:%Y')
        )


# class Supplier(db.Model):
#     __tablename__ = 'suppliers'
#
#     supplier_id = db.Column(db.Integer, primary_key=True)
#     supplier_name = db.Column(StrippedString(64), nullable=False, index=True)
#     cnpj = db.Column(db.String(18))
#     user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'), index=True)
#
#     def __repr__(self):
#         return '<Fornecedor: {}>'.format(self.company)
#

# class Payment(db.Model):
#     __tablename__ = 'payments'
#     # ????
#     payment_id = db.Column(db.Integer, primary_key=True)
#     value = db.Column(db.Float(precision=2), nullable=False, index=True)
#     date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
#
#     user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))
#
#     def __repr__(self):
#         return '<O pagamento do dia {} foi de R${}.>'.format(self.date, self.value)


class PaymentMethod(db.Model):
    __tablename__ = 'payment_methods'

    method_id = db.Column(db.Integer, primary_key=True)
    method = db.Column(db.String(32))
    payments = db.relationship('Sale', backref='payment_method')

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.method)


class Sale(db.Model):
    __tablename__ = "sales"

    sale_id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    client_id_fk = db.Column(UUID(as_uuid=True), db.ForeignKey('clients.client_id'), index=True)
    total_value = db.Column(db.Float(precision=2), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.today(), index=True)
    delivery_date = db.Column(db.Date)
    due = db.Column(db.Boolean, default=False)
    payment_method_id_fk = db.Column(db.Integer, db.ForeignKey('payment_methods.method_id'))
    partial_sales = db.relationship('PartialSale', backref="sale", cascade="all, delete-orphan")
    user = db.relationship('User', back_populates='sales')
    user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))


class PartialSale(db.Model):
    __tablename__ = "partial_sales"

    partial_sale_id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    product_id_fk = db.Column(UUID(as_uuid=True), db.ForeignKey('products.product_id'), nullable=False)
    product_amount = db.Column(db.Float(precision=2), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    partial_total = db.Column(db.Float(precision=2))
    user = db.relationship('User', back_populates='partial_sales')
    sale_id_fk = db.Column(UUID(as_uuid=True), db.ForeignKey('sales.sale_id'), nullable=False)
    product = db.relationship('Product', back_populates='partial_sales')
    user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    def __repr__(self):
        return '<Partial {} from Sale {}>'.format(
            self.sale_id_fk, self.product_id_fk, self.product_amount)


########### NOT YET IMPLEMENTED #############


# class Recipe(db.Model):
#     __tablename__ = "recipes"
#
#     recipe_id = db.Column(db.Integer, primary_key=True)
#     product_id_fk = db.Column(UUID(as_uuid=True), db.ForeignKey('products.product_id'), index=True)
#     recipe_name = db.Column(db.String(64), nullable=False, index=True)
#     recipe_description = db.Column(db.String)
#     production_time = db.Column(db.Float(precision=2), index=True)
#     recipe_steps = db.relationship('RecipeStep', back_populates='recipe_steps')
#     user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))
#
#     def __repr__(self):
#         return "<{}>".format(self.recipe_name)
#
#
# class RecipeStep(db.Model):
#     __tablename__ = "recipe_steps"
#
#     step_id = db.Column(db.Integer, primary_key=True)
#     recipe_id_fk = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
#     step_number = db.Column(db.Integer, nullable=False)
#     step_description = db.Column(db.String, nullable=False)
#     user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.user_id'))
#     recipe = db.relationship('Recipe', back_populates='recipe')
#
#     def __repr__(self):
#         return "<Step {} from {}>".format(self.step_number, self.recipe)
#
#
# class Ingredient(db.Model):
#     __tablename__ = 'ingredients'
#
#     ingredient_id = db.Column(db.Integer, primary_key=True, index=True)
#     ingredient_name = db.Column(StrippedString(64), nullable=False, index=True)
#     recipe_reference = db.Column(db.Boolean, default=False, nullable=False)
#     user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))
#
#     def __repr__(self):
#         return '<{}: {}>'.format(self.__class__.__name__, self.ingredient_name)
#
#
# class Measurement(db.Model):
#     __tablename__ = 'measurements'
#
#     measurement_id = db.Column(db.Integer, primary_key=True)
#     measurement_name = db.Column(StrippedString, nullable=False, index=True)
#     quantity_measurement = db.relationship('Quantity', backref="ingredient_measurement")
#     user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))
#
#     def __repr__(self):
#         return "<{}: {}>".format(self.__class__.__name__, self.measurement_name)
#
#
# class Quantity(db.Model):
#     __tablename__ = 'quantities'
#
#     quantity_id = db.Column(db.Integer, primary_key=True)
#     ingredient_id_fk = db.Column(db.Integer, db.ForeignKey('ingredients.ingredient_id'))
#     measurement_id_fk = db.Column(db.Integer, db.ForeignKey('measurements.measurement_id'))
#     ingredient_quantity = db.Column(db.Float(precision=2), nullable=False, index=True)
#     production_time = db.Column(db.Float(precision=2), index=True)
#     recipe_id_fk = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
#     user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))
#
#     def __repr__(self):
#         return "<Ingrediente ID: {} | Receita ID: {} | Quantidade: {}>" \
#             .format(self.ingredient_id_fk, self.recipe_id_fk, self.ingredient_quantity)
#


####################################


class Utilities:
    @staticmethod
    def flash_error_messages(form):
        for err in form.errors:
            for message in form.errors[err]:
                flash('{}: {}'.format(err.title(), message), 'danger')

    @staticmethod
    def save(entity):
        try:
            db.session.add(entity)
            db.session.commit()
            return True
        except:
            db.session.rollback()
            raise

    @staticmethod
    def delete(entity):
        try:
            db.session.delete(entity)
            db.session.commit()
            return True
        except:
            db.session.rollback()
            raise
