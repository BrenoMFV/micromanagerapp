from datetime import datetime

from flask import current_app, flash
from flask_login import UserMixin, current_user
from flask_login._compat import text_type
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
    first_name = db.Column(StrippedString(32), nullable=False, index=True)
    last_name = db.Column(StrippedString(64), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(StrippedString(64), unique=True, nullable=False)
    new_email = db.Column(StrippedString(64))
    company_name = db.Column(StrippedString(24))
    cnpj = db.Column(StrippedString(32))
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed = db.Column(db.Boolean, default=False)
    permission = db.Column(db.Integer, default=0)
    user_client_rl = db.relationship('Client', backref='user_client')
    user_client_category_rl = db.relationship('ClientCategory', backref='user_client_category')
    user_product_rl = db.relationship('Product', backref='user_products')
    user_ingredient_rl = db.relationship('Ingredient', backref='user_ingredients')
    user_recipe_rl = db.relationship('Recipe', backref='user_recipe')
    user_recipe_step_rl = db.relationship('RecipeStep', backref='user_recipe_step')
    user_measurement_rl = db.relationship('Measurement', backref='user_measurement')
    user_product_stock_rl = db.relationship('Production', backref='user_stock')
    user_prices_rl = db.relationship('Price', backref='user_price')
    user_partial_sale_rl = db.relationship('PartialSale', backref="user_partial_sale")
    user_sale_rl = db.relationship('Sale', backref='user_sale')

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

    client_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(StrippedString(32), nullable=False, index=True)
    email = db.Column(StrippedString(64), index=True)
    ddd = db.Column(db.String(2))
    phonenumber = db.Column(db.String(16))
    cpf = db.Column(StrippedString(14))
    cnpj = db.Column(StrippedString(18))
    added = db.Column(db.DateTime, default=datetime.utcnow)
    deleted = db.Column(db.Boolean(), default=False)
    category_id_fk = db.Column(db.Integer, db.ForeignKey('clients_categories.category_id'))
    client_address = db.relationship('Address', backref='client', lazy='dynamic')
    client_sale_rl = db.relationship('Sale', backref='client_sale', lazy='dynamic')
    user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    

    def __repr__(self):
        return '<Client: {}>'.format(self.name)


class Address(db.Model):
    __tablename__ = 'addresses'

    address_id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(1024))
    city = db.Column(db.String(32))
    state = db.Column(db.String(2))
    observations = db.Column(db.String(128))
    client_id_fk = db.Column(db.Integer, db.ForeignKey('clients.client_id'))
    user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __repr__(self):
        return '<Address: {}>'.format(self.address_id)


class ClientCategory(db.Model):
    __tablename__ = 'clients_categories'

    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(32), nullable=False, index=True)
    category_price_rl = db.relationship('Price', backref='category_id') 
    user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __repr__(self):
        return '<Categoria de Cliente: {}.>'.format(self.category_name)


class Product(db.Model):
    __tablename__ = 'products'

    query_class = QueryWithSoftDelete

    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(StrippedString(64), nullable=False, index=True)
    product_category_fk = db.Column(db.Integer, db.ForeignKey('products_categories.category_id'), nullable=False)
    amount = db.Column(db.Float(precision=2), nullable=False, default=0.00)
    stock_alert = db.Column(db.Float(precision=2), default=0.00)
    unit = db.Column(db.Integer, db.ForeignKey('units.unit_id'))
    deleted = db.Column(db.Boolean(), default=False)
    product_production_rl = db.relationship('Production', backref="product_production")
    product_partial_sale_rl = db.relationship('PartialSale', backref='product_sold')
    product_recipe_rl = db.relationship('Recipe', backref='products_recipe')
    user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.product_id)


class Price(db.Model):
    __tablename__ = 'prices'

    price_id = db.Column(db.Integer, primary_key=True)
    product_id_fk = db.Column(db.Integer, db.ForeignKey('products.product_id'))
    category_id_fk = db.Column(db.Integer, db.ForeignKey('clients_categories.category_id'))
    price = db.Column(db.Float(precision=2), nullable=False)
    user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __repr__(self):
        return '<Product_ID: {}, Clients Category: {} Price: R$ {}>'\
            .format(self.product_id_fk, 
                    self.category_id_fk, 
                    self.price)


class Unit(db.Model):
    __tablename__ = 'units'

    unit_id = db.Column(db.Integer, primary_key=True)
    unit = db.Column(db.String)
    product = db.relationship('Product', backref='product_unit')
    user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __repr__(self):
        return '<{}>'.format(self.unit)


class ProductCategory(db.Model):
    __tablename__ = 'products_categories'

    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String, nullable=False)
    product_category_rl = db.relationship('Product', backref='product_category')
    user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __repr__(self):
        return '<category {}>'.format(self.category_name)


class Supplier(db.Model):
    __tablename__ = 'suppliers'

    supplier_id = db.Column(db.Integer, primary_key=True)
    supplier_name = db.Column(StrippedString(64), nullable=False, index=True)
    cnpj = db.Column(db.String(18))
    user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'), index=True)

    def __repr__(self):
        return '<Fornecedor: {}>'.format(self.company)


class Production(db.Model):
    __tablename__ = 'productions'

    production_id = db.Column(db.Integer, primary_key=True)
    product_id_fk = db.Column(db.Integer, db.ForeignKey('products.product_id'), index=True)
    amount_produced = db.Column(db.Integer, nullable=False)
    production_date = db.Column(db.Date, nullable=False)
    expiration_date = db.Column(db.Date)
    _batch = db.Column(db.String())
    user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    @property
    def batch(self):
        return self._batch

    @batch.setter
    def batch(self, product_id):
        product_id = str(product_id)
        week = str(datetime.date(datetime.today()).isocalendar()[1])
        year = str(datetime.date(datetime.today()).isocalendar()[0])[2:]
        second = datetime.time(datetime.now()).strftime("%S")
        self._batch = "0" + product_id + week + year + second 

    def __repr__(self):
        return '<Product: {} | Amount Produced: {} | Date: {}>'.format(
            self.product_id_fk, 
            self.amount_produced, 
            self.production_date
        )


class Payment(db.Model):
    __tablename__ = 'payments'
    # ????
    payment_id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float(precision=2), nullable = False, index=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __repr__(self):
        return '<O pagamento do dia {} foi de R${}.>'.format(self.date, self.value)


class Sale(db.Model):
    __tablename__ = "sales"

    sale_id = db.Column(db.Integer, primary_key=True)
    client_id_fk = db.Column(db.Integer, db.ForeignKey('clients.client_id'), index=True)
    total_value = db.Column(db.Float(precision=2), nullable = False)
    date = db.Column(db.Date, nullable=False, default=datetime.today(), index=True)
    delivery_date = db.Column(db.Date)
    due = db.Column(db.Boolean, default=False)
    partial_sale_rl = db.relationship('PartialSale', backref="sale_ref", cascade="all, delete-orphan")
    user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    # possible payment method foreignkey here 


class PartialSale(db.Model):
    __tablename__ = "partial_sales"

    partial_sale_id = db.Column(db.Integer, primary_key=True)
    product_id_fk = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    product_amount = db.Column(db.Float(precision=2), nullable=False)
    price = db.Column(db.Float(precision=2), nullable = False)
    partial_total = db.Column(db.Float(precision=2))
    sale_id_fk = db.Column(db.Integer, db.ForeignKey('sales.sale_id'), nullable=False)
    user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    def __repr__(self):
        return '<Sale: {} | Product: {} | Amount: {}>'.format(
            self.sale_id_fk, self.product_id_fk, self.product_amount)


########### NOT YET IMPLEMENTED #############

class Recipe(db.Model):
    __tablename__ = "recipes"
    
    recipe_id = db.Column(db.Integer, primary_key=True)
    product_id_fk = db.Column(db.Integer, db.ForeignKey('products.product_id'), index=True)
    recipe_name = db.Column(db.String(64), nullable=False, index=True)
    recipe_description = db.Column(db.String)
    production_time = db.Column(db.Float(precision=2), index=True)
    recipe_steps_rl = db.relationship('RecipeStep', backref='recipe_steps')
    user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.recipe_name)


class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    
    ingredient_id = db.Column(db.Integer, primary_key=True, index=True)
    ingredient_name = db.Column(StrippedString(64), nullable=False, index=True)
    recipe_reference = db.Column(db.Boolean, default=False, nullable=False)
    user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    
    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.ingredient_name)


class Measurement(db.Model):
    __tablename__ = 'measurements'
    
    measurement_id = db.Column(db.Integer, primary_key=True)
    measurement_name = db.Column(StrippedString, nullable=False, index=True)
    quantity_measurement = db.relationship('Quantity', backref="ingredient_measurement")
    user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.measurement_name)


class Quantity(db.Model):
    __tablename__ = 'quantities'

    quantity_id = db.Column(db.Integer, primary_key=True)
    ingredient_id_fk = db.Column(db.Integer, db.ForeignKey('ingredients.ingredient_id'))
    measurement_id_fk = db.Column(db.Integer, db.ForeignKey('measurements.measurement_id'))
    ingredient_quantity = db.Column(db.Float(precision=2), nullable = False, index=True)
    production_time = db.Column(db.Float(precision=2), index=True)
    recipe_id_fk = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
    user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    
    def __repr__(self):
        return "<Ingrediente ID: {} | Receita ID: {} | Quantidade: {}>"\
            .format(self.ingredient_id_fk, self.recipe_id_fk, self.ingredient_quantity)


class RecipeStep(db.Model):
    __tablename__ = "recipe_steps"

    step_id = db.Column(db.Integer, primary_key=True)
    recipe_id_fk = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
    step_number = db.Column(db.Integer, nullable=False)
    step_description = db.Column(db.String)
    user_id_fk = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __repr__(self):
        return "<Step: {}; Step description: {} >".format(self.step_number, self.step_description)

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
