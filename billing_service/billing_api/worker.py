import requests

from celery import Celery
from celery import shared_task
from celery.schedules import crontab


celery = Celery(__name__)
celery.conf.broker_url = "redis://redis:6379"
celery.conf.result_backend = "redis://redis:6379"
celery.conf.beat_schedule = {
    'add-every-day': {
        'task': 'worker.cancel_prolong',
    'schedule': crontab(minute=0, hour=6),
        # 'schedule': 10, # For test
        # 'args': (1, 1), # For test
    }
}


@shared_task
def cancel_prolong():
    params = {}
    url = f'http://billing_api:8001/api/v1/actions/change'

    with requests.Session() as session:
        with session.put(url=url, params=params) as response:
            if response.status_code == 200:
                return response.json()
