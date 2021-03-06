import asyncio

import aio_pika

connection_loop = asyncio.get_event_loop()

sharable_secret = 'secret'


async def rabbit_tools(loop):
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@127.0.0.1/", loop=loop
    )
    channel = await connection.channel()

    crawler_queue = await channel.declare_queue(
        'crawler_queue',
        durable=True,
        auto_delete=False)

    return connection, channel, crawler_queue
