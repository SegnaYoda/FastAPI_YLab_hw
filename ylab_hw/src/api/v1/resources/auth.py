import datetime
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import jwt
from starlette import status
import uuid


class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=['bcrypt'])
    secret = 'supersecret_ylab_homework'

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, pwd, hashed_pwd):
        return self.pwd_context.verify(pwd, hashed_pwd)

    def encode_token(self, type_token, username, email, is_super,
                            user_uuid, hours, rfrsh_uuid, jti_token):
        payload = {
            'iat': datetime.datetime.utcnow(),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=hours),
            'type': type_token,
            'usrnm': username,
            'email': email,
            'is_super': is_super,
            'user_uuid': user_uuid,
            'jti': jti_token,
            'rfi': rfrsh_uuid,
        }
        return jwt.encode(payload, self.secret, algorithm='HS256')

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            return payload # dict
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Expired signature')
        except jwt.InvalidTokenError or KeyError:
            raise HTTPException(status_code=401, detail='Invalid token')
        
    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)

    def auth_current_user_uuid(self, auth: HTTPAuthorizationCredentials = Security(security)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials.'
        )
        token = auth.credentials
        payload = self.decode_token(token)
        if payload is None:
            raise credentials_exception
        return (payload, token)
    
    def get_a_uuid(self):
        """Выдача uuid."""
        return str(uuid.uuid4())
