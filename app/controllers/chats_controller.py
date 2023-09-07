import ormar
import asyncio
from typing import List
from app.models.chat import Chat
from app.models.user import User
from fastapi.websockets import WebSocket, WebSocketDisconnect
from fastapi import APIRouter, Depends, HTTPException, status
from app.serializers.chats.get_chat_serializer import GetChatSerializer
from app.serializers.users.get_user_serializer import GetUserSerializer
from app.serializers.chats.create_chat_serializer import CreateChatSerializer
from app.middlewares import jwt_authentication_middleware, jwt_websocket_middleware
from app.services.singletones.socket_service_singleton import socket_service_singleton

router = APIRouter(
    prefix="/api/chats",
    tags=["chats"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get('/')
async def chats_index(current_user: User = Depends(jwt_authentication_middleware)) -> list:
    chats: List[Chat] = await Chat.get_chat_list(current_user).select_related(['sender', 'receiver', 'messages'])\
        .order_by('-messages__created_at').all()

    return [GetChatSerializer(
            id=chat.id,
            sender=GetUserSerializer(
                id=chat.sender.id,
                username=chat.sender.username,
                first_name=chat.sender.first_name,
                last_name=chat.sender.last_name,
                created_at=chat.sender.created_at
            ),
            receiver=GetUserSerializer(
                id=chat.receiver.id,
                username=chat.receiver.username,
                first_name=chat.receiver.first_name,
                last_name=chat.receiver.last_name,
                created_at=chat.receiver.created_at
            ),
            last_message=await chat.get_latest_message(),
            created_at=chat.created_at
        ) for chat in chats]


@router.get('/{id}', response_model=GetChatSerializer)
async def chats_show(id: int, current_user: User = Depends(jwt_authentication_middleware)) -> Chat:
    chat: Chat | None = await Chat.get_chat_list(current_user).select_related(['sender', 'receiver']).get_or_none(id=id)
    if chat is None:
        raise HTTPException(detail='Chat is not found', status_code=status.HTTP_404_NOT_FOUND)

    return chat


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=GetChatSerializer)
async def chats_store(body: CreateChatSerializer, current_user: User = Depends(jwt_authentication_middleware)):
    receiver: User = await User.objects.get_or_none(id=body.receiver_id)
    if receiver is None:
        raise HTTPException(detail='Receiver is not found', status_code=status.HTTP_404_NOT_FOUND)
    existing_chat: Chat | None = await Chat.get_if_exists(current_user, receiver)
    if existing_chat is not None:
        return existing_chat

    chat: Chat = await Chat.objects.create(
        sender=current_user,
        receiver=receiver
    )

    chat_json: str = GetChatSerializer(
        id=chat.id,
        sender=GetUserSerializer(
            id=chat.sender.id,
            username=chat.sender.username,
            first_name=chat.sender.first_name,
            last_name=chat.sender.last_name,
            created_at=chat.sender.created_at
        ),
        receiver=GetUserSerializer(
            id=chat.receiver.id,
            username=chat.receiver.username,
            first_name=chat.receiver.first_name,
            last_name=chat.receiver.last_name,
            created_at=chat.receiver.created_at
        ),
        last_message=None,
        created_at=chat.created_at,
    ).json(ensure_ascii=False)

    sender_id: int = chat.sender.id
    receiver_id: int = chat.receiver.id

    await socket_service_singleton.send_message(chat_json, sender_id)
    await socket_service_singleton.send_message(chat_json, receiver_id)

    return chat


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def chats_destroy(id: int, current_user: User = Depends(jwt_authentication_middleware)):
    chat: Chat = await Chat.objects.filter(
        ormar.or_(
            sender=current_user,
            receiver=current_user
        )
    ).get_or_none(id=id)

    if chat is None:
        raise HTTPException(detail='Chat is not found', status_code=status.HTTP_404_NOT_FOUND)

    chat_json: str = GetChatSerializer(
        id=chat.id,
        sender=GetUserSerializer(
            id=chat.sender.id,
            username=chat.sender.username,
            first_name=chat.sender.first_name,
            last_name=chat.sender.last_name,
            created_at=chat.sender.created_at
        ),
        receiver=GetUserSerializer(
            id=chat.receiver.id,
            username=chat.receiver.username,
            first_name=chat.receiver.first_name,
            last_name=chat.receiver.last_name,
            created_at=chat.receiver.created_at
        ),
        last_message=None,
        created_at=chat.created_at,
        to_delete=True,
    ).json(ensure_ascii=False)

    sender_id: int = chat.sender.id
    receiver_id: int = chat.receiver.id

    await chat.delete()

    await socket_service_singleton.send_message(chat_json, sender_id)
    await socket_service_singleton.send_message(chat_json, receiver_id)


@router.websocket('/')
async def chat_list_websocket(websocket: WebSocket, current_user: User = Depends(jwt_websocket_middleware)):
    await socket_service_singleton.connect(
        websocket=websocket,
        instance_id=current_user.id
    )
    try:
        while True:
            await asyncio.sleep(0.5)
            await websocket.receive_json()
    except WebSocketDisconnect:
        socket_service_singleton.disconnect(
            websocket=websocket,
            instance_id=current_user.id
        )
