import json

from yookassa import Configuration, Payment
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.sql import text

from src.db.base import get_session
from src.services.kafka import get_kafka
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
        producer = Depends(get_kafka)
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
        print(str(e))

    def acked(err, msg):
        if err is not None:
            print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
        else:
            print("Message produced: %s" % (str(msg)))

    producer.produce('yookassa-log', key=str(payment.id), value=json.dumps(data_transaction), callback=acked)

    producer.poll(1)

    return confirmation_url
