from datetime import datetime
from pydantic import BaseModel

from app.helpers import covert_datetime_to_string


class GetUserSerializer(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    created_at: datetime

    class Config:
        json_encoders = {
            datetime: covert_datetime_to_string
        }
