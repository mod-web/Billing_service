import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
import aiohttp as aiohttp

from src.models.models import orders, user_subscribes
from src.db.base import get_session
from config import settings
from src.services.orders import get_orders_service, OrdersService

router = APIRouter()


@router.get(
    '/',
    description='Get all orders',
    summary='Get all orders',
)
async def get_orders(
    orders_service: OrdersService = Depends(get_orders_service),
) -> list:
    return await orders_service.get_orders()


@router.post(
    '/',
    summary='Add a new order',
    description='user_id: 5a146f79-cf46-4c7e-ab09-e0e172a5c32e',
)
async def new_order(
    user_id: str,
    type_subscribe_id: str,
    orders_service: OrdersService = Depends(get_orders_service),
) -> str:
    return await orders_service.place_new_order(user_id,type_subscribe_id)


@router.put(
    "/{payment_id}",
    summary='Change status a order',
    description='Change status a order',
)
async def change_status(
    payment_id: str,
    status: str,
    renew: bool,
    orders_service: OrdersService = Depends(get_orders_service),
) -> str:
    return await orders_service.change_status(payment_id, status, renew)


@router.delete(
    '/{order_id}',
    description='Delete a order',
    summary='Delete a order',
)
async def delete_order(
    order_id: str,
    orders_service: OrdersService = Depends(get_orders_service),
) -> str:
    return await orders_service.delete_order(order_id)
