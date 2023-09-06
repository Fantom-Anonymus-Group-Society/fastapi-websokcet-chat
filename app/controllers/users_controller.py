from typing import List
from app.models.user import User
from fastapi import APIRouter, Depends, status
from app.middlewares import jwt_authentication_middleware
from app.serializers.users.get_user_serializer import GetUserSerializer

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get('/', response_model=List[GetUserSerializer])
async def users_index(current_user: User = Depends(jwt_authentication_middleware)):
    return await User.objects.exclude(id=current_user.id).all()
