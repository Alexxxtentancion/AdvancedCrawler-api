import pickle
import uuid

import aio_pika

from authorizationMS.utils import connection_loop, rabbit_tools

conn, ch, i_queue, o_queue = connection_loop.run_until_complete(rabbit_tools(connection_loop))


class AuthInterface:
    async def make_request(self, r_type:str, data=None, timeout=None):
        id_ = uuid.uuid1()
        await ch.default_exchange.publish(
            aio_pika.Message(body=pickle.dumps({'r_type': r_type, "data": data, "id": id_.hex, 'timeout': timeout})),
            routing_key='inbound',
        )
        async with o_queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    r = pickle.loads(message.body)
                    r.get('data')
                    if id_.hex == r.get('id'):
                        break
        return r.get('data')
