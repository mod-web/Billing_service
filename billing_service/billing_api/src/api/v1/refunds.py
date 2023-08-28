from datetime import datetime, timedelta
from dateutil.relativedelta import *

from fastapi import APIRouter, Depends
from yookassa import Configuration, Refund
from sqlalchemy.sql import text
from src.db.base import get_session
from src.models.models import user_subscribes


router = APIRouter()


@router.post(
    '/',
    description='Create refund for a order',
    summary='Create refund for a order',
)
async def create_refund(
    subscription_id: str,
    session = Depends(get_session)
) -> dict:
    Configuration.account_id = 243091
    Configuration.secret_key = 'test_3SWAMPhw_Q1RcbAjaGY_GQpts4CSQ5D6Txv7ivHpwMg'

    try:
        stmt = text(f"""SELECT period, price, start_active_at, payment_id 
                        FROM public.user_subscribes
                        JOIN public.type_subscribes
                        ON public.user_subscribes.type_subscribe_id = public.type_subscribes.id
                        JOIN public.orders
                        ON public.user_subscribes.order_id = public.orders.id
                        WHERE public.user_subscribes.id = '{subscription_id}'
                        AND active = TRUE""")
        res = await session.execute(stmt)
        await session.commit()

        res = res.fetchone()

        if res is None:
            return {'subscription_id': subscription_id,
                    'active': False,
                    'refund_amount': 0,
                    'status': 'already_refunded'}

        res = res._asdict()

        period = res.get('period')
        price = res.get('price')
        start_active_at = res.get('start_active_at')
        payment_id = res.get('payment_id')

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

        Refund.create({
            "amount": {
                "value": f"{return_price}.00",
                "currency": "RUB"
            },
            "payment_id": f"{payment_id}"
        })

        subscribes_res = await session.execute(user_subscribes.update()
                                          .where(user_subscribes.c.id == subscription_id)
                                          .values(active=False,
                                                  update_at=datetime.now())
                                          .returning(user_subscribes.c.id))
        await session.commit()

        return {'subscription_id': str(subscribes_res.first()[0]),
                'active': False,
                'status': 'refunded',
                'refund_amount': return_price}

    except Exception as e:
        print(str(e))
