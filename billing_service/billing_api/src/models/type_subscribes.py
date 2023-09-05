from fastapi import APIRouter
from pydantic.schema import Optional, List
from datetime import datetime
from src.models.base import AbstractModel

router = APIRouter()


class TypeSubscribes(AbstractModel):
    name: str
    price: float
    period: str
