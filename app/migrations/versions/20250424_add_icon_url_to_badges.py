"""Add icon_url to badges table

Revision ID: 20250424_add_icon_url
Revises: 20250419_add_admin_id_to_points_transaction
Create Date: 2025-04-24 20:34:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250424_add_icon_url'
down_revision = '20250419_add_admin_id_to_points_transaction'
branch_labels = None
depends_on = None


def upgrade():
    # Add icon_url column to badges table
    op.add_column('badges', sa.Column('icon_url', sa.String(), nullable=True))
    
    # Update existing records with a default value
    op.execute("UPDATE badges SET icon_url = '/static/images/badges/default_badge.png'")


def downgrade():
    # Remove icon_url column from badges table
    op.drop_column('badges', 'icon_url')
