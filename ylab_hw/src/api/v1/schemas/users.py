from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel

__all__ = (
    "UserViewShort",
    "UserView",
    "UserInput",
    "UserLogin",
)


class UserViewShort(SQLModel):
    username: str
    email: str


class UserView(UserViewShort):
    uuid: str
    created_at: datetime
    is_superuser: bool = False


class UserInput(SQLModel):
    username: str
    password: str = Field(max_length=256, min_length=6)
    email: str
    
    # password2: str

    # @validator('password2')
    # def password_match(cls, v, values, **kwargs):
    #     if 'password' in values and v != values['password']:
    #         raise ValueError('passwords don\'t match')
    #     return v


class UserLogin(SQLModel):
    username: str
    password: str