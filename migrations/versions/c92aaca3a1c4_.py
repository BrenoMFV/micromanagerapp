"""empty message

Revision ID: c92aaca3a1c4
Revises: 
Create Date: 2021-06-23 21:33:18.354802

"""
from alembic import op
import sqlalchemy as sa
from app.helpers import StrippedString

# revision identifiers, used by Alembic.
revision = 'c92aaca3a1c4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('first_name', StrippedString(length=32), nullable=False),
    sa.Column('last_name', StrippedString(length=64), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=False),
    sa.Column('email', StrippedString(length=64), nullable=False),
    sa.Column('new_email', StrippedString(length=64), nullable=True),
    sa.Column('company_name', StrippedString(length=24), nullable=True),
    sa.Column('cnpj', StrippedString(length=32), nullable=True),
    sa.Column('member_since', sa.DateTime(), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.Column('permission', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_first_name'), 'users', ['first_name'], unique=False)
    op.create_table('clients_categories',
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('category_name', sa.String(length=32), nullable=False),
    sa.Column('user_id_fk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id_fk'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('category_id')
    )
    op.create_index(op.f('ix_clients_categories_category_name'), 'clients_categories', ['category_name'], unique=False)
    op.create_table('ingredients',
    sa.Column('ingredient_id', sa.Integer(), nullable=False),
    sa.Column('ingredient_name', StrippedString(length=64), nullable=False),
    sa.Column('user_id_fk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id_fk'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('ingredient_id')
    )
    op.create_index(op.f('ix_ingredients_ingredient_id'), 'ingredients', ['ingredient_id'], unique=False)
    op.create_index(op.f('ix_ingredients_ingredient_name'), 'ingredients', ['ingredient_name'], unique=False)
    op.create_table('measurements',
    sa.Column('measurement_id', sa.Integer(), nullable=False),
    sa.Column('measurement_name', StrippedString(), nullable=False),
    sa.Column('user_id_fk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id_fk'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('measurement_id')
    )
    op.create_index(op.f('ix_measurements_measurement_name'), 'measurements', ['measurement_name'], unique=False)
    op.create_table('payments',
    sa.Column('payment_id', sa.Integer(), nullable=False),
    sa.Column('value', sa.Float(precision=2), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('user_id_fk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id_fk'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('payment_id')
    )
    op.create_index(op.f('ix_payments_date'), 'payments', ['date'], unique=False)
    op.create_index(op.f('ix_payments_value'), 'payments', ['value'], unique=False)
    op.create_table('products_categories',
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('category_name', sa.String(), nullable=False),
    sa.Column('user_id_fk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id_fk'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('category_id')
    )
    op.create_table('suppliers',
    sa.Column('supplier_id', sa.Integer(), nullable=False),
    sa.Column('supplier_name', StrippedString(length=64), nullable=False),
    sa.Column('cnpj', sa.String(length=18), nullable=True),
    sa.Column('user_id_fk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id_fk'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('supplier_id')
    )
    op.create_index(op.f('ix_suppliers_supplier_name'), 'suppliers', ['supplier_name'], unique=False)
    op.create_index(op.f('ix_suppliers_user_id_fk'), 'suppliers', ['user_id_fk'], unique=False)
    op.create_table('units',
    sa.Column('unit_id', sa.Integer(), nullable=False),
    sa.Column('unit', sa.String(), nullable=True),
    sa.Column('user_id_fk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id_fk'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('unit_id')
    )
    op.create_table('clients',
    sa.Column('client_id', sa.Integer(), nullable=False),
    sa.Column('name', StrippedString(length=32), nullable=False),
    sa.Column('email', StrippedString(length=64), nullable=True),
    sa.Column('ddd', sa.String(length=2), nullable=True),
    sa.Column('phonenumber', sa.String(length=16), nullable=True),
    sa.Column('cpf', StrippedString(length=14), nullable=True),
    sa.Column('cnpj', StrippedString(length=18), nullable=True),
    sa.Column('added', sa.DateTime(), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.Column('category_id_fk', sa.Integer(), nullable=True),
    sa.Column('user_id_fk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category_id_fk'], ['clients_categories.category_id'], ),
    sa.ForeignKeyConstraint(['user_id_fk'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('client_id')
    )
    op.create_index(op.f('ix_clients_email'), 'clients', ['email'], unique=False)
    op.create_index(op.f('ix_clients_name'), 'clients', ['name'], unique=False)
    op.create_table('products',
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('product_name', StrippedString(length=64), nullable=False),
    sa.Column('product_category_fk', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Float(precision=2), nullable=False),
    sa.Column('stock_alert', sa.Float(precision=2), nullable=True),
    sa.Column('unit', sa.Integer(), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.Column('user_id_fk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['product_category_fk'], ['products_categories.category_id'], ),
    sa.ForeignKeyConstraint(['unit'], ['units.unit_id'], ),
    sa.ForeignKeyConstraint(['user_id_fk'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('product_id')
    )
    op.create_index(op.f('ix_products_product_name'), 'products', ['product_name'], unique=False)
    op.create_table('addresses',
    sa.Column('address_id', sa.Integer(), nullable=False),
    sa.Column('address', sa.String(length=1024), nullable=True),
    sa.Column('city', sa.String(length=32), nullable=True),
    sa.Column('state', sa.String(length=2), nullable=True),
    sa.Column('observations', sa.String(length=128), nullable=True),
    sa.Column('client_id_fk', sa.Integer(), nullable=True),
    sa.Column('user_id_fk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['client_id_fk'], ['clients.client_id'], ),
    sa.ForeignKeyConstraint(['user_id_fk'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('address_id')
    )
    op.create_table('prices',
    sa.Column('price_id', sa.Integer(), nullable=False),
    sa.Column('product_id_fk', sa.Integer(), nullable=True),
    sa.Column('category_id_fk', sa.Integer(), nullable=True),
    sa.Column('price', sa.Float(precision=2), nullable=False),
    sa.Column('user_id_fk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category_id_fk'], ['clients_categories.category_id'], ),
    sa.ForeignKeyConstraint(['product_id_fk'], ['products.product_id'], ),
    sa.ForeignKeyConstraint(['user_id_fk'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('price_id')
    )
    op.create_table('productions',
    sa.Column('production_id', sa.Integer(), nullable=False),
    sa.Column('product_id_fk', sa.Integer(), nullable=True),
    sa.Column('amount_produced', sa.Integer(), nullable=False),
    sa.Column('production_date', sa.Date(), nullable=False),
    sa.Column('expiration_date', sa.Date(), nullable=True),
    sa.Column('_batch', sa.String(), nullable=True),
    sa.Column('user_id_fk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['product_id_fk'], ['products.product_id'], ),
    sa.ForeignKeyConstraint(['user_id_fk'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('production_id')
    )
    op.create_index(op.f('ix_productions_product_id_fk'), 'productions', ['product_id_fk'], unique=False)
    op.create_table('recipes',
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.Column('product_id_fk', sa.Integer(), nullable=True),
    sa.Column('recipe_name', sa.String(length=64), nullable=False),
    sa.Column('recipe_description', sa.String(), nullable=True),
    sa.Column('production_time', sa.Float(precision=2), nullable=True),
    sa.Column('user_id_fk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['product_id_fk'], ['products.product_id'], ),
    sa.ForeignKeyConstraint(['user_id_fk'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('recipe_id')
    )
    op.create_index(op.f('ix_recipes_product_id_fk'), 'recipes', ['product_id_fk'], unique=False)
    op.create_index(op.f('ix_recipes_production_time'), 'recipes', ['production_time'], unique=False)
    op.create_index(op.f('ix_recipes_recipe_name'), 'recipes', ['recipe_name'], unique=False)
    op.create_table('sales',
    sa.Column('sale_id', sa.Integer(), nullable=False),
    sa.Column('client_id_fk', sa.Integer(), nullable=True),
    sa.Column('total_value', sa.Float(precision=2), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('delivery_date', sa.Date(), nullable=True),
    sa.Column('due', sa.Boolean(), nullable=True),
    sa.Column('user_id_fk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['client_id_fk'], ['clients.client_id'], ),
    sa.ForeignKeyConstraint(['user_id_fk'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('sale_id')
    )
    op.create_index(op.f('ix_sales_client_id_fk'), 'sales', ['client_id_fk'], unique=False)
    op.create_index(op.f('ix_sales_date'), 'sales', ['date'], unique=False)
    op.create_table('partial_sales',
    sa.Column('partial_sale_id', sa.Integer(), nullable=False),
    sa.Column('product_id_fk', sa.Integer(), nullable=False),
    sa.Column('product_amount', sa.Float(precision=2), nullable=False),
    sa.Column('price', sa.Float(precision=2), nullable=False),
    sa.Column('partial_total', sa.Float(precision=2), nullable=True),
    sa.Column('sale_id_fk', sa.Integer(), nullable=False),
    sa.Column('user_id_fk', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['product_id_fk'], ['products.product_id'], ),
    sa.ForeignKeyConstraint(['sale_id_fk'], ['sales.sale_id'], ),
    sa.ForeignKeyConstraint(['user_id_fk'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('partial_sale_id')
    )
    op.create_table('quantities',
    sa.Column('quantity_id', sa.Integer(), nullable=False),
    sa.Column('ingredient_id_fk', sa.Integer(), nullable=True),
    sa.Column('measurement_id_fk', sa.Integer(), nullable=True),
    sa.Column('ingredient_quantity', sa.Float(precision=2), nullable=False),
    sa.Column('production_time', sa.Float(precision=2), nullable=True),
    sa.Column('recipe_id_fk', sa.Integer(), nullable=True),
    sa.Column('user_id_fk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['ingredient_id_fk'], ['ingredients.ingredient_id'], ),
    sa.ForeignKeyConstraint(['measurement_id_fk'], ['measurements.measurement_id'], ),
    sa.ForeignKeyConstraint(['recipe_id_fk'], ['recipes.recipe_id'], ),
    sa.ForeignKeyConstraint(['user_id_fk'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('quantity_id')
    )
    op.create_index(op.f('ix_quantities_ingredient_quantity'), 'quantities', ['ingredient_quantity'], unique=False)
    op.create_index(op.f('ix_quantities_production_time'), 'quantities', ['production_time'], unique=False)
    op.create_table('recipe_steps',
    sa.Column('step_id', sa.Integer(), nullable=False),
    sa.Column('recipe_id_fk', sa.Integer(), nullable=True),
    sa.Column('step_number', sa.Integer(), nullable=False),
    sa.Column('step_description', sa.String(), nullable=True),
    sa.Column('user_id_fk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['recipe_id_fk'], ['recipes.recipe_id'], ),
    sa.ForeignKeyConstraint(['user_id_fk'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('step_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('recipe_steps')
    op.drop_index(op.f('ix_quantities_production_time'), table_name='quantities')
    op.drop_index(op.f('ix_quantities_ingredient_quantity'), table_name='quantities')
    op.drop_table('quantities')
    op.drop_table('partial_sales')
    op.drop_index(op.f('ix_sales_date'), table_name='sales')
    op.drop_index(op.f('ix_sales_client_id_fk'), table_name='sales')
    op.drop_table('sales')
    op.drop_index(op.f('ix_recipes_recipe_name'), table_name='recipes')
    op.drop_index(op.f('ix_recipes_production_time'), table_name='recipes')
    op.drop_index(op.f('ix_recipes_product_id_fk'), table_name='recipes')
    op.drop_table('recipes')
    op.drop_index(op.f('ix_productions_product_id_fk'), table_name='productions')
    op.drop_table('productions')
    op.drop_table('prices')
    op.drop_table('addresses')
    op.drop_index(op.f('ix_products_product_name'), table_name='products')
    op.drop_table('products')
    op.drop_index(op.f('ix_clients_name'), table_name='clients')
    op.drop_index(op.f('ix_clients_email'), table_name='clients')
    op.drop_table('clients')
    op.drop_table('units')
    op.drop_index(op.f('ix_suppliers_user_id_fk'), table_name='suppliers')
    op.drop_index(op.f('ix_suppliers_supplier_name'), table_name='suppliers')
    op.drop_table('suppliers')
    op.drop_table('products_categories')
    op.drop_index(op.f('ix_payments_value'), table_name='payments')
    op.drop_index(op.f('ix_payments_date'), table_name='payments')
    op.drop_table('payments')
    op.drop_index(op.f('ix_measurements_measurement_name'), table_name='measurements')
    op.drop_table('measurements')
    op.drop_index(op.f('ix_ingredients_ingredient_name'), table_name='ingredients')
    op.drop_index(op.f('ix_ingredients_ingredient_id'), table_name='ingredients')
    op.drop_table('ingredients')
    op.drop_index(op.f('ix_clients_categories_category_name'), table_name='clients_categories')
    op.drop_table('clients_categories')
    op.drop_index(op.f('ix_users_first_name'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
