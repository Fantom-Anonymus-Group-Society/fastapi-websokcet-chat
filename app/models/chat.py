from typing import Optional, Union

import ormar
from datetime import datetime
from app.core.base_meta import BaseMeta
from app.models.user import User


class Chat(ormar.Model):
    class Meta(BaseMeta):
        tablename = "chats"

    id: int = ormar.Integer(primary_key=True)
    sender: Optional[Union[User, dict]] = ormar.ForeignKey(User, related_name="sender_chats", ondelete="RESTRICT")
    receiver: Optional[Union[User, dict]] = ormar.ForeignKey(User, related_name="receiver_chats", ondelete="RESTRICT")
    created_at: datetime = ormar.DateTime(timezone=True, default=datetime.now)

    def get_chat_list(self, user: User):
        return self.filter(
            ormar.or_(
                sender=user,
                receiver=user
            )
        )
