from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.sql import text

from src.models.models import user_subscribes
from src.db.base import get_session


router = APIRouter()


@router.get(
    '/',
    description='Get all subscriptions',
    summary='Get all subscriptions',
)
async def get_subscriptions(
    session = Depends(get_session),
) -> list:
    try:
        stmt = text("""SELECT * FROM public.user_subscribes""")
        res = await session.execute(stmt)
        await session.commit()
        return [i._asdict() for i in res.fetchall()]
    except Exception as e:
        print(str(e))


@router.post(
    '/',
    description='Add a new subscription',
    summary='Add a new subscription',
)
async def add_subscription(
    user_id: str,
    type_subscribe_id: str,
    order_id: str | None,
    session = Depends(get_session),
) -> str:
    try:
        res = await session.execute(user_subscribes.insert()
                                    .values(user_id=user_id,
                                            type_subscribe_id=type_subscribe_id,
                                            order_id=order_id))
        await session.commit()
        return str(res.inserted_primary_key[0])
    except Exception as e:
        print(str(e))


@router.delete(
    '/{type_subscriptions_id}',
    description='Delete a subscription',
    summary='Delete a subscription',
)
async def delete_subscription(
    type_subscriptions_id: str,
    session = Depends(get_session),
):
    try:
        await session.execute(
            user_subscribes.delete().where(user_subscribes.c.id == type_subscriptions_id))
        await session.commit()
        return 'deleted'
    except Exception as e:
        print(str(e))