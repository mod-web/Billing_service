import aio_pika
import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from config import settings
from src.api.v1 import notifications
from src.services import utils
from src.services.broker import RabbitmqBroker

app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


app.include_router(notifications.router, prefix='/api/v1/notifications', tags=['notifications'])


@app.get('/')
async def status():
    return {'status': 'OK'}


@app.on_event('startup')
async def startup():
    url = f'amqp://{settings.broker.login}:{settings.broker.password}@{settings.broker.host}/'
    utils.rabbitmq_connection = await aio_pika.connect(url=url)
    utils.broker = await RabbitmqBroker().configure()


@app.on_event('shutdown')
async def shutdown():
    await utils.rabbitmq_connection.close()


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
    )
