from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from src.api.v1.schemas.users import UserInput, UserLogin, UserView, UserViewShort
from src.models.users import User
from src.services.user_services import UserService, get_user_service

from .auth import AuthHandler


user_router = APIRouter()
auth_handler = AuthHandler()


@user_router.post(
    path='/signup',
    status_code=201,
    tags=['users'],
    description='Register new user',
)
def register(
    user_info: UserInput, user_service: UserService = Depends(get_user_service),
) -> UserInput:
    user_created: dict = user_service.register_service(user_info=user_info)
    return {"msg": "User created.", "User": UserView(**user_created)}


@user_router.post(
    path='/login',
    status_code=200,
    tags=['users'],
)
def login(
    user_info: UserLogin, user_service: UserService = Depends(get_user_service),
) -> UserLogin:
    user = user_service.login_service(user_info=user_info)
    return user


@user_router.post(
    path='/refresh',
    status_code=200,
    tags=['users'],
)
def refresh(
    payload_info: User = Depends(auth_handler.auth_current_user_uuid),
    user_service: UserService = Depends(get_user_service),
):
    if user_service.check_refresh_tkn(payload_info):
        user_token = user_service.refresh_token(payload_info)
        return user_token
    else:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="Could not validate user. Login once again or refresh access_token.")


@user_router.get(
    path='/users/me',
    status_code=200,
    tags=['users'],
)
def get_user(
    payload_info: User = Depends(auth_handler.auth_current_user_uuid),
    user_service: UserService = Depends(get_user_service),
) -> UserView:
    user_uuid = payload_info[0]['user_uuid']
    if user_service.check_access_tkn(payload_info[0]['jti']) and payload_info[0]['type'] == "access":
        user_info = user_service.get_current_user(user_uuid=user_uuid)
        return UserView(**user_info)
    else:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="Could not validate user. Login once again or refresh access_token.")


@user_router.patch(
    path='/users/me',
    status_code=200,
    tags=['users'],
)
def patch_user(
    update_data: UserViewShort, payload_info: User = Depends(auth_handler.auth_current_user_uuid),
    user_service: UserService = Depends(get_user_service),
) -> UserView:
    if user_service.check_access_tkn(payload_info[0]['jti']) and payload_info[0]['type'] == "access":
        user_update, access_token = user_service.patch_current_user(payload_info, update_data=update_data)
        return {"msg": "Update is successfull. Please use new access token",
                "user": user_update,
                "access_token": access_token}
    else:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="Could not validate user. Login once again or refresh access_token.")


@user_router.delete(
    path="/users/me",
    summary="Удалить пользователя.",
    tags=["users"],
)
def delete_user(
    payload_info: User = Depends(auth_handler.auth_current_user_uuid),
    user_service: UserService = Depends(get_user_service),
) -> UserView:
    if user_service.check_access_tkn(payload_info[0]['jti']) and payload_info[0]['type'] == "access":
        user_uuid = payload_info[0]['user_uuid']
        user_info = user_service.delete_current_user(user_uuid=user_uuid, payload_info=payload_info)
        return user_info
    else:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="Could not validate user. Login once again or refresh access_token.")


@user_router.get(
    path='/users',
    status_code=200,
    tags=['users'],
)
def get_all_users(
    payload_info: User = Depends(auth_handler.auth_current_user_uuid),
    user_service: UserService = Depends(get_user_service),
) -> UserView:
    if user_service.check_access_tkn(payload_info[0]['jti']) and payload_info[0]['type'] == "access":
        all_user = user_service.select_all_users()
        return {"users": [UserView(**user.dict()) for user in all_user]}
    else:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="Could not validate user. Login once again or refresh access_token.")


@user_router.post(
    path='/logout',
    status_code=200,
    tags=['users'],
)
def logout(
    payload_info: User = Depends(auth_handler.auth_current_user_uuid),
    user_service: UserService = Depends(get_user_service),
):
    if user_service.check_access_tkn(payload_info[0]['jti']):
        if user_service.logout(payload_info):
            return {"msg": "You have been logged out."}
    else:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="Could not validate user. Login once again or refresh access_token.")


@user_router.post(
    path='/logout_all',
    status_code=200,
    tags=['users'],
)
def logout_all(
    payload_info: User = Depends(auth_handler.auth_current_user_uuid),
    user_service: UserService = Depends(get_user_service),
):
    if user_service.check_access_tkn(payload_info[0]['jti']):
        if user_service.logout_all(payload_info):
            return {"msg": "You have been logged out from all devices."}
    else:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="Could not validate user. Login once again or refresh access_token.")
