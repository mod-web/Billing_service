import json

import aiohttp as aiohttp
from fastapi import APIRouter, Depends
from sqlalchemy.sql import text

from src.db.base import get_session
from src.modules.query import update_without_renew, get_renew_subscriptions
from src.services.kafka import get_kafka


router = APIRouter()


@router.post(
    '/buy',
    description='Buy a new subscription',
    summary='Buy a new subscription',
)
async def buy_subscription(
    user_id: str,
    type_subscription_id: str
) -> str:
    order_params = {'user_id': user_id,
                    'type_subscribe_id': type_subscription_id}
    order_url = f'http://billing_service:8001/api/v1/orders/'
    async with aiohttp.ClientSession() as s:
        async with s.post(url=order_url, params=order_params) as response:
            if response.status == 200:
                order_id = await response.json()

    payment_params = {'order_id': order_id}
    payment_url = f'http://billing_service:8001/api/v1/payments/'
    async with aiohttp.ClientSession() as s:
        async with s.post(url=payment_url, params=payment_params) as response:
            if response.status == 200:
                payment_link = await response.json()

    return payment_link


@router.put(
    '/change',
    description='Disable expired subscription & renew',
    summary='Disable expired subscription & renew',
)
async def change_subscription(
    session = Depends(get_session),
    producer = Depends(get_kafka)
) -> dict:
    try:
        query = await update_without_renew()
        stmt = text(query)
        res = await session.execute(stmt)
        await session.commit()
        data_subscribe = res.fetchall()
        changed = [] if data_subscribe is None else [i[0] for i in data_subscribe]
    except Exception as e:
        print(str(e))

    try:
        query = await get_renew_subscriptions()
        stmt = text(query)
        res = await session.execute(stmt)
        await session.commit()
        data_subscribe = res.fetchall()

        prolonging_subscriptions = [] if data_subscribe is None else \
                                   [i._asdict() for i in data_subscribe]
    except Exception as e:
        print(str(e))

    def acked(err, msg):
        if err is not None:
            print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
        else:
            print("Message produced: %s" % (str(msg)))

    for i in prolonging_subscriptions:
        dict_res = {
            'user_id': str(i.get('user_id')),
            'payment_id': str(i.get('payment_id')),
            'price': str(i.get('price'))
        }
        producer.produce('prolong-topic', key=str(i.get('subscribe_id')), value=json.dumps(dict_res), callback=acked)
        producer.poll(1)

    return {
        'changed': changed,
        'prolonging': prolonging_subscriptions
    }