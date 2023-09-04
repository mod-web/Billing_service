import json
import logging
from argparse import ArgumentParser
import time
from confluent_kafka import Consumer, Producer, OFFSET_BEGINNING
import socket

from provider.yookassa import Yookassa
from config import cfg


logging.basicConfig(level=logging.INFO)


def acked(err, msg):
    if err is not None:
        logging.warning(f'Failed to deliver message: {str(msg)}: {str(err)}')
    else:
        logging.info(f'Message produced: {str(msg)}')


def check_payment(message):
    payment_id = message.key().decode('utf-8')
    provider = Yookassa(cfg.yookassa.account_id, cfg.yookassa.secret_key)
    payment = provider.check_payment(payment_id)

    config = {'bootstrap.servers': f'{cfg.kafka.host}:{cfg.kafka.port}',
              'client.id': socket.gethostname()}
    producer = Producer(config)

    if payment.status == 'pending':
        time.sleep(5)
        producer.produce(message.topic(), key=message.key(), value=message.value(), callback=acked)
        producer.poll(10)
    else:
        renew = payment.payment_method.saved

        res = {'status': payment.status,
               'renew': renew}

        res = json.dumps(res)

        producer.produce('ready-topic', key=message.key(), value=res, callback=acked)
        producer.poll(1)
        logging.info(f'Payment: {payment_id} - {payment.status}! -> ready-topic')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--reset', action='store_true')
    args = parser.parse_args()

    conf = {'bootstrap.servers': "kafka:29092",
            'group.id': "check_payment_consumer",
            'auto.offset.reset': 'smallest'}

    consumer = Consumer(conf)

    def reset_offset(cons, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            cons.assign(partitions)
        logging.info('Reset complete')

    topic = "yookassa-log"
    consumer.subscribe([topic], on_assign=reset_offset)

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                pass
            elif msg.error():
                logging.warning(f"ERROR: {msg.error()}")
            else:
                check_payment(msg)

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
