"""add price to order item

Revision ID: add_price_to_order_item
Revises: [previous_revision_id]
Create Date: 2024-06-11 16:48:24.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_price_to_order_item'
down_revision = '[previous_revision_id]'  # Replace with your last migration ID
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('order_item', sa.Column('price', sa.Float(), nullable=False, server_default='0.0'))

def downgrade():
    op.drop_column('order_item', 'price')
