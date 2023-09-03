rabbitmq_connection = None
broker = None


async def get_rabbitmq_connection():
    return rabbitmq_connection


async def get_broker():
    return broker
