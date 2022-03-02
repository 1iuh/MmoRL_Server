#!/usr/bin/env python

from random import randint, choice
from common import Vector2, MyMatrix
from consts import REDISKEYS, INSTRUCT, WALL, INTERACTABLE
from actions import Action
from move_objects import Player, Door, Enemy, MoveObject
from ray_casting import ray_casting
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

class ObjectStore(object):
    uid_dict: dict
    position_dict: dict

    def __init__(self):
        self.uid_dict = dict()
        self.position_dict = dict()
            
    @staticmethod
    def get_position_key(position:Vector2):
        return "_".join([str(position.x), str(position.y)])

    def get_by_position(self, position:Vector2):
        return self.position_dict.get(self.get_position_key(position))

    def __getitem__(self, uid)->MoveObject:
        return self.uid_dict[uid]

    def __setitem__(self, uid, obj):
        self.uid_dict[uid] = obj
        self.position_dict[self.get_position_key(obj.position)] = obj

    def move(self, obj, position):
        self.position_dict[self.get_position_key(obj.position)] = None
        obj.position = position
        self.position_dict[self.get_position_key(obj.position)] = obj

    def delete(self, uid):
        obj = self.uid_dict[uid]
        if obj is None:
            return
        del self.position_dict[self.get_position_key(obj.position)]
        del self.uid_dict[uid]

    def dumps(self):
        res = []
        for _,v in self.uid_dict.items():
            if v.hp > 0:
                res.append({
                    "uid": v.uid,
                    "x": v.position.x,
                    "y": v.position.y,
                    "hp": v.hp,
                    "maxHp": v.max_hp,
                    "energy": v.energy,
                    "sign": v.sign
                })
        return res


    def has_wall(self, position:Vector2):
        if dungeon.los_blocking[position] == 1: 
            return True
        return False
        

objStore = ObjectStore()

class GameManager(object):

    def __init__(self):
        pass
            

    def spawnEnemy(self):
        for _ in range(0, randint(1, 3)):
            pt = choice(choice(dungeon.rooms).floors)
            if objStore.get_by_position(pt) is None:
                Enemy(pt, objStore)

        
    def spawnPlayer(self, username):
        pt = choice(choice(dungeon.rooms).floors)
        player = Player(pt, objStore, username)
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
                #vision=player.vision,
                mapWidth=dungeon_width, # type: ignore
                mapLength=dungeon_height, # type: ignore
                playerUID=player.uid,
                messages=[f"「{user}」 进入了游戏。"],
                maxHp=player.max_hp,
                hp=player.hp,
                username=user,
                moveObjects = objStore.dumps()
            )
        ))
        redis_key = REDISKEYS.CHANNEL + user
        redis_conn.publish(redis_key, payload) #type: ignore 

    def setPlayerAction(self, username:str, instruct:str, *args):
        player = players.get(username)
        if player is None:
            return
        player.action = Action.factory(instruct, *args)
        
    def setAction(self, uid:str, instruct:str, *args):
        obj = objStore[uid]
        obj.action = Action.factory(instruct, *args) # type:ignore

    def nextTurn(self):

        destroy_list = []
        # 执行
        for _, obj in objStore.uid_dict.items():
            if obj.hp <= 0:
                destroy_list.append(obj)
            obj.energy += 100
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
                    #"vision": player.vision,
                    "floor": player.explored_floor.rawData, # type: ignore
                    "moveObjects": objStore.dumps(),
                    "messages": "",

                }
            ))
            redis_conn.publish(redis_key, payload) #type: ignore 

        # 销毁对象
        while len(destroy_list) > 0:
            obj = destroy_list.pop()
            objStore.delete(obj.uid)

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

    gm.spawnEnemy()
    while True:
        command = redis_conn.rpop(REDISKEYS.CLIENTCOMMANDS)
        if command:
            command_controller(gm, command)
        time.sleep(0.01)
