import pickle
import uuid

import aio_pika

from crawlerMS.utils import connection_loop, rabbit_tools

conn, ch, crawler_queue = connection_loop.run_until_complete(rabbit_tools(connection_loop))
from asyncorm.main import CrawlerStats

class CrawlerInterface:
    @staticmethod
    async def make_nowait_request(r_type:str, data=None):
        try:
            id_ = uuid.uuid4()
            await ch.default_exchange.publish(
                aio_pika.Message(
                    body=pickle.dumps(
                        {'r_type': r_type,"domain": data.get('domain'), "user": data.get("user"),
                         "id": id_.hex})),
                routing_key='crawler_queue',
            )
            return {"status": "ok", "id": id_.hex}
        except:
            return {"status": "error"}