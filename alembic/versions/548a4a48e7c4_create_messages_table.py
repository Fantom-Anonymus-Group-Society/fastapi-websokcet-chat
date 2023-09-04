"""create messages table

Revision ID: 548a4a48e7c4
Revises: 911b9e5ba8ed
Create Date: 2023-09-04 20:02:21.297389

"""
from datetime import datetime

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '548a4a48e7c4'
down_revision = '911b9e5ba8ed'
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
