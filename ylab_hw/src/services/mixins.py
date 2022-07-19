from sqlmodel import Session

from src.db import AbstractCache, get_cache, get_blocked_access_tkn, get_active_refresh_tkn
from fastapi import Depends
from functools import lru_cache

class PostServiceMixin:
    def __init__(
            self,
            cache: AbstractCache,
            session: Session,
        ):
        self.cache: AbstractCache = cache
        self.session: Session = session


class UserServiceMixin:
    def __init__(
            self,
            session: Session,
        ):
        self.session: Session = session


class CacheServiceMixin:
    def __init__(
            self,
            cache: AbstractCache,
            blocked_access_tkn: AbstractCache,
            active_refresh_tkn: AbstractCache
        ):
        self.cache: AbstractCache = cache
        self.blocked_access_tkn: AbstractCache = blocked_access_tkn
        self.active_refresh_tkn: AbstractCache = active_refresh_tkn
