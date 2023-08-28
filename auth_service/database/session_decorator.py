from datetime import datetime
from functools import wraps
from http import HTTPStatus

import redis as redis
from flask import request, jsonify
from sqlalchemy.orm import Session

from auth_config import redis_config, RATE_LIMIT_COUNT

redis_conn = redis.Redis(host=redis_config.host, port=redis_config.port, db=0)


def get_session():
    def wrapper(func):
        def inner(self, *args, **kwargs):
            with Session(self.engine) as session:
                return func(self, *args, **kwargs, session=session)

        return inner

    return wrapper


def rate_limit():
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            pipe = redis_conn.pipeline()
            now = datetime.now()
            key = f'{request.remote_addr}:{now.minute}'
            pipe.incr(key, 1)
            pipe.expire(key, 59)
            result = pipe.execute()
            request_number = result[0]
            if request_number > RATE_LIMIT_COUNT:
                return jsonify({'error': 'Too many requests'}), HTTPStatus.TOO_MANY_REQUESTS
            return func(*args, **kwargs)
        return inner
    return wrapper
