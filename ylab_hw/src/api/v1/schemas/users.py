from datetime import datetime

from sqlmodel import Field
from pydantic import BaseModel


__all__ = (
    "UserViewShort",
    "UserView",
    "UserInput",
    "UserLogin",
)


class UserViewShort(BaseModel):
    username: str
    email: str


class UserView(UserViewShort):
    uuid: str
    created_at: datetime
    is_superuser: bool = False


class UserInput(BaseModel):
    """Валидация для повторного ввода пароля по умолчанию не включена."""
    username: str
    password: str = Field(max_length=256, min_length=6)
    email: str
    # password2: str

    # @validator('password2')
    # def password_match(cls, v, values, **kwargs):
    #     if 'password' in values and v != values['password']:
    #         raise ValueError('passwords don\'t match')
    #     return v


class UserLogin(BaseModel):
    username: str
    password: str
