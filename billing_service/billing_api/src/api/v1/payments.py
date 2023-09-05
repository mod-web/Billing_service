import json
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from confluent_kafka import Producer

from src.db.base import get_session
from src.services.kafka import get_kafka
from src.modules.provider.yookassa import Yookassa
from config import settings


router = APIRouter()


@router.post(
    '/',
    description='Order start payment',
    summary='Order start payment',
)
async def start_payment(
        order_id: str,
        session: AsyncSession = Depends(get_session),
        producer: Producer = Depends(get_kafka)
) -> str:
    try:
        stmt = text(f"""SELECT public.type_subscribes.name, public.type_subscribes.price FROM public.orders
                        JOIN public.user_subscribes ON public.orders.id = public.user_subscribes.order_id
                        JOIN public.type_subscribes ON public.user_subscribes.type_subscribe_id =public.type_subscribes.id
                        WHERE public.orders.id = '{order_id}'""")
        res = await session.execute(stmt)
        await session.commit()
        data_subscribe = res.fetchone()
    except Exception as e:
        logging.warning(f'Error: {str(e)}')

    provider = Yookassa(settings.yookassa.account_id, settings.yookassa.secret_key)
    payment = provider.create_payment(order_id, data_subscribe[0], data_subscribe[1])
    confirmation_url = payment.confirmation.confirmation_url

    data_transaction = {'payment_id': payment.id,
                        'status': payment.status,
                        'created_at': payment.created_at}

    statement = text(f"""UPDATE public.orders
                         SET payment_id='{payment.id}', status='pending'
                         WHERE id = '{order_id}';""")

    try:
        await session.execute(statement)
        await session.commit()
    except Exception as e:
        logging.warning(f'Error: {str(e)}')

    def acked(err, msg):
        if err is not None:
            logging.warning(f'Failed to deliver message: {str(msg)}: {str(err)}')
        else:
            logging.info(f'Message produced: {str(msg)}')

    producer.produce('yookassa-log', key=str(payment.id), value=json.dumps(data_transaction), callback=acked)

    producer.poll(1)

    return confirmation_url
