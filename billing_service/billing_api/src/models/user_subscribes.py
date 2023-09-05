from fastapi import APIRouter
from pydantic.schema import Optional, List
from datetime import datetime
from src.models.base import AbstractModel

router = APIRouter()


class UserSubscribes(AbstractModel):
    user_id: str
    type_subscribe_id: str
    order_id: str
    active: bool = False
    start_active_at: datetime
    created_at: datetime
    update_at: datetime
