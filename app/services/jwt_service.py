import jwt
import datetime

from starlette import status

from app.models.user import User
from fastapi import HTTPException
from app.configs.environment import env


class JWTService:
    @staticmethod
    def create_token_by_user(user: User, additional_payload: dict | None = None) -> str:
        if additional_payload is None:
            additional_payload: dict = {}
        payload: dict = {
            'sub': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=72)
        }
        payload.update(additional_payload)
        return jwt.encode(payload, env.secret_key, algorithm=env.algorithm)

    @staticmethod
    def get_payload_from_token(token: str) -> dict:
        token: str = token.split(' ')[1]
        try:
            return jwt.decode(token, env.secret_key, algorithms=[env.algorithm])
        except jwt.exceptions.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is expired")
        except jwt.exceptions.DecodeError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect token type")
