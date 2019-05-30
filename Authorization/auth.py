import asyncio
import datetime
import pickle
import uuid

import aio_pika
import jwt

from authorization.utils import connection_loop, rabbit_tools, sharable_secret
from asyncorm.main import User

conn, ch, i_queue, o_queue = connection_loop.run_until_complete(rabbit_tools(connection_loop))


class AuthMs:
    async def callback_inbound(self, message: aio_pika.IncomingMessage):
        with message.process():
            data = pickle.loads(message.body)

            if data.get('r_type') == 'signup':
                try:
                    r = await asyncio.wait_for(self.signup(data.get('data')), 5)
                    token = jwt.encode({
                        'username': data.get('data').get('name'),
                    }, sharable_secret)
                    status = r
                    _id = data.get('id')
                    data = {"id": _id,"data":{'status': status, "data": {"token": token.decode('utf-8')}}}
                except:
                    data = {'status': "500", "data": {}}

            await ch.default_exchange.publish(
                aio_pika.Message(body=pickle.dumps(data)),
                routing_key='outbound',
            )

    async def callback_outbound(self, message: aio_pika.IncomingMessage):
        with message.process():
            "Outbound"
            print('got message')
            print(pickle.loads(message.body))
            return pickle.loads(message.body)

    @staticmethod
    async def signup(data):
        if len(await User.objects.filter(name=data.get('data').get('name'))) == 0:
            await User.objects.create(email=data.get('data').get('email'), password=data.get('data').get('password'),
                                      name=data.get('data').get('name'),
                                      created_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                      last_login_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            return {"status": "success"}
        else:
            print("Нихуя")

            return {"error": "ueser with this username exists"}

    async def make_request(self, r_type, data):
        id_ = uuid.uuid1()
        print(id_)
        await ch.default_exchange.publish(
            aio_pika.Message(body=pickle.dumps({'r_type': r_type, "data": data, "id": id_.hex})),
            routing_key='inbound',
        )
        # r = await o_queue.consume(self.callback_outbound)
        async with o_queue.iterator() as queue_iter:
            # Cancel consuming after __aexit__
            async for message in queue_iter:
                async with message.process():
                    r = pickle.loads(message.body)
                    print(r.get('id'))
                    if id_.hex==r.get('id'):
                        break
        return r.get('data')

    async def consumer_inbound(self):
        await ch.set_qos(prefetch_count=1)
        await i_queue.consume(self.callback_inbound)


if __name__ == '__main__':
    auth = AuthMs()
    connection_loop.create_task(auth.consumer_inbound())
    print(" [*] Waiting for messages. To exit press CTRL+C")
    connection_loop.run_forever()
