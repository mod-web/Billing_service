import json
import pika
from pika.exchange_type import ExchangeType

from config import cfg
from abc_rmq import AbstractRmq


class Rmq(AbstractRmq):
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=cfg.broker.host,
                                      credentials=pika.PlainCredentials(
                                          cfg.broker.login,
                                          cfg.broker.password)))

        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange='email',
                                      exchange_type=ExchangeType.direct)

        self.channel.exchange_declare(exchange='dead_email',
                                      exchange_type=ExchangeType.fanout)

        self.channel.queue_declare(queue='instant_q',
                                   durable=True,
                                   arguments={
                                       'x-dead-letter-exchange': 'dead_email',
                                   })

        self.channel.queue_declare(queue='delayed_q',
                                   durable=True)

        self.channel.queue_declare(queue='dead_q',
                                   durable=True,
                                   arguments={
                                       'x-message-ttl': 60 * 1000,
                                       'x-dead-letter-exchange': 'email',
                                   })

        self.channel.queue_declare(queue='return_q')

        self.channel.queue_bind(exchange='email',
                                queue='instant_q',
                                routing_key='instant')

        self.channel.queue_bind(exchange='email',
                                queue='delayed_q',
                                routing_key='delayed')

        self.channel.queue_bind(exchange='dead_email',
                                queue='dead_q')

        self.channel.basic_consume(
            queue='return_q',
            on_message_callback=self.on_response,
            auto_ack=True)

        # channel.basic_qos(prefetch_count=1)  # only 1 msg for worker until completion

        self.response = None
        self.corr_id = None

    def on_response(self,
                    ch: pika.adapters.blocking_connection.BlockingChannel,
                    method: pika.spec.Basic.Deliver,
                    props: pika.spec.BasicProperties,
                    body: bytes) -> None:
        if self.corr_id == props.correlation_id:
            self.response = body

    def publish(self, routing_key: str, msg: str) -> bytes:
        self.response = None
        self.corr_id = json.loads(msg).get('uuid')
        self.channel.basic_publish(exchange='email',
                                   routing_key=routing_key,
                                   body=msg,
                                   properties=pika.BasicProperties(
                                       delivery_mode=2,  # make message persistent
                                       reply_to='return_q',
                                       correlation_id=self.corr_id
                                   ))

        self.connection.process_data_events(time_limit=None)  # wait for RPC
        return self.response
