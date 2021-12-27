#!/usr/bin/env python

import asyncio

import websockets
import aioredis

import logging
import async_timeout
from consts import REDISKEYS, INSTRUCT
from common import command_generater


logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("websockets.client")

STOPWORD = b"STOP"

connected = set()

async def consumer_handler(websocket, redis, user):
    try:
        # 先发送一条初始化数据，让客户端渲染地图等
        command = command_generater(user, INSTRUCT.INIT)
        await redis.lpush(REDISKEYS.CLIENTCOMMANDS, command )

        async for message in websocket:
            command = command_generater(user, message)
            await redis.lpush(REDISKEYS.CLIENTCOMMANDS, command )
    finally:
        command = command_generater(user, INSTRUCT.DISCONNECT)
        await redis.lpush(REDISKEYS.CLIENTCOMMANDS, command)


async def producer_handler(websocket, ch):
    while True:
        try:
            async with async_timeout.timeout(1):
                message = await ch.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    if message["data"] == STOPWORD:
                        break
                    await websocket.send(message['data'])
                await asyncio.sleep(0.01)
        except asyncio.TimeoutError:
            pass


async def handler(websocket):
    token = await websocket.recv()
    consumer_redis = await aioredis.from_url('redis://localhost')
    pub_redis = await aioredis.from_url('redis://localhost')

    user = await consumer_redis.hget(REDISKEYS.TOKENS, token)
    if user is None:
        await websocket.close(1011, "authentication failed")
        return
    user = user.decode('utf8')
    logger.info(f'{user} logged.')
    pubsub = pub_redis.pubsub()
    logger.info(f'start to sub {REDISKEYS.CHANNEL + user}')
    await pubsub.subscribe(REDISKEYS.CHANNEL + user)

    connected.add(websocket)
    await asyncio.gather(
        consumer_handler(websocket, consumer_redis, user),
        producer_handler(websocket, pubsub),
    )

async def main():
    async with websockets.serve(handler, "", 8001): # type:ignore
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
