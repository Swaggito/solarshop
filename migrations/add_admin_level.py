from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add admin_access_level column with default value 0
    op.add_column('user', sa.Column('admin_access_level', sa.Integer(), nullable=True, server_default='0'))
    
    # Update existing admin users to have level 2
    op.execute("UPDATE user SET admin_access_level = 2 WHERE is_admin = 1")

def downgrade():
    # Remove the column if needed to rollback
    op.drop_column('user', 'admin_access_level')

if __name__ == '__main__':
    upgrade()
