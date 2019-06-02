import asyncio
import pickle

import aio_pika

from authorizationMS.auth import AuthMs
from authorizationMS.utils import connection_loop, rabbit_tools

conn, ch, i_queue, o_queue = connection_loop.run_until_complete(rabbit_tools(connection_loop))
auth = AuthMs()


async def callback_inbound(message: aio_pika.IncomingMessage):
    with message.process():
        data = pickle.loads(message.body)

        _id = data.get('id')
        timeout = data.get('timeout')
        if data.get('r_type') == 'signup':
            try:
                r = await asyncio.wait_for(auth.signup(data.get('data')), timeout)
                data = {"id": _id, "data": r}
            except TimeoutError:
                data = {'status': "500", "data": {}}
        elif data.get('r_type') == 'login':
            try:
                r = await asyncio.wait_for(auth.login(data.get('data')), timeout)
                data = {"id": _id, "data": r}
            except TimeoutError:
                data = {'status': "500", "data": {}}
        elif data.get('r_type') == 'validate':
            try:
                r = await asyncio.wait_for(auth.validate(data.get('data').get('token')), timeout)
                data = {"id": _id, "data": r}
            except TimeoutError:
                return {'status': "500", "data": {}}

        await ch.default_exchange.publish(
            aio_pika.Message(body=pickle.dumps(data)),
            routing_key='outbound',
        )


async def consumer_inbound():
    await ch.set_qos(prefetch_count=1)
    await i_queue.consume(callback_inbound)


if __name__ == '__main__':
    connection_loop.create_task(consumer_inbound())
    print(" [*] Waiting for messages. To exit press CTRL+C")
    connection_loop.run_forever()
