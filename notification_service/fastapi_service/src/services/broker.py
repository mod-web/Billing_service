import json

from aio_pika import ExchangeType, Message

from src.services import AbstractBroker
from src.services.utils import get_rabbitmq_connection


class RabbitmqBroker(AbstractBroker):
    channel = None

    async def configure(self):
        self.connection = await get_rabbitmq_connection()

        self.channel = await self.connection.channel()

        self.email_exchange = await self.channel.declare_exchange(
            name='email',
            type=ExchangeType.DIRECT,
        )

        self.dead_email_exchange = await self.channel.declare_exchange(
            name='dead_email',
            type=ExchangeType.FANOUT,
        )

        instant_q = await self.channel.declare_queue(
            name='instant_q',
            durable=True,
            arguments={
               'x-dead-letter-exchange': 'dead_email',
            },
        )

        delayed_q = await self.channel.declare_queue(
            name='delayed_q',
            durable=True,
        )

        dead_q = await self.channel.declare_queue(
            name='dead_q',
            durable=True,
            arguments={
               'x-message-ttl': 60 * 1000,
               'x-dead-letter-exchange': 'email',
            },
        )

        await self.channel.declare_queue(name='return_q')

        self.instant_q = await instant_q.bind(self.email_exchange, 'instant')
        await delayed_q.bind(self.email_exchange, 'delayed')
        await dead_q.bind(self.dead_email_exchange)

        self.response = None
        self.corr_id = None

        return self

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    async def publish_to_broker(self, routing_key: str, msg: str):
        self.response = None
        self.corr_id = json.loads(msg).get('uuid')

        await self.channel.default_exchange.publish(
            Message(
                msg.encode(),
                content_type='text/plain',
                correlation_id=self.corr_id,
                reply_to='return_q',
            ),
            routing_key=routing_key,
        )

        # For working with transactions
        channel_no_confirms = await self.connection.channel(
            publisher_confirms=False
        )
        await channel_no_confirms.close()
        return self.response

        # await self.connection.process_data_events(time_limit=None)  # wait for RPC
        # return self.response
