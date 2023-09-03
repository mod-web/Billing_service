import requests
from celery import Celery
from celery import shared_task
from celery.schedules import crontab

from config import settings


celery = Celery(__name__)
celery.conf.broker_url = f"redis://{settings.redis.host}:{settings.redis.port}"
celery.conf.result_backend = f"redis://{settings.redis.host}:{settings.redis.port}"
celery.conf.beat_schedule = {
    'add-every-day': {
        'task': 'worker.cancel_prolong',
        'schedule': crontab(minute=0, hour=6), # every day at 6AM
        # 'schedule': 10, # For test every 10 sec
        # 'args': (1, 1), # For test
    }
}


@shared_task
def cancel_prolong():
    params = {}
    url = f'http://{settings.billing.host}:{settings.billing.port}/api/v1/actions/change'

    with requests.Session() as session:
        with session.put(url=url, params=params) as response:
            if response.status_code == 200:
                return response.json()
