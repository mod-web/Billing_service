import json
import logging
from datetime import datetime

from confluent_kafka import Producer
from dateutil.relativedelta import relativedelta
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.base import get_session
from src.models.models import user_subscribes
from src.modules.provider.yookassa import Yookassa
from src.services.kafka import get_kafka


class RefundsService:
    def __init__(self, session: AsyncSession, producer: Producer) -> None:
        self.session = session
        self.producer = producer

    async def __get_subscription(self, subscription_id: str):
        stmt = text(f"""SELECT period, price, start_active_at, payment_id, provider
                        FROM public.user_subscribes
                        JOIN public.type_subscribes
                        ON public.user_subscribes.type_subscribe_id = public.type_subscribes.id
                        JOIN public.orders
                        ON public.user_subscribes.order_id = public.orders.id
                        WHERE public.user_subscribes.id = '{subscription_id}'
                        AND active = TRUE""")
        res = await self.session.execute(stmt)
        await self.session.commit()

        return res.fetchone()

    async def create_refund(self, subscription_id: str) -> dict:
        subscription = await self.__get_subscription(subscription_id)
        if subscription is None:
            return {'subscription_id': subscription_id,
                    'active': False,
                    'refund_amount': 0,
                    'status': 'already_refunded'}

        subscription = subscription._asdict()

        period = subscription.get('period')
        price = subscription.get('price')
        start_active_at = subscription.get('start_active_at')
        payment_id = subscription.get('payment_id')
        provider = subscription.get('provider')

        match period:
            case '1mon':
                num = 1
            case '3mon':
                num = 3
            case '6mon':
                num = 6
            case '12mon':
                num = 12

        date_fire = start_active_at + relativedelta(months=+num)
        all_day = date_fire - start_active_at
        day_not_spend = date_fire - datetime.now()
        price_per_day = int(price) / int(all_day.days)
        return_price = round(int(day_not_spend.days) * price_per_day)

        match provider:
            case 'yookassa':
                pvd = Yookassa()
            case _:
                return {'status': 'provider is no longer supported'}

        pvd.refund_payment(payment_id, return_price)

        subscribes_res = await self.session.execute(
            user_subscribes.update().where(
                user_subscribes.c.id == subscription_id,
            ).values(
                active=False,
                update_at=datetime.now(),
            ).returning(user_subscribes.c.id))
        await self.session.commit()

        return {'subscription_id': str(subscribes_res.first()[0]),
                'active': False,
                'status': 'refunded',
                'refund_amount': return_price}


def get_refunds_service(
    session: AsyncSession = Depends(get_session),
    producer: Producer = Depends(get_kafka),
) -> RefundsService:
    return RefundsService(session, producer)
