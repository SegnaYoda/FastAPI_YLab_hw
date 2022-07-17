from fastapi import APIRouter, HTTPException, Security, security, Depends
from fastapi.security import HTTPAuthorizationCredentials
from starlette.responses import JSONResponse
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND
from typing import Optional
from src.services.user_services import UserService, get_user_service


from .auth import AuthHandler

from src.api.v1.schemas.users import UserInput, UserLogin, UserView, UserViewShort
from src.models.users import User


user_router = APIRouter()
auth_handler = AuthHandler()


@user_router.post(  # регистрация
    path='/signup',
    status_code=201,
    tags=['users'],
    description='Register new user'
)
def register(
    user: UserInput, user_service: UserService = Depends(get_user_service),
) -> UserInput:
    user_created: dict = user_service.register_service(user=user)
    return {"msg":"User created", "User": UserView(**user_created)}
    


@user_router.post(
    path='/login',
    status_code=200,
    tags=['users']
)
def login(
    user: UserLogin, user_service: UserService = Depends(get_user_service),
) -> UserLogin:
    user = user_service.login_service(user=user)
    return user


@user_router.post(
    path='/refresh',
    status_code=200,
    tags=['users']
)
def refresh(
    user_uuid: User = Depends(auth_handler.auth_current_user_uuid),
    user_service: UserService = Depends(get_user_service)
):
    user_info = user_service.refresh_token(user_uuid=user_uuid)
    return user_info


@user_router.get(
    path='/users/me',
    status_code=200, # добавил
    tags=['users']
)
def get_current_user(
    user_uuid: User = Depends(auth_handler.auth_current_user_uuid),
    user_service: UserService = Depends(get_user_service)
) -> UserView:
    user_info = user_service.get_current_user(user_uuid=user_uuid)
    return UserView(**user_info)


@user_router.get(
    path='/users',
    status_code=200, # добавил
    tags=['users']
)
def get_all_user(
    user_uuid: User = Depends(auth_handler.auth_current_user_uuid),
    user_service: UserService = Depends(get_user_service)
) -> UserView:
    if user_uuid:
        all_user = user_service.select_all_users()
        return {"users": [UserViewShort(**user.dict()) for user in all_user]}


