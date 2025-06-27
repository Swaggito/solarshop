"""add price to order items

Revision ID: add_price_to_order_items
Create Date: 2025-06-11 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_price_to_order_items'
down_revision = None  # Update this with your last migration ID
branch_labels = None
depends_on = None

def upgrade():
    # SQLite doesn't support ALTER TABLE ADD COLUMN with NOT NULL without default
    op.add_column('order_item',
        sa.Column('price', sa.Float(), nullable=True)
    )
    
    # Update existing records with product price
    op.execute("""
        UPDATE order_item 
        SET price = (
            SELECT price 
            FROM product 
            WHERE product.id = order_item.product_id
        )
    """)
    
    # Now make the column not nullable
    with op.batch_alter_table('order_item') as batch_op:
        batch_op.alter_column('price',
                            existing_type=sa.Float(),
                            nullable=False)

def downgrade():
    with op.batch_alter_table('order_item') as batch_op:
        batch_op.drop_column('price')
