from pydantic import BaseModel


class UpdateProfileSerializer(BaseModel):
    username: str | None
    first_name: str | None
    last_name: str | None
    password: str | None
