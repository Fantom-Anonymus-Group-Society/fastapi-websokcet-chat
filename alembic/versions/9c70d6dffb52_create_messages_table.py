"""create messages table

Revision ID: 9c70d6dffb52
Revises: b5ac5c45d082
Create Date: 2023-09-06 18:03:45.899809

"""
from datetime import datetime

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c70d6dffb52'
down_revision = 'b5ac5c45d082'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user', sa.Integer, sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column('chat', sa.Integer, sa.ForeignKey("chats.id", ondelete="RESTRICT"), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), default=datetime.now)
    )


def downgrade() -> None:
    op.drop_table('messages')
