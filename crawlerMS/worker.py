import datetime
import pickle

import aio_pika

from asyncorm.exceptions import DoesNotExist
from asyncorm.main import CrawlerStats
from crawlerMS.crawler import Crowler
from crawlerMS.utils import connection_loop, rabbit_tools

conn, ch, crawler_queue = connection_loop.run_until_complete(rabbit_tools(connection_loop))


async def callback_inbound(message: aio_pika.IncomingMessage):
    with message.process():
        data = pickle.loads(message.body)
        user = data.get('user')
        try:
            domain = await CrawlerStats.objects.get(domain=data.get('domain'), author_id=user.get('id'))
            if domain:
                if datetime.datetime.strptime(domain.time,
                                              '%Y-%m-%d %H:%M:%S') > datetime.datetime.now() - datetime.timedelta(
                    seconds=30):
                    pass
                else:
                    crawl = Crowler(data.get('domain'), 4)
                    await crawl.main()
                    await CrawlerStats(id=domain.id, domain=data.get('domain'), author_id=user.get('id'),
                                       time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                       pages_count=len(crawl.links),
                                       avg_time_per_page=sum(crawl.times) / len(crawl.links),
                                       max_time_per_page=max(crawl.times), min_time_per_page=min(crawl.times)).save()
        except DoesNotExist:
            crawl = Crowler(data.get('domain'), 4)
            await crawl.main()

            await CrawlerStats.objects.create(domain=data.get('domain'), author_id=user.get('id'),
                                              time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                              pages_count=len(crawl.links),
                                              avg_time_per_page=sum(crawl.times) / len(crawl.links),
                                              max_time_per_page=max(crawl.times),
                                              min_time_per_page=min(crawl.times))


async def consumer_inbound():
    await ch.set_qos(prefetch_count=1)
    await crawler_queue.consume(callback_inbound)


if __name__ == '__main__':
    connection_loop.create_task(consumer_inbound())
    print(" [*] Waiting for messages. To exit press CTRL+C")
    connection_loop.run_forever()
