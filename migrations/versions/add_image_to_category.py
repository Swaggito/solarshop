from alembic import op
import sqlalchemy as sa

"""add image to category table

Revision ID: add_image_to_category
Revises: # previous_revision_id
Create Date: 2024-01-25
"""

def upgrade():
    op.add_column('category', sa.Column('image', sa.String(255), nullable=True))

def downgrade():
    op.drop_column('category', 'image')
