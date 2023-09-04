from typing import Annotated

from app.models.user import User
from fastapi import Header, Query
from fastapi.websockets import WebSocket
from app.middlewares.base_auth_middleware import BaseAuthMiddleware


async def jwt_authentication_middleware(authorization: str | None = Header(default=None)) -> User:
    return await (BaseAuthMiddleware()).authenticate(authorization)


async def jwt_websocket_middleware(websocket: WebSocket, authorization: Annotated[str | None, Query()] = None) -> User:
    return await (BaseAuthMiddleware(websocket=True)).authenticate(authorization)
