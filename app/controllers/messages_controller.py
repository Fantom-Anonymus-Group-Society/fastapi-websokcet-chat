from typing import List

import ormar
from app.models.chat import Chat
from app.models.message import Message
from app.models.user import User
from app.middlewares import jwt_authentication_middleware
from app.serializers.messages.create_message_serializer import CreateMessageSerializer
from app.serializers.messages.get_message_serializer import GetMessageSerializer
from app.services.pagination_service import PaginationService
from fastapi import APIRouter, Depends, HTTPException, status
from app.serializers.users.get_user_serializer import GetUserSerializer

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
    return await Message.objects.create(
        user=current_user,
        chat=chat,
        content=body.content
    )


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def chats_destroy(chat_id: int, id: int, current_user: User = Depends(jwt_authentication_middleware)):
    chat: Chat = await Chat.objects.get_or_none(id=chat_id)
    if chat is None:
        raise HTTPException(detail='Chat is not found', status_code=status.HTTP_404_NOT_FOUND)

    message: Message = await Message.objects.filter(user=current_user).filter(chat=chat).get_or_none(id=id)
    if message is None:
        raise HTTPException(detail='Message is not found', status_code=status.HTTP_404_NOT_FOUND)

    await message.delete()
