from pydantic import BaseModel


class CreateUserSerializer(BaseModel):
    username: str
    first_name: str
    last_name: str
    is_staff: bool | None
    is_superuser: bool | None
    password: str
