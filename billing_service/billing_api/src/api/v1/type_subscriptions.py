import logging
from decimal import Decimal
from sqlalchemy.sql import text
from fastapi import APIRouter, Depends, HTTPException

from src.db.base import get_session
from src.models.models import type_subscribes
from src.services.subscriptions import SubscriptionService, get_subscriptions_service

router = APIRouter()


@router.get(
    '/',
    description='Get all type subscriptions',
    summary='Get all type subscriptions',
)
async def get_type_subscriptions(
    subscription_service: SubscriptionService = Depends(get_subscriptions_service),
) -> list:
    return await subscription_service.get_type_subscriptions()


@router.post(
    '/',
    description='Add a new type subscription',
    summary='Add a new type subscription',
)
async def add_type_subscription(
    name: str,
    price: str,
    period: str,
    subscription_service: SubscriptionService = Depends(get_subscriptions_service),
) -> str:
    return await subscription_service.add_type_subscription(
        name=name,
        price=price,
        period=period,
    )


@router.delete(
    '/{type_subscription_id}',
    description='Delete a subscription',
    summary='Delete a subscription',
)
async def delete_type_subscription(
    type_subscription_id: str,
    subscription_service: SubscriptionService = Depends(get_subscriptions_service),
) -> str:
    return await subscription_service.delete_type_subscription(type_subscription_id)
