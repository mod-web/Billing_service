import json

from yookassa import Configuration, Payment
from fastapi import APIRouter, Depends
from sqlalchemy.sql import text

from src.db.base import get_session
from src.services.kafka import get_kafka


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

    try:
        stmt = text(f"""SELECT public.type_subscribes.name, public.type_subscribes.price FROM public.orders
                        JOIN public.user_subscribes ON public.orders.id = public.user_subscribes.order_id
                        JOIN public.type_subscribes ON public.user_subscribes.type_subscribe_id =public.type_subscribes.id
                        WHERE public.orders.id = '{order_id}'""")
        res = await session.execute(stmt)
        await session.commit()
        data_subscribe = res.fetchone()
    except Exception as e:
        print(str(e))

    payment = Payment.create({
        "amount": {
            "value": f"{data_subscribe[1]}",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://www.example.com/return_url"
        },
        "capture": True,
        "description": f'Order "{data_subscribe[0]} - {int(data_subscribe[1])} RUB"'
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
