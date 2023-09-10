import json
import logging
from datetime import datetime
from decimal import Decimal

import aiohttp
from confluent_kafka import Producer
from fastapi import HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from src.db.base import get_session
from src.models.models import user_subscribes, type_subscribes
from src.modules.query import update_without_renew, get_renew_subscriptions
from src.services.base_service import BaseService
from src.services.kafka import get_kafka


class SubscriptionService(BaseService):
    def __init__(self, session: AsyncSession, producer: Producer) -> None:
        super().__init__(session)
        self.producer = producer

    async def get_subscriptions(self):
        stmt = text("""SELECT * FROM public.user_subscribes""")
        if query_result := await self._execute_stmt(stmt):
            subscriptions = [i._asdict() for i in query_result.fetchall()]
            if not subscriptions:
                raise HTTPException(status_code=404, detail="subscriptions not found")
            return subscriptions
        return []

    async def add_subscription(self, user_id: str, type_subscribe_id: str, order_id: str) -> str:
        try:
            res = await self.session.execute(
                user_subscribes.insert().values(
                    user_id=user_id,
                    type_subscribe_id=type_subscribe_id,
                    order_id=order_id),
            )
            await self.session.commit()
            return str(res.inserted_primary_key[0])
        except Exception as e:
            logging.warning(f'Error: {str(e)}')

    async def update_subscription(self, action: str, subscription_id: str) -> str:
        subscribe_values = {'active': False, 'update_at': datetime.now()}
        if action == 'prolong':
            subscribe_values.update(start_active_at=datetime.now())
        try:
            subscribe_res = await self.session.execute(
                user_subscribes.update().where(
                    user_subscribes.c.id == subscription_id,
                ).values(
                    **subscribe_values
                ).returning(user_subscribes.c.id))
            subscribe_id = str(subscribe_res.first()[0])
            await self.session.commit()
            return subscribe_id
        except Exception as e:
            logging.warning(f'Error: {str(e)}')

    async def delete_subscription(self, subscription_id: str) -> dict[str, str]:
        try:
            await self.session.execute(
                user_subscribes.delete().where(user_subscribes.c.id == subscription_id))
            await self.session.commit()
            return {'detail': 'deleted'}
        except Exception as e:
            logging.warning(f'Error: {str(e)}')
            raise HTTPException(status_code=404, detail="subscription not found")

    async def get_type_subscriptions(self) -> list:
        stmt = text("""SELECT * FROM public.type_subscribes""")
        if query_result := await self._execute_stmt(stmt):
            types = [i._asdict() for i in query_result.fetchall()]
            if not types:
                raise HTTPException(status_code=404, detail="types not found")
            return types
        return []

    async def add_type_subscription(self, name: str, price: str, period: str) -> str:
        try:
            res = await self.session.execute(
                type_subscribes.insert().values(
                    name=name,
                    price=Decimal(price),
                    period=period),
            )
            await self.session.commit()
            return str(res.inserted_primary_key[0])
        except Exception as e:
            logging.warning(f'Error: {str(e)}')

    async def delete_type_subscription(self, type_subscription_id: str) -> str:
        try:
            await self.session.execute(
                type_subscribes.delete().where(type_subscribes.c.id == type_subscription_id))
            await self.session.commit()
            return {'detail': 'deleted'}
        except Exception as e:
            logging.warning(f'Error: {str(e)}')
            raise HTTPException(status_code=404, detail="type not found")

    async def buy_subscription(self, user_id: str, type_subscription_id: str, provider: str) -> str:
        order_params = {
            'user_id': user_id,
            'type_subscribe_id': type_subscription_id,
            'provider': provider,
        }
        order_url = f'http://{settings.billing.host}:{settings.billing.port}/api/v1/orders/'
        async with aiohttp.ClientSession() as s:
            async with s.post(url=order_url, params=order_params) as response:
                if response.status == 200:
                    order_id = await response.json()

        payment_params = {'order_id': order_id}
        payment_url = f'http://{settings.billing.host}:{settings.billing.port}/api/v1/payments/'
        async with aiohttp.ClientSession() as s:
            async with s.post(url=payment_url, params=payment_params) as response:
                if response.status == 200:
                    payment_link = await response.json()
                    return payment_link

    async def change_subscription(self) -> dict:
        query = await update_without_renew()
        stmt = text(query)
        if query_result := await self._execute_stmt(stmt):
            data_subscribe = query_result.fetchall()
            changed = [] if data_subscribe is None else [i[0] for i in data_subscribe]

        query = await get_renew_subscriptions()
        stmt = text(query)
        if query_result := await self._execute_stmt(stmt):
            data_subscribe = query_result.fetchall()
            prolonging_subscriptions = [] if data_subscribe is None else [i._asdict() for i in data_subscribe]

        def acked(err, msg):
            if err is not None:
                logging.warning(f'Failed to deliver message: {str(msg)}: {str(err)}')
            else:
                logging.info(f'Message produced: {str(msg)}')

        for i in prolonging_subscriptions:
            dict_res = {
                'user_id': str(i.get('user_id')),
                'payment_id': str(i.get('payment_id')),
                'price': str(i.get('price'))
            }
            self.producer.produce('prolong-topic', key=str(i.get('subscribe_id')), value=json.dumps(dict_res),
                             callback=acked)
            self.producer.poll(1)

        return {
            'changed': changed,
            'prolonging': prolonging_subscriptions
        }


def get_subscriptions_service(
    session: AsyncSession = Depends(get_session),
    producer: Producer = Depends(get_kafka),
) -> SubscriptionService:
    return SubscriptionService(session, producer)
