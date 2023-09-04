from fastapi import HTTPException, status, WebSocketException

from app.models.user import User
from app.services.jwt_service import JWTService


class BaseAuthMiddleware:
    def __init__(self, websocket: bool = False):
        self.websocket = websocket

        self.no_token_websocket_error: WebSocketException = WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

        self.no_token_error: HTTPException = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                                           detail="No Authorization header is provided")
        self.incorrect_token_error: HTTPException = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                                                  detail="Incorrect token type")
        self.forbidden_error: HTTPException = HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                                            detail="You are not permitted to use this source")

    def validate_payload_(self, authorization: str) -> dict:
        if authorization is None:
            if self.websocket:
                raise self.no_token_websocket_error
            raise self.no_token_error
        return JWTService.get_payload_from_token(authorization)

    async def get_and_validate_user_(self, payload: dict) -> User:
        user: User = await User.objects.get_or_none(id=payload.get('sub'))
        if not user or user.username != payload.get('username'):
            if self.websocket:
                raise self.no_token_websocket_error
            raise self.incorrect_token_error
        return user

    async def authenticate(self, authorization: str) -> User:
        payload: dict = self.validate_payload_(authorization)
        return await self.get_and_validate_user_(payload)
