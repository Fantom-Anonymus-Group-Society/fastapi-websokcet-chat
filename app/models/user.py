import ormar
from datetime import datetime
from app.core.base_meta import BaseMeta


class User(ormar.Model):
    class Meta(BaseMeta):
        tablename = "users"

    id: int = ormar.Integer(primary_key=True)
    first_name: str = ormar.String(max_length=255, nullable=True)
    last_name: str = ormar.String(max_length=255, nullable=True)
    username: str = ormar.String(max_length=255, unique=True, nullable=True)
    password: str = ormar.String(max_length=255, nullable=False)
    created_at: datetime = ormar.DateTime(timezone=True, default=datetime.now)
