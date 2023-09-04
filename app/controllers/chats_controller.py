import ormar
from typing import List
from app.models.chat import Chat
from app.models.user import User
from app.middlewares import jwt_authentication_middleware
from app.services.pagination_service import PaginationService
from fastapi import APIRouter, Depends, HTTPException, status
from app.serializers.chats.get_chat_serializer import GetChatSerializer
from app.serializers.users.get_user_serializer import GetUserSerializer
from app.serializers.chats.create_chat_serializer import CreateChatSerializer

router = APIRouter(
    prefix="/api/chats",
    tags=["chats"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get('/')
async def chats_index(page: int = 1, current_user: User = Depends(jwt_authentication_middleware)) -> dict:
    chats: Chat = Chat.objects.get_chat_list(current_user)
    chats_count: int = await chats.count()
    chats: List[Chat] = await chats.select_related(['sender', 'receiver']).order_by('-created_at').paginate(page=page).all()

    return {
        'chats': [GetChatSerializer(
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
        ) for chat in chats],
        'pagination': PaginationService.get_pagination_data(chats_count)
    }


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=GetChatSerializer)
async def chats_store(body: CreateChatSerializer, current_user: User = Depends(jwt_authentication_middleware)):
    receiver: User = await User.objects.get_or_none(id=body.receiver_id)
    if receiver is None:
        raise HTTPException(detail='Receiver is not found', status_code=status.HTTP_404_NOT_FOUND)
    existing_chat: Chat | None = await Chat.objects.get_if_exists(current_user, receiver)
    if existing_chat is not None:
        return existing_chat
    return await Chat.objects.create(
        sender=current_user,
        receiver=receiver
    )


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

    await chat.delete()
