import uuid
from datetime import datetime

from sqlalchemy import MetaData, Table, Column, String, DateTime, UUID


metadata = MetaData()

orders = Table(
    'orders',
    metadata,
    Column('id',
           UUID(as_uuid=True),
           primary_key=True,
           default=uuid.uuid4,
           unique=True),
    Column('user_id',
           UUID(as_uuid=True),
           nullable=False),
    Column('payment_id',
           UUID(as_uuid=True),
           nullable=True),
    Column('status', String),
    Column('created_at', DateTime, default=datetime.now()),
    Column('update_at', DateTime, default=datetime.now()),
)