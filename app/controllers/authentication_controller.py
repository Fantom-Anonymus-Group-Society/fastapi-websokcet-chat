from app.models.user import User
from app.configs.environment import env
from asyncpg import UniqueViolationError

from app.serializers.users.get_user_serializer import GetUserSerializer
from app.services.jwt_service import JWTService
from app.services.hasher_service import HasherService
from app.middlewares import jwt_authentication_middleware
from fastapi import APIRouter, Depends, HTTPException, status
from app.serializers.authentication.login_serializer import LoginSerializer
from app.serializers.authentication.registration_serializer import RegistrationSerializer
from app.serializers.authentication.update_profile_serializer import UpdateProfileSerializer

router = APIRouter(
    prefix="/api/auth",
    tags=["authentication"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get("/me", response_model=GetUserSerializer)
async def me(user: User = Depends(jwt_authentication_middleware)) -> GetUserSerializer:
    return GetUserSerializer(
                id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                created_at=user.created_at
            )


@router.patch("/me")
async def update_profile(body: UpdateProfileSerializer, user: User = Depends(jwt_authentication_middleware)) -> User:
    if user.first_name is not None:
        user.first_name = body.first_name
    if user.last_name is not None:
        user.last_name = body.last_name
    if user.username is not None:
        user.username = body.username
    if user.password is not None:
        user.password = HasherService.get_password_hash(body.password)
    return await user.update()


@router.post("/login", status_code=status.HTTP_201_CREATED)
async def login(body: LoginSerializer) -> dict:
    user: User = await User.objects.get_or_none(username=body.username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Incorrect credentials, please try again!")
    if not HasherService.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Incorrect password!")
    return {
        'token': f"Bearer {JWTService.create_token_by_user(user)}"
    }


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegistrationSerializer) -> dict:
    if body.password != body.confirmation:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='password_confirmation_error')
    try:
        user: User = await User.objects.create(
            first_name=body.first_name,
            last_name=body.last_name,
            username=body.username,
            password=HasherService.get_password_hash(body.password),
        )
        response: dict = {
            'user': GetUserSerializer(
                id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                created_at=user.created_at
            ).dict()
        }
        if env.environment == 'local':
            response['token'] = f"Bearer {JWTService.create_token_by_user(user)}"
        return response
    except UniqueViolationError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='User with the same username or email already exists')
