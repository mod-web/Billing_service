rabbitmq_connection = None
broker = None
postgresql = None


async def get_rabbitmq_connection():
    return rabbitmq_connection


async def get_broker():
    return broker


async def get_postgresql():
    return postgresql