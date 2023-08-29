import json

from fastapi import APIRouter, Depends

from src.services.auth_service import get_user_info
from src.services.broker import RabbitmqBroker
from src.services.utils import get_broker

router = APIRouter()


@router.post(
    '/delayed',
    description='Publish delayed notification to broker',
    summary='Publish delayed notification to broker',
)
async def publish_notification(
    uuid: str,
    group_name: str,
    template: str,
    type_: str,
    title: str,
    hours_from: str,
    hours_to: str,
    broker: RabbitmqBroker = Depends(get_broker),
):
    users = await get_user_info(group_name=group_name)
    for timezone, users in users.items():
        body = {
            'uuid': uuid,
            'type_sender': type_,
            'timezone': timezone,
            'time_from': hours_from,
            'time_to': hours_to,
            'template_id': template,
            'subject': title,
            'data': users
        }
        await broker.publish_to_broker(routing_key='delayed', msg=json.dumps(body))
