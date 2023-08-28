from confluent_kafka import Producer
import socket

async def get_kafka():
    conf = {'bootstrap.servers': "kafka:29092",
            'client.id': socket.gethostname()}
    producer = Producer(conf)
    return producer