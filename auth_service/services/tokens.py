from datetime import timedelta
from functools import wraps
from http import HTTPStatus
from typing import Dict, Tuple, Any
import logging
import redis
from flask import jsonify, abort
from flask_jwt_extended import create_access_token, verify_jwt_in_request, get_jwt
from flask_jwt_extended import create_refresh_token

from auth_config import redis_config

logger = logging.getLogger(__name__)


def admin_access():
    def outer(func):
        @wraps(func)
        def inner(*args, **kwargs):
            verify_jwt_in_request()
            additional_claims = get_jwt()
            if additional_claims['is_admin']:
                return func(*args, **kwargs)
            else:
                return jsonify(msg='Access only for admins'), HTTPStatus.FORBIDDEN

        return inner

    return outer


def create_access_and_refresh_tokens(
        identity: str,
        payload: Dict[str, str],
        seconds: int = 900,
        days: int = 30,
) -> Tuple[str, str]:
    exp_access = timedelta(seconds=seconds)
    exp_refresh = timedelta(days=days)
    logger.debug("Создаем access и refresh токены")
    access_token = create_access_token(
        identity=identity, additional_claims=payload, expires_delta=exp_access)
    refresh_token = create_refresh_token(
        identity=identity, additional_claims=payload, expires_delta=exp_refresh)

    return access_token, refresh_token


class RedisTokenStorage:
    def __init__(self):
        self.redis_host = redis_config.host
        self.redis_port = redis_config.port
        self.jwt_redis_blocklist = redis.StrictRedis(
            host=self.redis_host, port=self.redis_port, db=0, decode_responses=True
        )

    def add_token_to_blacklist(self, token: Dict[str, Any]) -> None:
        jti = token["jti"]
        iat = token.get('iat')
        exp = token.get('exp')
        seconds_till_expire = exp - iat
        self.jwt_redis_blocklist.set(jti, "expired", ex=timedelta(seconds=seconds_till_expire))

    def check_token_in_blacklist(self, token: Dict[str, Any]) -> str | None:
        jti = token["jti"]
        return self.jwt_redis_blocklist.get(jti)


def get_redis_storage():
    return RedisTokenStorage()


def validate_access_token(
        token_store_service: RedisTokenStorage = get_redis_storage(),
):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            token = get_jwt()
            token_in_blacklist = token_store_service.check_token_in_blacklist(token)
            if token_in_blacklist:
                abort(401)
            else:
                return fn(*args, **kwargs)

        return decorator

    return wrapper
