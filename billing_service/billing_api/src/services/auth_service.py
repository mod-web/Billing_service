from typing import Dict, Any
import aiohttp as aiohttp

from config import settings


async def get_user_info(group_name: str) -> Dict[str, Any]:
    params = {'group_name': group_name}
    url = f'{settings.auth_service_url}/user-info'
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, params=params) as response:
            if response.status == 200:
                return await response.json()
