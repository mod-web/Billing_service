import logging
from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.base import get_session
from src.models.models import user_subscribes, type_subscribes


class SubscriptionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_subscriptions(self):
        try:
            stmt = text("""SELECT * FROM public.user_subscribes""")
            res = await self.session.execute(stmt)
            await self.session.commit()
        except Exception as e:
            logging.warning(f'Error: {str(e)}')
        finally:
            subscriptions = [i._asdict() for i in res.fetchall()]
            if not subscriptions:
                raise HTTPException(status_code=404, detail="subscriptions not found")
            return subscriptions

    async def add_subscription(self, user_id: str, type_subscribe_id: str, order_id: str) -> str:
        try:
            res = await self.session.execute(
                user_subscribes.insert().values(
                    user_id=user_id,
                    type_subscribe_id=type_subscribe_id,
                    order_id=order_id),
            )
            await self.session.commit()
            return str(res.inserted_primary_key[0])
        except Exception as e:
            logging.warning(f'Error: {str(e)}')

    async def update_subscription(self, action: str, subscription_id: str) -> str:
        if action == 'cancel':
            try:
                subscribe_res = await self.session.execute(
                    user_subscribes.update().where(
                        user_subscribes.c.id == subscription_id,
                    ).values(
                        active=False,
                        update_at=datetime.now(),
                    ).returning(user_subscribes.c.id))
                subscribe_id = str(subscribe_res.first()[0])
                await self.session.commit()
                return subscribe_id
            except Exception as e:
                logging.warning(f'Error: {str(e)}')

        elif action == 'prolong':
            try:
                subscribe_res = await self.session.execute(
                    user_subscribes.update().where(
                        user_subscribes.c.id == subscription_id,
                    ).values(
                        active=True,
                        start_active_at=datetime.now(),
                        update_at=datetime.now(),
                    ).returning(user_subscribes.c.id))
                subscribe_id = str(subscribe_res.first()[0])
                await self.session.commit()
                return subscribe_id
            except Exception as e:
                logging.warning(f'Error: {str(e)}')

    async def delete_subscription(self, subscription_id: str) -> dict[str, str]:
        try:
            await self.session.execute(
                user_subscribes.delete().where(user_subscribes.c.id == subscription_id))
            await self.session.commit()
            return {'detail': 'deleted'}
        except Exception as e:
            logging.warning(f'Error: {str(e)}')
            raise HTTPException(status_code=404, detail="subscription not found")

    async def get_type_subscriptions(self) -> list:
        try:
            stmt = text("""SELECT * FROM public.type_subscribes""")
            res = await self.session.execute(stmt)
            await self.session.commit()
        except Exception as e:
            logging.warning(f'Error: {str(e)}')
        finally:
            types = [i._asdict() for i in res.fetchall()]
            if not types:
                raise HTTPException(status_code=404, detail="types not found")
            return types

    async def add_type_subscription(self, name: str, price: str, period: str) -> str:
        try:
            res = await self.session.execute(
                type_subscribes.insert().values(
                    name=name,
                    price=Decimal(price),
                    period=period),
            )
            await self.session.commit()
            return str(res.inserted_primary_key[0])
        except Exception as e:
            logging.warning(f'Error: {str(e)}')

    async def delete_type_subscription(self, type_subscription_id: str) -> str:
        try:
            await self.session.execute(
                type_subscribes.delete().where(type_subscribes.c.id == type_subscription_id))
            await self.session.commit()
            return {'detail': 'deleted'}
        except Exception as e:
            logging.warning(f'Error: {str(e)}')
            raise HTTPException(status_code=404, detail="type not found")


def get_subscriptions_service(
        session: AsyncSession = Depends(get_session),
) -> SubscriptionService:
    return SubscriptionService(session)
