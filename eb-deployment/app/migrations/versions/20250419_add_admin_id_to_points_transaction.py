"""
Add admin_id column to points_transaction table

Revision ID: 20250419_add_admin_id
Revises: 
Create Date: 2025-04-19 14:35:00
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('points_transaction', sa.Column('admin_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_points_transaction_admin_id_user', 'points_transaction', 'user', ['admin_id'], ['id'])

def downgrade():
    op.drop_constraint('fk_points_transaction_admin_id_user', 'points_transaction', type_='foreignkey')
    op.drop_column('points_transaction', 'admin_id')
