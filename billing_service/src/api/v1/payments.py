from yookassa import Configuration, Payment
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.sql import text

from src.db.base import get_session
from src.models.models import orders


router = APIRouter()


@router.post(
    '/',
    description='Order start payment',
    summary='Order start payment',
)
async def start_payment(
        order_id: str,
        session = Depends(get_session),
):
    Configuration.account_id = 243091
    Configuration.secret_key = 'test_3SWAMPhw_Q1RcbAjaGY_GQpts4CSQ5D6Txv7ivHpwMg'

    payment = Payment.create({
        "amount": {
            "value": "100.00",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://www.example.com/return_url"
        },
        "capture": True,
        "description": "Заказ №1"
    }, order_id)

    confirmation_url = payment.confirmation.confirmation_url
    print(payment.id)
    print(payment.status)
    print(payment.created_at)
    print(payment.amount.value)


    statement = text(f"""UPDATE public.orders
                         SET payment_id='{payment.id}', status='pending'
                         WHERE id = '{order_id}';""")

    try:
        await session.execute(statement)
        await session.commit()
    except Exception as e:
        print(str(e))



    # from confluent_kafka import Producer
    # import socket
    #
    # conf = {'bootstrap.servers': "kafka:29092",
    #         'client.id': socket.gethostname()}
    #
    # producer = Producer(conf)



    return confirmation_url
