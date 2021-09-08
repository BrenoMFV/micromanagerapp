"""empty message

Revision ID: 08e3bc28057b
Revises: 
Create Date: 2021-08-08 01:22:28.884649

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from app.helpers import StrippedString

# revision identifiers, used by Alembic.
revision = '08e3bc28057b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('payment_methods',
    sa.Column('method_id', sa.Integer(), nullable=False),
    sa.Column('method', sa.String(length=32), nullable=True),
    sa.PrimaryKeyConstraint('method_id')
    )
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
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('clients_categories',
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('category_name', sa.String(length=32), nullable=False),
    sa.Column('user_id_fk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id_fk'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('category_id')
    )
    op.create_index(op.f('ix_clients_categories_category_name'), 'clients_categories', ['category_name'], unique=False)
    op.create_table('products_categories',
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('category_name', sa.String(), nullable=False),
    sa.Column('user_id_fk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id_fk'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('category_id')
    )
    op.create_table('units',
    sa.Column('unit_id', sa.Integer(), nullable=False),
    sa.Column('unit', sa.String(), nullable=True),
    sa.Column('user_id_fk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id_fk'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('unit_id')
    )
    op.create_table('clients',
    sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', StrippedString(length=32), nullable=False),
    sa.Column('email', StrippedString(length=64), nullable=True),
    sa.Column('ddd', sa.String(length=4), nullable=True),
    sa.Column('phonenumber', sa.String(length=10), nullable=True),
    sa.Column('cpf', StrippedString(length=14), nullable=True),
    sa.Column('cnpj', StrippedString(length=18), nullable=True),
    sa.Column('added', sa.DateTime(), nullable=True),
    sa.Column('user_id_fk', sa.Integer(), nullable=True),
    sa.Column('category_id_fk', sa.Integer(), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['category_id_fk'], ['clients_categories.category_id'], ),
    sa.ForeignKeyConstraint(['user_id_fk'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('client_id')
    )
    op.create_index(op.f('ix_clients_email'), 'clients', ['email'], unique=False)
    op.create_index(op.f('ix_clients_name'), 'clients', ['name'], unique=False)
    op.create_table('products',
    sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('product_name', StrippedString(length=64), nullable=False),
    sa.Column('product_category_fk', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Float(precision=2), nullable=False),
    sa.Column('stock_alert', sa.Float(precision=2), nullable=True),
    sa.Column('unit_id_fk', sa.Integer(), nullable=True),
    sa.Column('user_id_fk', sa.Integer(), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['product_category_fk'], ['products_categories.category_id'], ),
    sa.ForeignKeyConstraint(['unit_id_fk'], ['units.unit_id'], ),
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
    sa.Column('client_id_fk', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('user_id_fk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['client_id_fk'], ['clients.client_id'], ),
    sa.ForeignKeyConstraint(['user_id_fk'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('address_id')
    )
    op.create_table('prices',
    sa.Column('price_id', sa.Integer(), nullable=False),
    sa.Column('price', sa.Float(precision=2), nullable=False),
    sa.Column('product_id_fk', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('category_id_fk', sa.Integer(), nullable=True),
    sa.Column('user_id_fk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category_id_fk'], ['clients_categories.category_id'], ),
    sa.ForeignKeyConstraint(['product_id_fk'], ['products.product_id'], ),
    sa.ForeignKeyConstraint(['user_id_fk'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('price_id')
    )
    op.create_table('productions',
    sa.Column('production_id', sa.Integer(), nullable=False),
    sa.Column('product_id_fk', postgresql.UUID(as_uuid=True), nullable=True),
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
    op.create_table('sales',
    sa.Column('sale_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('client_id_fk', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('total_value', sa.Float(precision=2), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('delivery_date', sa.Date(), nullable=True),
    sa.Column('due', sa.Boolean(), nullable=True),
    sa.Column('payment_method_id_fk', sa.Integer(), nullable=True),
    sa.Column('user_id_fk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['client_id_fk'], ['clients.client_id'], ),
    sa.ForeignKeyConstraint(['payment_method_id_fk'], ['payment_methods.method_id'], ),
    sa.ForeignKeyConstraint(['user_id_fk'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('sale_id')
    )
    op.create_index(op.f('ix_sales_client_id_fk'), 'sales', ['client_id_fk'], unique=False)
    op.create_index(op.f('ix_sales_date'), 'sales', ['date'], unique=False)
    op.create_table('partial_sales',
    sa.Column('partial_sale_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('product_id_fk', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('product_amount', sa.Float(precision=2), nullable=False),
    sa.Column('price', sa.Float(precision=2), nullable=False),
    sa.Column('partial_total', sa.Float(precision=2), nullable=True),
    sa.Column('sale_id_fk', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id_fk', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['product_id_fk'], ['products.product_id'], ),
    sa.ForeignKeyConstraint(['sale_id_fk'], ['sales.sale_id'], ),
    sa.ForeignKeyConstraint(['user_id_fk'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('partial_sale_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('partial_sales')
    op.drop_index(op.f('ix_sales_date'), table_name='sales')
    op.drop_index(op.f('ix_sales_client_id_fk'), table_name='sales')
    op.drop_table('sales')
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
    op.drop_table('products_categories')
    op.drop_index(op.f('ix_clients_categories_category_name'), table_name='clients_categories')
    op.drop_table('clients_categories')
    op.drop_table('users')
    op.drop_table('payment_methods')
    # ### end Alembic commands ###