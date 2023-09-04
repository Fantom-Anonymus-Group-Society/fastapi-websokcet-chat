from datetime import datetime
from pydantic import BaseModel
from app.helpers import covert_datetime_to_string
from app.serializers.users.get_user_serializer import GetUserSerializer


class GetMessageSerializer(BaseModel):
    id: int
    user: GetUserSerializer
    chat: int
    content: str
    created_at: datetime

    class Config:
        json_encoders = {
            datetime: covert_datetime_to_string
        }
