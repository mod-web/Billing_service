from fastapi import APIRouter, Depends

from src.services.subscriptions import SubscriptionService, get_subscriptions_service

router = APIRouter()


@router.post(
    '/buy',
    description='user_id: 5a146f79-cf46-4c7e-ab09-e0e172a5c32e\n'
                'provider: yookassa',
    summary='Buy a new subscription',
)
async def buy_subscription(
    user_id: str,
    type_subscription_id: str,
    provider: str,
    subscription_service: SubscriptionService = Depends(get_subscriptions_service),
) -> str:
    return await subscription_service.buy_subscription(user_id, type_subscription_id, provider)


@router.put(
    '/change',
    description='Disable expired subscription & renew',
    summary='Disable expired subscription & renew',
)
async def change_subscription(
    subscription_service: SubscriptionService = Depends(get_subscriptions_service),
) -> dict:
    return await subscription_service.change_subscription()
