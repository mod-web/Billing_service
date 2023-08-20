from fastapi import APIRouter, Depends


router = APIRouter()


@router.post(
    '/',
    description='Add a new subscriptions',
    summary='Add a new subscriptions',
)
async def publish_notification():
    pass


@router.delete(
    '/{subscriptions_id}',
    description='Cancel a subscriptions',
    summary='Cancel a subscriptions',
)
async def cancel_subscriptions(
    subscriptions_id: str,
):
    pass