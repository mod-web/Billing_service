from fastapi import APIRouter, Depends

from src.services.refunds import RefundsService, get_refunds_service

router = APIRouter()


@router.post(
    '/',
    description='Create refund for a order',
    summary='Create refund for a order',
)
async def create_refund(
    subscription_id: str,
    refunds_service: RefundsService = Depends(get_refunds_service),
) -> dict:
    return await refunds_service.create_refund(subscription_id)
