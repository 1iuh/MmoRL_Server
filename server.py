#!/usr/bin/env python

import asyncio

import websockets
import aioredis

import logging

logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("websockets.client")


async def consumer_handler(websocket, redis, user):
    async for message in websocket:
        command = '|'.join([user, message])
        await redis.lpush('client_commands', command )

async def producer_handler(websocket, ch):
    while await ch.wait_message():
            msg = await ch
            await websocket.send(msg)

connected = set()

async def handler(websocket):
    token = await websocket.recv()
    sub = await aioredis.from_url('redis://localhost')
    pub = await aioredis.from_url('redis://localhost')

    user = await sub.get(token)
    if user is None:
        await websocket.close(1011, "authentication failed")
        return
    user = user.decode('utf8')
    ch, *_ = await pub.subscribe('chan:'+'user')

    connected.add(websocket)
    await asyncio.gather(
        consumer_handler(websocket, sub, user),
        producer_handler(websocket, ch),
    )

async def main():
    async with websockets.serve(handler, "", 8001): # type:ignore
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
