import json
from argparse import ArgumentParser
import time

from confluent_kafka import Consumer, Producer, OFFSET_BEGINNING
from yookassa import Configuration, Payment
import socket


def acked(err, msg):
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        print("Message produced: %s" % (str(msg)))


def check_payment(message):
    Configuration.account_id = 243091
    Configuration.secret_key = 'test_3SWAMPhw_Q1RcbAjaGY_GQpts4CSQ5D6Txv7ivHpwMg'

    payment_id = message.key().decode('utf-8')
    payment = Payment.find_one(payment_id)

    config = {'bootstrap.servers': "kafka:29092",
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
        print(f'Payment: {payment_id} - {payment.status}! -> ready-topic')


if __name__ == '__main__':
    # Parse the command line.
    parser = ArgumentParser()
    parser.add_argument('--reset', action='store_true')
    args = parser.parse_args()

    conf = {'bootstrap.servers': "kafka:29092",
            'group.id': "check_payment_consumer",
            'auto.offset.reset': 'smallest'}

    # Create Consumer instance
    consumer = Consumer(conf)

    # Set up a callback to handle the '--reset' flag.
    def reset_offset(cons, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            cons.assign(partitions)
        print('Reset complete')

    # Subscribe to topic
    topic = "yookassa-log"
    consumer.subscribe([topic], on_assign=reset_offset)

    # Poll for new messages from Kafka and print them.
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                # Initial message consumption may take up to
                # `session.timeout.ms` for the consumer group to
                # rebalance and start consuming
                pass
                # print("Waiting...")
            elif msg.error():
                print("ERROR: %s".format(msg.error()))
            else:
                # Extract the (optional) key and value, and print.
                check_payment(msg)

    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        consumer.close()
