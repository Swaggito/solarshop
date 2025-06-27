"""add role to user

Revision ID: add_role_to_user
Create Date: 2025-06-11 23:50:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_role_to_user'
down_revision = None  # Update this with your last migration ID
branch_labels = None
depends_on = None

def upgrade():
    # Add role column to user table
    with op.batch_alter_table('user') as batch_op:
        batch_op.add_column(sa.Column('role', sa.String(20), nullable=True, server_default='user'))

def downgrade():
    with op.batch_alter_table('user') as batch_op:
        batch_op.drop_column('role')
