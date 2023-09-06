"""create chats table

Revision ID: b5ac5c45d082
Revises: 88df666f0cc1
Create Date: 2023-09-06 18:03:41.421476

"""
from datetime import datetime

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b5ac5c45d082'
down_revision = '88df666f0cc1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'chats',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('sender', sa.Integer, sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column('receiver', sa.Integer, sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), default=datetime.now)
    )


def downgrade() -> None:
    op.drop_table('chats')
