import logging
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.sql import text
import aiohttp as aiohttp

from src.models.models import orders, user_subscribes
from src.db.base import get_session


router = APIRouter()


@router.get(
    '/',
    description='Get all orders',
    summary='Get all orders',
)
async def get_orders(
    session = Depends(get_session),
) -> list:
    try:
        stmt = text("""SELECT * FROM public.orders""")
        res = await session.execute(stmt)
        await session.commit()
        return [i._asdict() for i in res.fetchall()]
    except Exception as e:
        logging.warning(f'Error: {str(e)}')


@router.post(
    '/',
    summary='Add a new order',
    description='user_id: 5a146f79-cf46-4c7e-ab09-e0e172a5c32e',
)
async def new_order(
    user_id: str,
    type_subscribe_id: str,
    session = Depends(get_session),
) -> str:
    try:
        res = await session.execute(orders.insert().values(user_id=user_id, status='created'))
        await session.commit()

        params = {'user_id': user_id,
                  'type_subscribe_id': type_subscribe_id,
                  'order_id': str(res.inserted_primary_key[0])}
        url = f'http://billing_api:8001/api/v1/subscriptions/'

        async with aiohttp.ClientSession() as s:
            async with s.post(url=url, params=params) as response:
                if response.status == 200:
                    await response.json()

        return str(res.inserted_primary_key[0])
    except Exception as e:
        logging.warning(f'Error: {str(e)}')


@router.put(
    "/{payment_id}",
    summary='Change status a order',
    description='Change status a order',
)
async def change_status(
    payment_id: str,
    status: str,
    renew: bool,
    session = Depends(get_session),
) -> str:
    try:
        order_res = await session.execute(orders.update()
                                               .where(orders.c.payment_id == payment_id)
                                               .values(status=status,
                                                       renew=renew,
                                                       update_at=datetime.now())
                                               .returning(orders.c.id))
        order_id = str(order_res.first()[0])
        await session.commit()

        if status == 'succeeded':
            subscribe_res = await session.execute(user_subscribes.update()
                                                       .where(user_subscribes.c.order_id == order_id)
                                                       .values(active=True,
                                                               start_active_at=datetime.now(),
                                                               update_at=datetime.now())
                                                       .returning(user_subscribes.c.id))
            subscribe_id = str(subscribe_res.first()[0])
            await session.commit()
            return f'order status changed: {order_id} and active new subscribe: {subscribe_id}'
        else:
            return f'order status canceled: {order_id}'
    except Exception as e:
        logging.warning(f'Error: {str(e)}')


@router.delete(
    '/{order_id}',
    description='Delete a order',
    summary='Delete a order',
)
async def delete_order(
    order_id: str,
    session = Depends(get_session),
):
    try:
        await session.execute(
            orders.delete().where(orders.c.id == order_id))
        await session.commit()
        return 'deleted'
    except Exception as e:
        logging.warning(f'Error: {str(e)}')