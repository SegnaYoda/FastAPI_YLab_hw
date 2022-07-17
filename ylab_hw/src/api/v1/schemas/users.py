from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel


class UserViewShort(SQLModel):
    uuid: str
    username: str
    email: str


class UserView(UserViewShort):
    created_at: datetime
    is_superuser: bool = False


class UserInput(SQLModel):
    username: str
    password: str = Field(max_length=256, min_length=6)
    # password2: str
    email: str

    # @validator('password2')
    # def password_match(cls, v, values, **kwargs):
    #     if 'password' in values and v != values['password']:
    #         raise ValueError('passwords don\'t match')
    #     return v


class UserLogin(SQLModel):
    username: str
    password: str
