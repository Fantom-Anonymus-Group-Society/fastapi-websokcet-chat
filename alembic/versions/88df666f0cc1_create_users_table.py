"""create users table

Revision ID: 88df666f0cc1
Revises: 
Create Date: 2023-09-06 18:03:32.409182

"""
from datetime import datetime

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '88df666f0cc1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('first_name', sa.String(255), nullable=False),
        sa.Column('last_name', sa.String(255), nullable=True),
        sa.Column('username', sa.String(225), nullable=False, unique=True),
        sa.Column('password', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), default=datetime.now)
    )


def downgrade() -> None:
    op.drop_table('users')
