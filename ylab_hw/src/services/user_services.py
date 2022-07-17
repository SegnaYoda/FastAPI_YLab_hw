import json
from sqlmodel import Session, select
from functools import lru_cache
from src.db.db import engine
from src.models.users import User
from src.services.mixins import ServiceMixin
from src.db import AbstractCache, get_cache, get_session
from typing import Optional
from fastapi import HTTPException, Security, security, Depends
from starlette.responses import JSONResponse
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND

from src.api.v1.schemas.users import UserInput, UserLogin
from src.models.users import User

from src.api.v1.resources.auth import AuthHandler



class UserService(ServiceMixin):

    auth_handler = AuthHandler()

    def register_service(self, user: UserInput):
        "Регистрация."
        users = self.select_all_users()
        if any(x.username == user.username for x in users):
            raise HTTPException(status_code=400, detail='Username is taken')
        hashed_pwd = self.auth_handler.get_password_hash(user.password)
        u = User(username=user.username, password=hashed_pwd, email=user.email)
        self.session.add(u)
        self.session.commit()
        user_created = self.find_user(user.username)
        return user_created

    def login_service(self, user: UserLogin):
        user_found = self.find_user(user.username)
        if not user_found:
            raise HTTPException(status_code=401, detail='Invalid username and/or password')
        verified = self.auth_handler.verify_password(user.password, user_found['password'])
        if not verified:
            raise HTTPException(status_code=401, detail='Invalid username and/or password')
        access_token = self.auth_handler.encode_token(user_found['username'], user_found['uuid'], hours=1)
        refresh_token = self.auth_handler.encode_token(user_found['username'], user_found['uuid'], hours=48)
        return {'access_token': access_token, "refresh_token": refresh_token}


    def refresh_token(self, user_uuid):
        credentials_exception = HTTPException(
            status_code=401,
            detail='Refresh - Could not validate credentials'
        )
        if user_uuid is None:
            raise credentials_exception
        user_found = self.session.query(User).filter(User.uuid == user_uuid).first()
        user_found = user_found.dict()
        access_token = self.auth_handler.encode_token(user_found['username'], user_found['uuid'], hours=1)
        refresh_token = self.auth_handler.encode_token(user_found['username'], user_found['uuid'], hours=48)
        return {'access_token': access_token, "refresh_token": refresh_token}


    def get_current_user(self, user_uuid):
        credentials_exception = HTTPException(
            status_code=401,
            detail='Could not validate credentials'
        )
        if user_uuid is None:
            raise credentials_exception
        if cached_user := self.cache.get(key=f"{user_uuid}"):
            return json.loads(cached_user)
        user = self.session.query(User).filter(User.uuid == user_uuid).first()
        if user:
            self.cache.set(key=f"{user.uuid}", value=user.json())
        # return user.dict() if user else None
        return user.dict() if user else None

    def select_all_users(self):
        all_users = self.session.query(User).order_by(User.created_at).all()
        return all_users


    def find_user(self, username: str) -> Optional[dict]:
        # with Session(engine) as session:
            # statement = select(User).where(User.username == name)
            # return session.exec(statement).first()

        if cached_user := self.cache.get(key=f"{username}"):
            return json.loads(cached_user)

        user = self.session.query(User).filter(User.username == username).first()
        if user:
            self.cache.set(key=f"{user.username}", value=user.json())
        # return user.dict() if user else None
        return user.dict() if user else None


# get_post_service — это провайдер PostService. Синглтон
@lru_cache()
def get_user_service(
    cache: AbstractCache = Depends(get_cache),
    session: Session = Depends(get_session),
) -> UserService:
    return UserService(cache=cache, session=session)