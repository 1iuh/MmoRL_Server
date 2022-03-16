#!/usr/bin/env python

from random import randint, choice
from utils import ray_casting
from consts import REDISKEYS, INSTRUCT
from actions import action_factory, Action
from actors import Player, Zombie
from gods import Nvwa
import pickle
import msgpack 
import logging
import redis
import time
from dungeon_generator import DungeonGenerator

logger = logging.getLogger("GameManager")

redis_conn = redis.Redis(host='localhost', port=6379, db=0)
redis_conn.delete(REDISKEYS.USERS)

redis_key = 'currency_dungeon'

dungeon_id = redis_conn.hget(redis_key, 'dungeon_id')
if dungeon_id is None:
    raise Exception()
dungeon_id = dungeon_id.decode('utf8')

dungeon: DungeonGenerator
with open('tmp/dungeon_dumps_'+dungeon_id, 'rb') as fp:
    dungeon = pickle.loads(fp.read())

dungeon_width = dungeon.map_width
dungeon_height = dungeon.map_height

messages = []
players = {}
online_player = {}

        

nvwa = Nvwa(dungeon)

class GameManager(object):

    def __init__(self):
        pass
            

    def spawnEnemy(self):
        for _ in range(0, randint(1, 3)):
            pt = choice(choice(dungeon.rooms).floors)
            if nvwa.get_by_position(pt) is None:
                Zombie(pt, nvwa)

        
    def spawnPlayer(self, username):
        pt = choice(choice(dungeon.rooms).floors)
        player = Player(pt, nvwa, username)
        player.inti_explored_floor(dungeon_width, dungeon_height)
        player.vision = ray_casting(dungeon.los_blocking, player.position, player.vision_range) 
        player.explored_floor.setMatrix((dungeon.tiles.toInt() & player.vision.toInt()).to_bytes(dungeon_height*dungeon_width, 'big')) 
        players[username] = player
        return
        

    def send_init_message(self, user):
        player = players.get(user)
        if player is None:
            return
        online_player[user]= player;

        payload = msgpack.packb(dict(
            messageType='INIT',
            data = dict(
                layers=dict(
                    floor=player.explored_floor.rawData, # type: ignore
                ),
                vision=player.vision.rawData,
                mapWidth=dungeon_width, # type: ignore
                mapLength=dungeon_height, # type: ignore
                playerUID=player.uid,
                messages=[f"「{user}」 进入了游戏。"],
                maxHp=player.max_hp,
                hp=player.hp,
                username=user,
                moveObjects = nvwa.dumps()
            )
        ))
        redis_key = REDISKEYS.CHANNEL + user
        redis_conn.publish(redis_key, payload) #type: ignore 

    def setPlayerAction(self, username:str, instruct:str, *args):
        player = players.get(username)
        if player is None:
            return
        player.action = action_factory(instruct, *args)
        
    def setAction(self, uid:str, instruct:str, *args):
        obj = nvwa[uid]
        obj.action = Action.factory(instruct, *args) # type:ignore

    def nextTurn(self):

        destroy_list = []
        # 执行
        for _, obj in nvwa.uid_dict.items():
            if obj.hp <= 0:
                destroy_list.append(obj)
            obj.excuteAction()
            obj.vision = ray_casting(dungeon.los_blocking, obj.position, obj.vision_range)

        # 给客户端推消息
        for username, player in online_player.items():

            redis_key = REDISKEYS.CHANNEL + username

            if player.hp <= 0:
                payload = msgpack.packb(dict(
                    messageType='GAMEOVER',
                ))
                redis_conn.publish(redis_key, payload) #type: ignore 
                return

            player.explored_floor.setMatrix((player.explored_floor.toInt() | (dungeon.tiles.toInt() & player.vision.toInt())).to_bytes(dungeon_height*dungeon_width, 'big')) 
            payload = msgpack.packb(dict(
                messageType='UPDATE',
                data = {
                    "vision": player.vision.rawData,
                    "floor": player.explored_floor.rawData, # type: ignore
                    "moveObjects": nvwa.dumps(),
                    "messages": "",
                }
            ))
            redis_conn.publish(redis_key, payload) #type: ignore 

        # 销毁对象
        while len(destroy_list) > 0:
            obj = destroy_list.pop()
            nvwa.delete(obj.uid)

    def playerDisconnect(self, user):
        logger.info(f'{user} 断开链接')
        # del online_player[user]


def command_controller(gm: GameManager, command_bytes: bytes):
    command = command_bytes.decode('utf8')
    user, instruct, *args  = command.split("|")

    print(f'recevie ={instruct}= from ={user}=')
    if instruct == INSTRUCT.INIT:
        gm.send_init_message(user)
    elif instruct == INSTRUCT.SPAWNPLAYER:
        gm.spawnPlayer(user)
    elif instruct == INSTRUCT.MOVE:
        gm.setPlayerAction(user, INSTRUCT.MOVE, *args)
        gm.nextTurn()
    elif instruct == INSTRUCT.DISCONNECT:
        gm.playerDisconnect(user)
    else:
        return


if __name__ == '__main__':
    gm = GameManager()

    # gm.spawnEnemy()
    gm.spawnPlayer('user1')
    print('game server start')
    while True:
        command = redis_conn.rpop(REDISKEYS.CLIENTCOMMANDS)
        if command:
            command_controller(gm, command)
        time.sleep(0.01)
