from typing import List
from app.models.user import User
from fastapi import APIRouter, Depends, status
from app.middlewares import jwt_authentication_middleware
from app.services.pagination_service import PaginationService
from app.serializers.users.get_user_serializer import GetUserSerializer

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get('/')
async def users_index(page: int = 1, current_user: User = Depends(jwt_authentication_middleware)):
    users: User = User.objects
    users_count: int = await users.count()
    users: List[User] = await users.paginate(page).all()
    return {
        'users': [GetUserSerializer(
            id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            created_at=user.created_at
        ) for user in users],
        'pagination': PaginationService.get_pagination_data(users_count)
    }
