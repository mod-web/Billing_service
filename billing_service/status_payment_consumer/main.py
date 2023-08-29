import json
import logging
from argparse import ArgumentParser
from confluent_kafka import Consumer, OFFSET_BEGINNING
import requests


logging.basicConfig(level=logging.INFO)


def change_status_order(payment_id, params):
    url = f'http://billing_api:8001/api/v1/orders/{payment_id}'
    with requests.Session() as session:
        with session.put(url=url, params=params) as response:
            if response.status_code == 200:
                logging.info(f'Payment change: {payment_id} - {params["status"]}!')
                return response.json()


def acked(err, msg):
    if err is not None:
        logging.warning(f'Failed to deliver message: {str(msg)}: {str(err)}')
    else:
        logging.info(f'Message produced: {str(msg)}')


def status_payment(message):
    payment_id = message.key().decode('utf-8')
    payment_data = json.loads(message.value().decode('utf-8'))
    change_status_order(payment_id, payment_data)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--reset', action='store_true')
    args = parser.parse_args()

    conf = {'bootstrap.servers': "kafka:29092",
            'group.id': "status_payment_consumer",
            'auto.offset.reset': 'smallest'}

    consumer = Consumer(conf)

    def reset_offset(cons, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            cons.assign(partitions)
        logging.info('Reset complete')

    topic = "ready-topic"
    consumer.subscribe([topic], on_assign=reset_offset)

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                pass
            elif msg.error():
                logging.warning("ERROR: %s".format(msg.error()))
            else:
                status_payment(msg)

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
