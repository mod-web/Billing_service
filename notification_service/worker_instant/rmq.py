import json
import pika
from pika.exchange_type import ExchangeType
import logging

from send.email import send_email
from config import cfg
from abc_rmq import AbstractRmq


logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


class Rmq(AbstractRmq):
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=cfg.broker.host,
                                      credentials=pika.PlainCredentials(
                                          cfg.broker.login,
                                          cfg.broker.password)))

        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange='email',
                                      exchange_type=ExchangeType.direct)  # depend on routing_key

        self.channel.exchange_declare(exchange='dead_email',
                                      exchange_type=ExchangeType.fanout)  # not depend on routing_key

        self.channel.queue_declare(queue='instant_q',
                                   durable=True,
                                   arguments={
                                       'x-dead-letter-exchange': 'dead_email',  # from instant_q to exchange dead_email
                                   })

        self.channel.queue_declare(queue='delayed_q',
                                   durable=True)

        self.channel.queue_declare(queue='dead_q',
                                   durable=True,
                                   arguments={
                                       'x-message-ttl': 60 * 1000,  # 1 minute life before put to exchange email
                                       'x-dead-letter-exchange': 'email',  # from dead_q to exchange email
                                   })

        self.channel.queue_bind(exchange='email',
                                queue='instant_q',
                                routing_key='instant')

        self.channel.queue_bind(exchange='email',
                                queue='delayed_q',
                                routing_key='delayed')

        self.channel.queue_bind(exchange='dead_email',
                                queue='dead_q')

        self.channel.basic_consume(queue='instant_q',
                                   on_message_callback=self.on_response,
                                   auto_ack=False)

        # channel.basic_qos(prefetch_count=1)  # only 1 msg for worker until completion

    def on_response(self,
                    ch: pika.adapters.blocking_connection.BlockingChannel,
                    method: pika.spec.Basic.Deliver,
                    properties: pika.spec.BasicProperties,
                    body: bytes) -> None:

        msg = json.loads(body)
        logging.info('try send')

        try:
            res = send_email(cfg.elastic.key, cfg.elastic.email_from, msg)

            self.publish(properties.reply_to, properties, str(res))

            self.channel.basic_ack(delivery_tag=method.delivery_tag)  # manual notification of completion

        except Exception as e:
            logging.error(f'Error: {e}')
            self.channel.basic_reject(delivery_tag=method.delivery_tag,
                                      requeue=False)  # requeue=False send to exchange dead_email

    def publish(self,
                routing_key: str,
                properties: pika.spec.BasicProperties,
                msg: str) -> None:
        self.channel.basic_publish(exchange='',
                                   routing_key=routing_key,
                                   properties=pika.BasicProperties(
                                       correlation_id=properties.correlation_id),
                                   body=msg)
