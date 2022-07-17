from datetime import datetime
from typing import Optional

from pydantic import validator, EmailStr
from sqlmodel import SQLModel, Field, Relationship
import uuid

__all__ = ("User",)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(default=str(uuid.uuid4()))
    username: str = Field(index=True)
    password: str = Field(max_length=256, min_length=6)
    email: str = Field()
    created_at: datetime = Field(default=datetime.utcnow(), nullable=False)
    is_superuser: bool = False
