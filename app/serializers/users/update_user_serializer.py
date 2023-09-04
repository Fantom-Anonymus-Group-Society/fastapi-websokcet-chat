from pydantic import BaseModel


class UpdateUserSerializer(BaseModel):
    username: str | None
    first_name: str | None
    last_name: str | None
    is_staff: bool | None
    is_superuser: bool | None
    password: str | None
