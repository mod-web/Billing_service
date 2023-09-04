from confluent_kafka import Producer
import socket

from config import settings


async def get_kafka():
    conf = {'bootstrap.servers': f'{settings.kafka.host}:{settings.kafka.port}',
            'client.id': socket.gethostname()}
    producer = Producer(conf)
    return producer
