from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from src.api.v1.schemas import PostCreate, PostListResponse, PostModel
from src.models.users import User
from src.services.post import PostService, get_post_service
from src.services.user_services import UserService, get_user_service

from .auth import AuthHandler


router = APIRouter()
auth_handler = AuthHandler()


@router.get(
    path="/",
    response_model=PostListResponse,
    summary="Список постов",
    tags=["posts"],
)
def post_list(
    post_service: PostService = Depends(get_post_service),
) -> PostListResponse:
    posts: dict = post_service.get_post_list()
    if not posts:
        # Если посты не найдены, отдаём 404 статус
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Posts not found.")
    return PostListResponse(**posts)


@router.get(
    path="/{post_id}",
    response_model=PostModel,
    summary="Получить определенный пост",
    tags=["posts"],
)
def post_detail(
    post_id: int, post_service: PostService = Depends(get_post_service),
) -> PostModel:
    post: Optional[dict] = post_service.get_post_detail(post_id)
    if not post:
        # Если пост не найден, отдаём 404 статус
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Post not found.")
    return PostModel(**post)


@router.patch(
    path="/{post_id}",
    summary="Редактировать определенный пост.",
    tags=["posts"],
)
def patch_post_detail(
    post_id: int, post: PostCreate, post_service: PostService = Depends(get_post_service),
    payload_info: User = Depends(auth_handler.auth_current_user_uuid),
    user_checker: UserService = Depends(get_user_service),
) -> PostCreate:
    if user_checker.check_access_tkn(payload_info[0]['jti']) and payload_info[0]['type'] == "access":
        patch_post: Optional[dict] = post_service.update_post_detail(post_id, post)
        if not patch_post:
            raise HTTPException(HTTPStatus.NOT_FOUND, detail="Post not found.")
        return {"msg": "Post updated.", "Updated post": patch_post}
    else:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="Could not validate user. Login once again or refresh access_token.")


@router.post(
    path="/",
    response_model=PostModel,
    status_code=201,
    summary="Создать пост",
    tags=["posts"],
)
def post_create(
    post: PostCreate, post_service: PostService = Depends(get_post_service),
    payload_info: User = Depends(auth_handler.auth_current_user_uuid),
    user_checker: UserService = Depends(get_user_service),
) -> PostCreate:
    if user_checker.check_access_tkn(payload_info[0]['jti']) and payload_info[0]['type'] == "access":
        post: dict = post_service.create_post(post=post)
        return PostModel(**post)
    else:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="Could not validate user. Login once again or refresh access_token.")


@router.delete(
    path="/{post_id}",
    summary="Удалить определенный пост",
    tags=["posts"],
)
def post_delete(
    post_id: int, post_service: PostService = Depends(get_post_service),
    payload_info: User = Depends(auth_handler.auth_current_user_uuid),
    user_checker: UserService = Depends(get_user_service),
) -> PostCreate:
    if user_checker.check_access_tkn(payload_info[0]['jti']) and payload_info[0]['type'] == "access":
        result = post_service.delete_post(post_id=post_id)
        if not result:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Post not found.")
        return result
    else:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="Could not validate user. Login once again or refresh access_token.")
