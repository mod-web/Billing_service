import aiohttp as aiohttp
from fastapi import APIRouter


router = APIRouter()


@router.post(
    '/',
    description='Buy a new subscription',
    summary='Buy a new subscription',
)
async def buy_subscription(
    user_id: str,
    type_subscription_id: str
):
    order_params = {'user_id': user_id,
              'type_subscribe_id': type_subscription_id}
    order_url = f'http://billing_service:8001/api/v1/orders/'
    async with aiohttp.ClientSession() as s:
        async with s.post(url=order_url, params=order_params) as response:
            if response.status == 200:
                order_id = await response.json()

    payment_params = {'order_id': order_id}
    payment_url = f'http://billing_service:8001/api/v1/payments/'
    async with aiohttp.ClientSession() as s:
        async with s.post(url=payment_url, params=payment_params) as response:
            if response.status == 200:
                payment_link = await response.json()

    return payment_link

