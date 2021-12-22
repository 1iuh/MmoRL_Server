#!/usr/bin/env python

import asyncio

import websockets
import aioredis

import logging
import async_timeout

logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("websockets.client")

STOPWORD = "STOP"

async def consumer_handler(websocket, redis, user):
    async for message in websocket:
        command = '|'.join([user, message])
        await redis.lpush('client_commands', command )

async def producer_handler(websocket, ch):
    while True:
        try:
            async with async_timeout.timeout(1):
                message = await ch.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    print(f"(Reader) Message Received: {message}")
                    if message["data"].decode() == STOPWORD:
                        print("(Reader) STOP")
                        break
                    await websocket.send(message['data'])
                await asyncio.sleep(0.01)
        except asyncio.TimeoutError:
            pass

connected = set()

async def handler(websocket):
    token = await websocket.recv()
    consumer_redis = await aioredis.from_url('redis://localhost')
    pub_redis = await aioredis.from_url('redis://localhost')

    user = await consumer_redis.get(token)
    if user is None:
        await websocket.close(1011, "authentication failed")
        return
    user = user.decode('utf8')
    pubsub = pub_redis.pubsub()
    await pubsub.subscribe("channel:"+user)

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
