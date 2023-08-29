import json
from datetime import datetime

from celery import shared_task
from celery.utils.log import get_task_logger
from django_celery_beat.models import CrontabSchedule

from scheduler.app_p.models import Notification
from scheduler.app_p.service import NotificationService

logger = get_task_logger(__name__)


@shared_task
def task_send_group_message(**kwargs):
    date_to_send = datetime.strptime(kwargs.get('date_to_send'), "YYYY-MM-DD")
    schedule_delay = CrontabSchedule.objects.get_or_create(
        day_of_month=f"{date_to_send.day}",
        month_of_year=f"{date_to_send.month}")
    Notification.objects.update_or_create(
        name=f'{kwargs["task_name"]}_delayed',
        default={
            'enabled': True,
            'crontab': schedule_delay if kwargs.get("notification_type") == "scheduled" else None,
            'task': 'scheduler.tasks.send_delayed_message',
            'kwargs': json.dumps(
                {'uuid': kwargs["uuid"],
                 'title': kwargs["title"],
                 'template_id': kwargs["template_id"],
                 'task_name': kwargs["task_name"],
                 'group': kwargs["group"],
                 'time_from': kwargs["time_from"],
                 'time_to': kwargs["time_to"],
                 'type_sender': kwargs["type_sender"]}
            ),
        }
    )


@shared_task
def send_delayed_message(**kwargs):
    notify_service = NotificationService()
    notify_service.send_info_json_to_notification(**kwargs)
