import aiohttp as aiohttp


async def change_status_order(payment_id):
    params = {'group_name': 'okok'}
    url = 'billing_api:8001/user-info'
    async with aiohttp.ClientSession() as session:
        async with session.put(url=url, params=params) as response:
            if response.status == 200:
                return await response.json()