from datetime import datetime
from pydantic import BaseModel
from app.helpers import covert_datetime_to_string
from app.models.chat import Chat
from app.serializers.users.get_user_serializer import GetUserSerializer


class GetMessageSerializer(BaseModel):
    id: int
    user: GetUserSerializer
    chat: int | Chat
    content: str
    created_at: datetime
    to_delete: bool | None

    class Config:
        json_encoders = {
            datetime: covert_datetime_to_string
        }
