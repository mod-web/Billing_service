import json
import pytz
import pika
from datetime import datetime
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

        self.channel.queue_bind(exchange='email',
                                queue='instant_q',
                                routing_key='instant')

        self.channel.queue_bind(exchange='email',
                                queue='delayed_q',
                                routing_key='delayed')

        self.channel.queue_bind(exchange='dead_email',
                                queue='dead_q')

        self.channel.basic_consume(queue='delayed_q',
                                   on_message_callback=self.on_response,
                                   auto_ack=False)

        # channel.basic_qos(prefetch_count=1)  # only 1 msg for worker until completion

    def on_response(self,
                    ch: pika.adapters.blocking_connection.BlockingChannel,
                    method: pika.spec.Basic.Deliver,
                    properties: pika.spec.BasicProperties,
                    body: bytes) -> None:
        msg = json.loads(body)
        timezone = msg.get('timezone')
        time_from = datetime.strptime(msg.get('time_from'), "%H:%M:%S").time()
        time_to = datetime.strptime(msg.get('time_to'), "%H:%M:%S").time()
        current_time = datetime.now(pytz.timezone(timezone)).time().replace(microsecond=0, tzinfo=None)

        if time_from < current_time < time_to:
            self.publish('instant', properties, body)
            ch.basic_ack(delivery_tag=method.delivery_tag)  # manual notification of completion
        else:
            self.channel.basic_reject(delivery_tag=method.delivery_tag,
                                      requeue=True)  # return to the same (requeue) queue

    def publish(self,
                routing_key: str,
                props: pika.spec.BasicProperties,
                msg: str) -> None:
        self.channel.basic_publish(exchange='email',
                                   routing_key=routing_key,
                                   body=msg,
                                   properties=pika.BasicProperties(
                                       delivery_mode=2,  # make message persistent
                                       reply_to=props.reply_to,
                                       correlation_id=props.correlation_id
                                   ))
