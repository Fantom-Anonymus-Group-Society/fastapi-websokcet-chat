from datetime import datetime
from pydantic import BaseModel


class RegistrationSerializer(BaseModel):
    username: str
    first_name: str
    last_name: str
    password: str
    confirmation: str
