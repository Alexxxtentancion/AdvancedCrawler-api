import asyncio
import datetime
import pickle
import uuid

import aio_pika
import jwt

from asyncorm.main import User, Token
from authorization.utils import connection_loop, rabbit_tools, sharable_secret

conn, ch, i_queue, o_queue = connection_loop.run_until_complete(rabbit_tools(connection_loop))


class AuthMs:
    async def callback_inbound(self, message: aio_pika.IncomingMessage):
        with message.process():
            data = pickle.loads(message.body)

            _id = data.get('id')
            if data.get('r_type') == 'signup':
                try:
                    r = await asyncio.wait_for(self.signup(data.get('data')), 5)
                    data = {"id": _id, "data": r}
                except TimeoutError:
                    data = {'status': "500", "data": {}}
            elif data.get('r_type') == 'login':
                try:
                    r = await asyncio.wait_for(self.login(data.get('data')), 5)
                    data = {"id": _id, "data": r}
                except TimeoutError:
                    data = {'status': "500", "data": {}}
            elif data.get('r_type') == 'validate':
                try:
                    r = await asyncio.wait_for(self.validate(data.get('data').get('token')), 5)
                    data = {"id": _id, "data": r}
                except TimeoutError:
                    return {'status': "500", "data": {}}

            await ch.default_exchange.publish(
                aio_pika.Message(body=pickle.dumps(data)),
                routing_key='outbound',
            )

    async def consumer_inbound(self):
        await ch.set_qos(prefetch_count=1)
        await i_queue.consume(self.callback_inbound)

    async def make_request(self, r_type, data):
        id_ = uuid.uuid1()
        await ch.default_exchange.publish(
            aio_pika.Message(body=pickle.dumps({'r_type': r_type, "data": data, "id": id_.hex})),
            routing_key='inbound',
        )
        async with o_queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    r = pickle.loads(message.body)
                    if id_.hex == r.get('id'):
                        break
        return r.get('data')

    @staticmethod
    async def create_token(email, user, expire_date):
        token = jwt.encode({
            'email': email,
        }, sharable_secret)
        tok = token.decode('utf-8')
        try:
            token = await Token.objects.get(user_id=user.id)
            token_obj = Token(id=token.id, token=tok, user_id=user.id, expire_date=expire_date)
            await token_obj.save()
        except Exception as e:
            await Token(token=tok, user_id=user.id, expire_date=expire_date).save()
        return tok

    async def validate(self, token):
        try:
            try:
                token_data = await Token.objects.get(token=token)
                if datetime.datetime.strptime(token_data.expire_date, '%Y-%m-%d %H:%M:%S') < datetime.datetime.now():
                    return {"status": "error", "reason": "expired token"}
            except:
                return {"status": "error", "reason": "wrong token"}
            user = await User.objects.get(id=token_data.user_id)
            data = {"id": user.id, "email": user.email, "password": user.password,
                    "name": user.name, "created_date": user.created_date, "last_login_date": user.last_login_date}
            return {"status": "success", "data": data}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

    async def signup(self, data):
        if len(await User.objects.filter(name=data.get('data').get('name'))) == 0:
            try:
                expire_date = datetime.datetime.now() + datetime.timedelta(hours=1)
                user = await User.objects.create(email=data.get('data').get('email'),
                                                 password=data.get('data').get('password'),
                                                 name=data.get('data').get('name'),
                                                 created_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                 last_login_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                token = await self.create_token(data.get('data').get('email'), user,
                                                expire_date.strftime("%Y-%m-%d %H:%M:%S"))
                return {"status": "success", "data": {"token": token, "expire_date": expire_date}}
            except:
                return {"status": "error", "reason": "wrong data"}
        else:
            return {"status": "error", "reason": "user with this username exists"}

    async def login(self, data):
        try:
            expire_date = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
            user = await User.objects.get(email=data.get('email'), password=data.get('password'))
            print(expire_date)
            if user:
                print("got")
                token = await self.create_token(data.get('email'), user, expire_date)
                return {"status": "ok", "data": {"token": token, "expire": expire_date}}
            else:
                return {"status": "error", "reason": "no user with this email"}
        except Exception as e:
            return {"status": "error here", "reason": str(e)}


if __name__ == '__main__':
    auth = AuthMs()
    connection_loop.create_task(auth.consumer_inbound())
    print(" [*] Waiting for messages. To exit press CTRL+C")
    connection_loop.run_forever()
