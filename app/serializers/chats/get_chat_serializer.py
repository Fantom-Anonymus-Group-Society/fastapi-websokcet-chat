from datetime import datetime
from pydantic import BaseModel
from app.helpers import covert_datetime_to_string
from app.serializers.users.get_user_serializer import GetUserSerializer
from app.serializers.messages.get_message_serializer import GetMessageSerializer


class GetChatSerializer(BaseModel):
    id: int
    sender: GetUserSerializer
    receiver: GetUserSerializer
    last_message: GetMessageSerializer | None
    created_at: datetime

    class Config:
        json_encoders = {
            datetime: covert_datetime_to_string
        }
