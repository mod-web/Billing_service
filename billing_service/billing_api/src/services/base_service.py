import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.services import AbstractService


class BaseService(AbstractService):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __execute_stmt(self, stmt: str):
        try:
            res = await self.session.execute(stmt)
            await self.session.commit()
        except Exception as e:
            logging.warning(f'Error: {str(e)}')
            return None
        return res
