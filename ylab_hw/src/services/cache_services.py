import datetime
import json
from functools import lru_cache

from fastapi import Depends

from src.db import AbstractCache, get_active_refresh_tkn, get_blocked_access_tkn, get_cache
from src.services.mixins import CacheServiceMixin


class CacheRedisService(CacheServiceMixin):
    """Обработчик для запросов в Redis."""

    hours_refresh_tkn = 1

    def get_user_from_cache_db0(self, user_uuid):
        """Получить из основной redis пользователя по uuid."""
        cached_user = self.cache.get(key=f"{user_uuid}")
        return cached_user

    def set_user_to_cache_db0(self, user):
        """Записать пользователя в redis по ключу uuid."""
        self.cache.set(key=f"{user.uuid}", value=user.json())
        return True

    def delete_user_from_cache_db0(self, user_uuid):
        """Удалить пользователя из redis по uuid."""
        if self.cache.get(key=f"{user_uuid}"):
            self.cache.delete(key=f"{user_uuid}")
            return True

    def add_access_token_to_cache(self, id_token, token, hours_exp_tkn):
        """Добавить access token в основной кеш."""
        self.cache.set(key=f"{id_token}", value=f"{token}", expire=(3600 * hours_exp_tkn))
        return True

    def delete_access_tkn_permission(self, payload_info):
        """Удаление access token из основного кеша и добавление его в блеклист."""
        payload = payload_info[0]
        token = payload_info[1]
        jti_token = payload['jti']
        hours_access_tkn = payload['exp']
        if self.cache.get(key=f"{jti_token}"):
            hours_access_tkn = datetime.datetime.fromtimestamp(int(hours_access_tkn))
            expired_time = hours_access_tkn - datetime.datetime.utcnow()
            self.cache.delete(key=f"{jti_token}")
            self.blocked_access_tkn.set(key=f"{jti_token}", value=f"{token}", expire=(2 * expired_time))
            return True

    def cache_active_refresh_tkn_list(self, user_uuid, refresh_token, hours_refresh_tkn):
        """Добавить refresh token к списку разрешенных refresh токенов пользователя."""
        self.hours_refresh_tkn = hours_refresh_tkn
        if list_tkn := self.active_refresh_tkn.get(key=f"{user_uuid}"):
            list_tkn = json.loads(list_tkn)
            list_tkn.append(refresh_token)
            self.active_refresh_tkn.set(key=f"{user_uuid}",
                                        value=json.dumps(list_tkn), expire=(3600 * hours_refresh_tkn))
            return True
        else:
            list_tkn = []
            list_tkn.append(refresh_token)
            self.active_refresh_tkn.set(key=f"{user_uuid}", value=json.dumps(list_tkn),
                                        expire=(3600 * hours_refresh_tkn))
            return True

    def delete_refresh_tkn_from_list(self, user_uuid, oldtoken, rfi=False):
        """Удалить конкретный refresh_токен из разершенных в списке пользователя."""
        hours_refresh_tkn = self.hours_refresh_tkn
        if list_tkn := self.active_refresh_tkn.get(key=f"{user_uuid}"):
            list_tkn = json.loads(list_tkn)
            if oldtoken in list_tkn:
                list_tkn.remove(oldtoken)
                self.active_refresh_tkn.set(key=f"{user_uuid}", value=json.dumps(list_tkn),
                                            expire=(3600 * hours_refresh_tkn))
        if rfi:
            self.cache.delete(key=f"{rfi}")
        return True

    def delete_all_refresh_tkn(self, user_uuid):
        """Удалить все активные refresh_token для определенного пользователя."""
        if self.active_refresh_tkn.get(key=f"{user_uuid}"):
            self.active_refresh_tkn.delete(key=f"{user_uuid}")
            return True

    def check_access_tkn_in_cache(self, id_token):
        """Проверить наличие access токена в базе данных."""
        if token := self.cache.get(key=f"{id_token}"):
            return token

    def check_access_tkn_in_blacklist(self, jti_token):
        """Проверить наличие access токена в blacklist."""
        if self.blocked_access_tkn.get(key=f"{jti_token}"):
            return True

    def check_refresh_tkn_in_cache(self, user_uuid, token):
        """Проверить наличие refresh токена в списке разрешенных для обновления."""
        if list_tkn := self.active_refresh_tkn.get(key=f"{user_uuid}"):
            list_tkn = json.loads(list_tkn)
            if str(token) in list_tkn:
                return True


@lru_cache
def get_cache_service(
    cache: AbstractCache = Depends(get_cache),
    blocked_access_tkn: AbstractCache = Depends(get_blocked_access_tkn),
    active_refresh_tkn: AbstractCache = Depends(get_active_refresh_tkn),
) -> CacheRedisService:
    return CacheRedisService(cache, blocked_access_tkn, active_refresh_tkn)
