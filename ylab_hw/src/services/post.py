import json
from functools import lru_cache
from typing import Optional

from fastapi import Depends

from sqlmodel import Session

from src.api.v1.schemas import PostCreate, PostModel
from src.db import AbstractCache, get_cache, get_session
from src.models import Post
from src.services import PostServiceMixin


__all__ = ("PostService", "get_post_service")


class PostService(PostServiceMixin):
    """Обработчик запросов по разделу Post."""

    def get_post_list(self) -> dict:
        """Получить список постов."""
        posts = self.session.query(Post).order_by(Post.created_at).all()
        return {"posts": [PostModel(**post.dict()) for post in posts]}

    def get_post_detail(self, post_id: int) -> Optional[dict]:
        """Получить детальную информацию поста."""
        if cached_post := self.cache.get(key=f"{post_id}"):
            return json.loads(cached_post)
        post = self.session.get(Post, post_id)
        if post:
            self.cache.set(key=f"{post.id}", value=post.json())
        return post.dict() if post else None

    def create_post(self, post: PostCreate) -> dict:
        """Создать пост."""
        new_post = Post(title=post.title, description=post.description)
        self.session.add(new_post)
        self.session.commit()
        self.session.refresh(new_post)
        return new_post.dict() if new_post else None

    def update_post_detail(self, post_id, post: PostCreate) -> dict:
        """Редактировать пост."""
        patch_post = self.session.get(Post, post_id)
        patch_data = post.dict(exclude_unset=True)
        for key, value in patch_data.items():
            setattr(patch_post, key, value)
        self.session.add(patch_post)
        self.session.commit()
        self.session.refresh(patch_post)
        self.cache.set(key=f"{patch_post.id}", value=patch_post.json())
        return patch_post if patch_post else None

    def delete_post(self, post_id):
        """Удалить пост."""
        post = self.session.get(Post, post_id)
        if self.cache.get(key=f"{post_id}"):
            self.cache.delete(key=f"{post_id}")
        self.session.delete(post)
        self.session.commit()
        result = "msg: post deleted"
        return result if post else None


# get_post_service — это провайдер PostService. Синглтон
@lru_cache()
def get_post_service(
    cache: AbstractCache = Depends(get_cache),
    session: Session = Depends(get_session),
) -> PostService:
    return PostService(cache=cache, session=session)
