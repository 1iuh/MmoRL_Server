from aiohttp import web
import aioredis
from consts import REDISKEYS, INSTRUCT
from utils import command_generater
from uuid import uuid4

async def create_user(redis, username):
    command = command_generater(username, INSTRUCT.SPAWNPLAYER)
    await redis.lpush(REDISKEYS.CLIENTCOMMANDS, command)
    await redis.hset(REDISKEYS.USERS, username, username)

async def signin(request):
    redis = await aioredis.from_url('redis://localhost')
    req_data = await request.json()
    username = req_data['username']
    # query user
    user = await redis.hget(REDISKEYS.USERS, username)
    # if no user , create a user
    if not user:
        await create_user(redis, username)
    token = str(uuid4())
    await redis.hset(REDISKEYS.TOKENS, token, username)
    payload = {
        "isSuccess": True,
        "response": {
            "token": token
        }
    }
    return web.json_response(payload)

app = web.Application()
app.add_routes([web.post('/signin', signin),
                # web.get('/{name}, handle)])
                ])

if __name__ == '__main__':
    web.run_app(app)
