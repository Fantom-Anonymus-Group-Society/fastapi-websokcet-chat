import ormar
import asyncio
from typing import List
from app.models.chat import Chat
from app.models.user import User
from app.models.message import Message
from fastapi.websockets import WebSocket, WebSocketDisconnect
from app.services.pagination_service import PaginationService
from fastapi import APIRouter, Depends, HTTPException, status
from app.serializers.chats.get_chat_serializer import GetChatSerializer
from app.serializers.users.get_user_serializer import GetUserSerializer
from app.serializers.messages.get_message_serializer import GetMessageSerializer
from app.middlewares import jwt_authentication_middleware, jwt_websocket_middleware
from app.serializers.messages.create_message_serializer import CreateMessageSerializer
from app.services.singletones.socket_service_singleton import socket_service_singleton


router = APIRouter(
    prefix="/api/messages/{chat_id}",
    tags=["messages"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get('/')
async def messages_index(chat_id: int, page: int = 1, current_user: User = Depends(jwt_authentication_middleware)) -> dict:
    chat: Chat = await Chat.objects.filter(
        ormar.or_(
            sender=current_user,
            receiver=current_user
        )
    ).get_or_none(id=chat_id)
    if chat is None:
        raise HTTPException(detail='Chat is not found', status_code=status.HTTP_404_NOT_FOUND)

    messages: Message = Message.objects
    messages_count: int = await messages.count()
    messages: List[Message] = await messages.select_related(['user']).order_by('-created_at').paginate(page=page, page_size=50).all()

    return {
        'messages': [GetMessageSerializer(
            id=message.id,
            user=GetUserSerializer(
                id=message.user.id,
                username=message.user.username,
                first_name=message.user.first_name,
                last_name=message.user.last_name,
                created_at=message.user.created_at
            ),
            chat=message.chat.id,
            content=message.content,
            created_at=message.created_at
        ) for message in messages],
        'pagination': PaginationService.get_pagination_data(messages_count)
    }


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=GetMessageSerializer)
async def messages_store(chat_id: int, body: CreateMessageSerializer, current_user: User = Depends(jwt_authentication_middleware)):
    chat: Chat = await Chat.objects.get_or_none(id=chat_id)
    if chat is None:
        raise HTTPException(detail='Chat is not found', status_code=status.HTTP_404_NOT_FOUND)
    message: Message = await Message.objects.create(
        user=current_user,
        chat=chat,
        content=body.content
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
        to_delete=True,
    ).json(ensure_ascii=False)

    sender_id: int = chat.sender.id
    receiver_id: int = chat.receiver.id

    message_json: str = GetMessageSerializer(
        id=message.id,
        user=GetUserSerializer(
            id=message.user.id,
            username=message.user.username,
            first_name=message.user.first_name,
            last_name=message.user.last_name,
            created_at=message.user.created_at
        ),
        chat=chat.id,
        content=message.content,
        created_at=message.created_at,
        to_delete=True
    ).json(ensure_ascii=False)

    # update chat message list
    await socket_service_singleton.send_message(message_json, chat.id, 'chat')
    # update chat in the list
    await socket_service_singleton.send_message(chat_json, sender_id)
    await socket_service_singleton.send_message(chat_json, receiver_id)

    return message


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def chats_destroy(chat_id: int, id: int, current_user: User = Depends(jwt_authentication_middleware)):
    chat: Chat = await Chat.objects.get_or_none(id=chat_id)
    if chat is None:
        raise HTTPException(detail='Chat is not found', status_code=status.HTTP_404_NOT_FOUND)

    message: Message = await Message.objects.filter(user=current_user).filter(chat=chat).get_or_none(id=id)
    if message is None:
        raise HTTPException(detail='Message is not found', status_code=status.HTTP_404_NOT_FOUND)

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

    message_json: str = GetMessageSerializer(
        id=message.id,
        user=GetUserSerializer(
            id=message.user.id,
            username=message.user.username,
            first_name=message.user.first_name,
            last_name=message.user.last_name,
            created_at=message.user.created_at
        ),
        chat=chat.id,
        content=message.content,
        created_at=message.created_at,
        to_delete=True
    ).json(ensure_ascii=False)

    await message.delete()

    # update chat message list
    await socket_service_singleton.send_message(message_json, chat.id, 'chat')
    # update chat in the list
    await socket_service_singleton.send_message(chat_json, sender_id)
    await socket_service_singleton.send_message(chat_json, receiver_id)


@router.websocket('/')
async def message_list_websocket(websocket: WebSocket, chat_id: int, current_user: User = Depends(jwt_websocket_middleware)):
    await socket_service_singleton.connect(
        websocket=websocket,
        instance_id=chat_id,
        connection_type='chat'
    )
    try:
        while True:
            await asyncio.sleep(0.5)
            await websocket.receive_json()
    except WebSocketDisconnect:
        socket_service_singleton.disconnect(
            websocket=websocket,
            instance_id=chat_id,
            connection_type='chat'
        )
