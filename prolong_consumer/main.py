import json
from argparse import ArgumentParser
from confluent_kafka import Consumer, Producer, OFFSET_BEGINNING
from yookassa import Configuration, Payment

import requests


def update_subscription_status(subscribe_id, action):
    params = {
        'action': action
    }
    url = f'http://billing_service:8001/api/v1/subscriptions/{subscribe_id}'
    with requests.Session() as session:
        with session.put(url=url, params=params) as response:
            if response.status_code == 200:
                print(f'Action {action}: {subscribe_id}')
                return response.json()


def acked(err, msg):
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        print("Message produced: %s" % (str(msg)))


def prolong(message):
    subscribe_id = message.key().decode('utf-8')
    payment_data = json.loads(message.value().decode('utf-8'))

    Configuration.account_id = 243091
    Configuration.secret_key = 'test_3SWAMPhw_Q1RcbAjaGY_GQpts4CSQ5D6Txv7ivHpwMg'

    print(payment_data['payment_id'])

    payment = Payment.create({
        "amount": {
            "value": f"{payment_data['price']}.00",
            "currency": "RUB"
        },
        "capture": True,
        "payment_method_id": payment_data['payment_id'],
        "description": "Renew order"
    })

    if payment.status == 'succeeded':
        update_subscription_status(subscribe_id, 'prolong')
    else:
        update_subscription_status(subscribe_id, 'cancel')


if __name__ == '__main__':
    # Parse the command line.
    parser = ArgumentParser()
    parser.add_argument('--reset', action='store_true')
    args = parser.parse_args()

    conf = {'bootstrap.servers': "kafka:29092",
            'group.id': "prolong_consumer",
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
    topic = "prolong-topic"
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
                prolong(msg)

    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        consumer.close()
