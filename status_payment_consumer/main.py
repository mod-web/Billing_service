from argparse import ArgumentParser
from confluent_kafka import Consumer, Producer, OFFSET_BEGINNING


def acked(err, msg):
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        print("Message produced: %s" % (str(msg)))


def status_payment(message):
    payment_id = message.key().decode('utf-8')
    payment_status = message.value().decode('utf-8')

    if payment_status == 'succeeded':
        print(f'Payment change: {payment_id} - {payment_status}!')
    elif payment_status == 'canceled':
        print(f'Payment change: {payment_id} - {payment_status}!')


if __name__ == '__main__':
    # Parse the command line.
    parser = ArgumentParser()
    parser.add_argument('--reset', action='store_true')
    args = parser.parse_args()

    conf = {'bootstrap.servers': "kafka:29092",
            'group.id': "status_payment_consumer",
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
    topic = "ready-topic"
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
                status_payment(msg)

    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        consumer.close()
