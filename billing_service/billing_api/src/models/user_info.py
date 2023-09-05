from fastapi import APIRouter
from pydantic.schema import Optional, List
from datetime import datetime
from src.models.base import AbstractModel

router = APIRouter()


class UserInfo(AbstractModel):
    user_id: str
    login: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
