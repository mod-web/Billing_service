import json
import logging
from argparse import ArgumentParser
from confluent_kafka import Consumer, OFFSET_BEGINNING
import requests

from provider.yookassa import Yookassa
from config import cfg


logging.basicConfig(level=logging.INFO)


def update_subscription_status(subscribe_id, action):
    params = {
        'action': action
    }
    url = f'http://{cfg.billing.host}:{cfg.billing.port}/api/v1/subscriptions/{subscribe_id}'
    with requests.Session() as session:
        with session.put(url=url, params=params) as response:
            if response.status_code == 200:
                logging.info(f'Action {action}: {subscribe_id}')
                return response.json()


def acked(err, msg):
    if err is not None:
        logging.warning(f'Failed to deliver message: {str(msg)}: {str(err)}')
    else:
        logging.info(f'Message produced: {str(msg)}')


def prolong(message):
    subscribe_id = message.key().decode('utf-8')
    payment_data = json.loads(message.value().decode('utf-8'))

    logging.info(f"try prolong {payment_data['payment_id']}")

    provider = Yookassa(cfg.yookassa.account_id, cfg.yookassa.secret_key)
    payment = provider.prolong_payment(payment_data['payment_id'], payment_data['price'])

    if payment.status == 'succeeded':
        update_subscription_status(subscribe_id, 'prolong')
    else:
        update_subscription_status(subscribe_id, 'cancel')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--reset', action='store_true')
    args = parser.parse_args()

    conf = {'bootstrap.servers': "kafka:29092",
            'group.id': "prolong_consumer",
            'auto.offset.reset': 'smallest'}

    consumer = Consumer(conf)

    def reset_offset(cons, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            cons.assign(partitions)
        logging.info('Reset complete')

    topic = "prolong-topic"
    consumer.subscribe([topic], on_assign=reset_offset)

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                pass
            elif msg.error():
                logging.warning("ERROR: %s".format(msg.error()))
            else:
                prolong(msg)

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
