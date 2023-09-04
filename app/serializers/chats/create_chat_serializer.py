from pydantic import BaseModel


class CreateChatSerializer(BaseModel):
    receiver_id: int
