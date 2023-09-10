import json
import logging

from confluent_kafka import Producer
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.base import get_session
from src.modules.provider.abc_provider import Provider
from src.services.base_service import BaseService
from src.services.kafka import get_kafka


class PaymentsService(BaseService):
    def __init__(self, session: AsyncSession, producer: Producer) -> None:
        super().__init__(session)
        self.producer = producer

    async def __get_data_subscribe(self, order_id: str):
        stmt = text(f"""SELECT public.type_subscribes.name, public.type_subscribes.price FROM public.orders
                                    JOIN public.user_subscribes ON public.orders.id = public.user_subscribes.order_id
                                    JOIN public.type_subscribes ON public.user_subscribes.type_subscribe_id =public.type_subscribes.id
                                    WHERE public.orders.id = '{order_id}'""")
        if query_result := await self._execute_stmt(stmt):
            return query_result.fetchone()

    async def __deliver_message(self, payment, order_id: str) -> None:
        data_transaction = {'payment_id': payment.id,
                            'status': payment.status,
                            'created_at': payment.created_at}

        statement = text(f"""UPDATE public.orders
                             SET payment_id='{payment.id}', status='pending'
                             WHERE id = '{order_id}';""")

        try:
            await self.session.execute(statement)
            await self.session.commit()
        except Exception as e:
            logging.warning(f'Error: {str(e)}')

        def acked(err, msg):
            if err is not None:
                logging.warning(f'Failed to deliver message: {str(msg)}: {str(err)}')
            else:
                logging.info(f'Message produced: {str(msg)}')

        self.producer.produce('yookassa-log', key=str(payment.id), value=json.dumps(data_transaction), callback=acked)
        self.producer.poll(1)

    async def start_payment(self, order_id: str, provider: Provider) -> str:
        confirmation_url = ''
        if data_subscribe := await self.__get_data_subscribe(order_id):

            payment = provider.create_payment(order_id, data_subscribe[0], data_subscribe[1])
            confirmation_url = payment.confirmation.confirmation_url

            await self.__deliver_message(order_id=order_id, payment=payment)

        return confirmation_url


def get_payments_service(
    session: AsyncSession = Depends(get_session),
    producer: Producer = Depends(get_kafka),
) -> PaymentsService:
    return PaymentsService(session, producer)
