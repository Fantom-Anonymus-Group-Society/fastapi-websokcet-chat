from typing import Optional, Union

import ormar
from datetime import datetime
from app.core.base_meta import BaseMeta
from app.models.user import User
from app.models.chat import Chat


class Message(ormar.Model):
    class Meta(BaseMeta):
        tablename = "messages"

    id: int = ormar.Integer(primary_key=True)
    user: Optional[Union[User, dict]] = ormar.ForeignKey(User, related_name="messages", ondelete="RESTRICT")
    chat: Optional[Union[Chat, dict]] = ormar.ForeignKey(Chat, related_name="messages", ondelete="RESTRICT")
    content: str = ormar.Text(nullable=False)
    created_at: datetime = ormar.DateTime(timezone=True, default=datetime.now)
