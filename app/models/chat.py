import ormar
from datetime import datetime
from app.models.user import User
from typing import Optional, Union
from app.models.message import Message
from app.core.base_meta import BaseMeta
from app.serializers.messages.get_message_serializer import GetMessageSerializer
from app.serializers.users.get_user_serializer import GetUserSerializer


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

    async def get_if_exists(self, first_user: User, second_user: User):
        return await self.filter(
            ormar.or_(
                sender=first_user,
                receiver=first_user
            )
        ).get_or_none(
            ormar.or_(
                sender=second_user,
                receiver=second_user
            )
        )

    async def get_latest_message(self) -> GetMessageSerializer | None:
        try:
            last_message = await Message.objects.filter(chat=self).select_related('user').order_by('-created_at').first()
            return GetMessageSerializer(
                id=last_message.id,
                user=GetUserSerializer(
                    id=last_message.user.id,
                    username=last_message.user.username,
                    first_name=last_message.user.first_name,
                    last_name=last_message.user.last_name,
                    created_at=last_message.user.created_at
                ),
                chat=self.id,
                content=last_message.content,
                created_at=last_message.created_at
            )
        except ormar.NoMatch:
            return None
