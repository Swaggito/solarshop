"""add created_at to user

Revision ID: add_created_at_to_user
Create Date: 2025-06-11 23:55:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_created_at_to_user'
down_revision = None  # Update this with your last migration ID
branch_labels = None
depends_on = None

def upgrade():
    # Add created_at column to user table
    with op.batch_alter_table('user') as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime, nullable=True, server_default=sa.func.now()))

def downgrade():
    with op.batch_alter_table('user') as batch_op:
        batch_op.drop_column('created_at')
