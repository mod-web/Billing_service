import uuid
from datetime import datetime

from sqlalchemy import MetaData, Table, Column, String, DateTime, UUID, Boolean, Enum, ForeignKey, DECIMAL


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
    Column('renew', Boolean, default=False),
    Column('status', String),
    Column('created_at', DateTime, default=datetime.now()),
    Column('update_at', DateTime, default=datetime.now()),
)

user_subscribes = Table(
    'user_subscribes',
    metadata,
    Column('id',
           UUID(as_uuid=True),
           primary_key=True,
           default=uuid.uuid4,
           unique=True),
    Column('user_id',
           UUID(as_uuid=True),
           nullable=False),
    Column('type_subscribe_id',
           UUID(as_uuid=True),
           ForeignKey('type_subscribes.id',
                      ondelete='CASCADE'),
           nullable=False,
           index=True),
    Column('order_id',
           UUID(as_uuid=True),
           ForeignKey('orders.id'),
           index=True),
    Column('active', Boolean, default=False),
    Column('start_active_at', DateTime, default=datetime.now()),
    Column('created_at', DateTime, default=datetime.now()),
    Column('update_at', DateTime, default=datetime.now()),
)

type_subscribes = Table(
    'type_subscribes',
    metadata,
    Column('id',
           UUID(as_uuid=True),
           primary_key=True,
           default=uuid.uuid4,
           unique=True),
    Column('name',
           String),
    Column('price',
           DECIMAL),
    Column('period',
           Enum(
               '1mon',
               '3mon',
               '6mon',
               '12mon',
               name='periodTypes'))
)

user_info = Table(
    'user_info',
    metadata,
    Column('id',
           UUID(as_uuid=True),
           primary_key=True,
           default=uuid.uuid4,
           unique=True),
    Column('user_id',
           UUID(as_uuid=True),
           nullable=False),
    Column('login',
           String),
    Column('first_name',
           String),
    Column('last_name',
           String),
)