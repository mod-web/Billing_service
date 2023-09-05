from fastapi import APIRouter
from pydantic.schema import Optional, List
from datetime import datetime
from src.models.base import AbstractModel

router = APIRouter()


class Orders(AbstractModel):
    user_id: str
    payment_id: str
    renew: Optional[bool] = False
    status: Optional[str] = None
    created_at: datetime
    update_at: datetime
