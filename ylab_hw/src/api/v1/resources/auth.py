import datetime

from fastapi import Security, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from passlib.context import CryptContext
import jwt
from starlette import status

from sqlmodel import Session
from src.db import get_session
from src.models.users import User


class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=['bcrypt'])
    secret = 'supersecret_ylab_homework'

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, pwd, hashed_pwd):
        return self.pwd_context.verify(pwd, hashed_pwd)

    def encode_token(self, username, uuid, hours):
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours),
            'iat': datetime.datetime.utcnow(),
            'sub': username,
            'uuid': uuid
        }
        return jwt.encode(payload, self.secret, algorithm='HS256')

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            return payload['uuid']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Expired signature')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token')

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)

    def auth_current_user_uuid(self, auth: HTTPAuthorizationCredentials = Security(security)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials'
        )
        user_uuid = self.decode_token(auth.credentials)
        if user_uuid is None:
            raise credentials_exception
        return user_uuid
        # # user = find_user(username)      # подправить
        # session: Session = Depends(get_session)
        # user = session.query(User).filter(User.username == username).first()
        # # ___
        # if user is None:
        #     raise credentials_exception
        # return user