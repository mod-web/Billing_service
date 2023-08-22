import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.sql import text

from src.models.models import orders
from src.db.base import get_session


router = APIRouter()


@router.post(
    '/',
    summary='New order creation',
    description='user_id: 5a146f79-cf46-4c7e-ab09-e0e172a5c32e',
)
async def new_order(
    user_id: str,
    session = Depends(get_session),
) -> str:
    order_id = uuid.uuid4()
    # statement = text(f"""INSERT INTO public.orders (id, user_id, status) VALUES ('{order_id}', '{user_id}', 'panding')""")
    try:
        await session.execute(orders.insert().values(id=order_id, user_id=user_id, status='created'))
        await session.commit()
    except Exception as e:
        print(str(e))
    return str(order_id)


@router.put(
    "/{item_id}",
    responses={403: {"description": "Operation forbidden"}},
)
async def new_order(
    item_id: str,
    status: str,
    session = Depends(get_session),
) -> str:

    statement = text(f"""UPDATE public.orders
                         SET status='{status}'
                         WHERE payment_id='{item_id}';""")
    try:
        await session.execute(statement)
        await session.commit()
    except Exception as e:
        print(str(e))

    if status == 'succeeded':
        print('hhhh', status)
        print('wwww', item_id)
    elif status == 'canceled':
        pass
    return 'status changed'