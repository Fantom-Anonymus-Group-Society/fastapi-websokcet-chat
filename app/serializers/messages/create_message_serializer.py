from pydantic import BaseModel


class CreateMessageSerializer(BaseModel):
    content: str
