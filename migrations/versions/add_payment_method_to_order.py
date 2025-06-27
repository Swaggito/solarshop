"""add payment method and special notes to order

Revision ID: add_payment_method_v1
Create Date: 2025-06-12 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_payment_method_v1'
down_revision = None  # Update this with your last migration ID

def upgrade():
    with op.batch_alter_table('order') as batch_op:
        batch_op.add_column(sa.Column('payment_method', sa.String(50), nullable=True))
        batch_op.add_column(sa.Column('special_notes', sa.Text(), nullable=True))

def downgrade():
    with op.batch_alter_table('order') as batch_op:
        batch_op.drop_column('payment_method')
        batch_op.drop_column('special_notes')
