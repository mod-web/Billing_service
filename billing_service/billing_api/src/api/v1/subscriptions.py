from fastapi import APIRouter, Depends

from src.services.subscriptions import get_subscriptions_service, SubscriptionService

router = APIRouter()


@router.get(
    '/',
    description='Get all subscriptions',
    summary='Get all subscriptions',
)
async def get_subscriptions(
    subscription_service: SubscriptionService = Depends(get_subscriptions_service),
) -> list:
    return await subscription_service.get_subscriptions()


@router.post(
    '/',
    description='Add a new subscription',
    summary='Add a new subscription',
)
async def add_subscription(
    user_id: str,
    type_subscribe_id: str,
    order_id: str | None,
    subscription_service: SubscriptionService = Depends(get_subscriptions_service),
) -> str:
    return await subscription_service.add_subscription(
        user_id=user_id,
        type_subscribe_id=type_subscribe_id,
        order_id=order_id,
    )


@router.put(
    '/{subscription_id}',
    description='Update a subscription',
    summary='Update a subscription',
)
async def update_subscription(
    action: str,
    subscription_id: str,
    subscription_service: SubscriptionService = Depends(get_subscriptions_service),
) -> str:
    return await subscription_service.update_subscription(
        action=action,
        subscription_id=subscription_id,
    )


@router.delete(
    '/{subscription_id}',
    description='Delete a subscription',
    summary='Delete a subscription',
)
async def delete_subscription(
    subscription_id: str,
    subscription_service: SubscriptionService = Depends(get_subscriptions_service),
) -> dict[str, str]:
    return await subscription_service.delete_subscription(subscription_id)
