import logging
from datetime import datetime

import aiohttp
from fastapi import Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from src.db.base import get_session
from src.models.models import orders, user_subscribes
from src.services.base_service import BaseService


class OrdersService(BaseService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_orders(self) -> list:
        stmt = text("""SELECT * FROM public.orders""")
        if query_result := await self._execute_stmt(stmt=stmt):
            orders = [i._asdict() for i in query_result.fetchall()]
            if not orders:
                raise HTTPException(status_code=404, detail="orders not found")
            return orders
        return []


    async def create_no_active_subscription(self, user_id: str, type_subscribe_id: str, order_id: str) -> None:
        """ Создание неактивной подписки """

        params = {'user_id': user_id,
                  'type_subscribe_id': type_subscribe_id,
                  'order_id': order_id}
        url = f'http://{settings.billing.host}:{settings.billing.port}/api/v1/subscriptions/'

        async with aiohttp.ClientSession() as s:
            async with s.post(url=url, params=params) as response:
                if response.status == 200:
                    await response.json()


    async def place_new_order(self, user_id: str, type_subscribe_id: str, provider: str) -> str:
        """ Создание заказа и неактивной подписки """

        try:
            res = await self.session.execute(orders.insert().values(user_id=user_id, status='created', provider=provider))
            await self.session.commit()

            order_id = str(res.inserted_primary_key[0])
            await self.create_no_active_subscription(user_id, type_subscribe_id, order_id)

            return order_id
        except Exception as e:
            logging.warning(f'Error: {str(e)}')


    async def change_status(self, payment_id: str, status: str, renew: bool) -> str:
        try:
            order_res = await self.session.execute(
                orders.update().where(
                    orders.c.payment_id == payment_id,
                ).values(
                    status=status,
                    renew=renew,
                    update_at=datetime.now(),
                ).returning(orders.c.id))
            order_id = str(order_res.first()[0])
            await self.session.commit()

            if status == 'succeeded':
                subscribe_res = await self.session.execute(
                    user_subscribes.update().where(
                        user_subscribes.c.order_id == order_id,
                    ).values(
                        active=True,
                        start_active_at=datetime.now(),
                        update_at=datetime.now(),
                    ).returning(user_subscribes.c.id))
                subscribe_id = str(subscribe_res.first()[0])
                await self.session.commit()
                return f'order status changed: {order_id} and active new subscribe: {subscribe_id}'
            else:
                return f'order status canceled: {order_id}'
        except Exception as e:
            logging.warning(f'Error: {str(e)}')

    async def delete_order(self, order_id: str) -> str:
        try:
            await self.session.execute(
                orders.delete().where(orders.c.id == order_id))
            await self.session.commit()
            return {'detail': 'deleted'}
        except Exception as e:
            logging.warning(f'Error: {str(e)}')
            raise HTTPException(status_code=404, detail="order not found")


def get_orders_service(
    session: AsyncSession = Depends(get_session),
) -> OrdersService:
    return OrdersService(session)
