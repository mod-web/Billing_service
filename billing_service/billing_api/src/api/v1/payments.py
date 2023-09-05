from fastapi import APIRouter, Depends

from src.modules.provider.yookassa import Yookassa
from src.services.payments import get_payments_service, PaymentsService

router = APIRouter()


@router.post(
    '/',
    description='Order start payment',
    summary='Order start payment',
)
async def start_payment(
    order_id: str,
    provider: str,
    payments_service: PaymentsService = Depends(get_payments_service),
) -> str:
    match provider:
        case 'yookassa':
            pvd = Yookassa()
        case _:
            return {'status': 'provider is not supported'}

    await payments_service.start_payment(order_id=order_id, provider=pvd)
