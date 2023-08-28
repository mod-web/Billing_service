from datetime import datetime
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


@router.put(
    '/{subscription_id}',
    description='Update a subscription',
    summary='Update a subscription',
)
async def update_subscription(
    action: str,
    subscription_id: str,
    session = Depends(get_session),
):
    if action == 'cancel':
        try:
            subscribe_res = await session.execute(user_subscribes.update()
                                                  .where(user_subscribes.c.id == subscription_id)
                                                  .values(active=False,
                                                          update_at=datetime.now())
                                                  .returning(user_subscribes.c.id))
            subscribe_id = str(subscribe_res.first()[0])
            await session.commit()
            return subscribe_id
        except Exception as e:
            print(str(e))

    elif action == 'prolong':
        try:
            subscribe_res = await session.execute(user_subscribes.update()
                                                  .where(user_subscribes.c.id == subscription_id)
                                                  .values(active=True,
                                                          start_active_at=datetime.now(),
                                                          update_at=datetime.now())
                                                  .returning(user_subscribes.c.id))
            subscribe_id = str(subscribe_res.first()[0])
            await session.commit()
            return subscribe_id
        except Exception as e:
            print(str(e))


@router.delete(
    '/{subscription_id}',
    description='Delete a subscription',
    summary='Delete a subscription',
)
async def delete_subscription(
    subscription_id: str,
    session = Depends(get_session),
):
    try:
        await session.execute(
            user_subscribes.delete().where(user_subscribes.c.id == subscription_id))
        await session.commit()
        return 'deleted'
    except Exception as e:
        print(str(e))
