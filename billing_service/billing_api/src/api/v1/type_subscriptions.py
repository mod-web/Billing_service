from decimal import Decimal
from sqlalchemy.sql import text
from fastapi import APIRouter, Depends

from src.db.base import get_session
from src.models.models import type_subscribes


router = APIRouter()


@router.get(
    '/',
    description='Get all type subscriptions',
    summary='Get all type subscriptions',
)
async def get_type_subscriptions(
    session = Depends(get_session),
) -> list:
    try:
        stmt = text("""SELECT * FROM public.type_subscribes""")
        res = await session.execute(stmt)
        await session.commit()
        return [i._asdict() for i in res.fetchall()]
    except Exception as e:
        print(str(e))


@router.post(
    '/',
    description='Add a new type subscription',
    summary='Add a new type subscription',
)
async def add_type_subscription(
    name: str,
    price: str,
    period: str,
    session = Depends(get_session),
):
    try:
        res = await session.execute(type_subscribes.insert()
                              .values(name=name, price=Decimal(price), period=period))
        await session.commit()
        return str(res.inserted_primary_key[0])
    except Exception as e:
        print(str(e))


@router.delete(
    '/{type_subscription_id}',
    description='Delete a subscription',
    summary='Delete a subscription',
)
async def delete_type_subscription(
    type_subscription_id: str,
    session = Depends(get_session),
):
    try:
        await session.execute(
            type_subscribes.delete().where(type_subscribes.c.id == type_subscription_id))
        await session.commit()
        return 'deleted'
    except Exception as e:
        print(str(e))
