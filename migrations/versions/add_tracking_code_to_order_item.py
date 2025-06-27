"""add tracking code to order items

Revision ID: add_tracking_code_v1
Create Date: 2024-06-12 02:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
import string
import random

revision = 'add_tracking_code_v1'
down_revision = None  # Update this with your last migration ID

def generate_tracking_code(order_id):
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"ORD-{order_id}-{code}"

def upgrade():
    # Add tracking_code column
    op.add_column('order_item', sa.Column('tracking_code', sa.String(20), nullable=True))

    # Generate tracking codes for existing order items
    connection = op.get_bind()
    order_items = connection.execute('SELECT id, order_id FROM order_item').fetchall()
    
    for item_id, order_id in order_items:
        tracking_code = generate_tracking_code(order_id)
        connection.execute(
            'UPDATE order_item SET tracking_code = ? WHERE id = ?',
            (tracking_code, item_id)
        )

    # Make tracking_code not nullable after updating existing records
    with op.batch_alter_table('order_item') as batch_op:
        batch_op.alter_column('tracking_code', nullable=False)

def downgrade():
    with op.batch_alter_table('order_item') as batch_op:
        batch_op.drop_column('tracking_code')
