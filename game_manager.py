#!/usr/bin/env python

from random import randint, choice
from common import Vector2, MyMatrix, Room
from consts import REDISKEYS, INSTRUCT, WALL, INTERACTABLE
from actions import Action
from move_objects import Player, Door, Enemy, MoveObject
import msgpack 
import logging
import redis
import time

dungeon_id = 'b42c310c-9c75-4eb6-b2e6-11b2001f99c5'
dungeon_width = 999
dungeon_height = 999

redis_conn = redis.Redis(host='localhost', port=6379, db=0)
redis_conn.delete(REDISKEYS.USERS)

logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger("GameManager")


floor = MyMatrix(dungeon_width, dungeon_height)
floor.setMatrix(redis_conn.get(REDISKEYS.FLOORLEVEL + dungeon_id))
loot = MyMatrix(dungeon_width, dungeon_height)
loot.setMatrix(redis_conn.get(REDISKEYS.LOOTLEVEL + dungeon_id))
interactable = MyMatrix(dungeon_width, dungeon_height)
interactable.setMatrix(redis_conn.get(REDISKEYS.INTERACTABLELEVEL + dungeon_id))

room_redis_key = REDISKEYS.ROOMS + dungeon_id
rooms = []
for room_str in redis_conn.lrange(room_redis_key, 0, -1):
    rooms.append(Room.fromStr(room_str.decode('utf-8')))

messages = []
players = {}

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

    def __delitem__(self, uid):
        obj = self.uid_dict[uid]
        if obj is None:
            return
        del self.position_dict[self.get_position_key(obj.position)]

    def update(self, obj):
        self.position_dict[self.get_position_key(obj.position)] = obj

    def dumps(self):
        res = []
        for _,v in self.uid_dict.items():
            res.append({
                "x": v.position.x,
                "y": v.position.y,
                "hp": v.hp,
                "maxHp": v.max_hp,
                "uid": v.uid,
                "sign": v.sign
            })
        return res


    def has_wall(self, position:Vector2):
        if floor[position] == WALL.NORMAL: 
            return True
        return False
        

objStore = ObjectStore()

class GameManager(object):

    def __init__(self):
        for pt, v in interactable:
            if v == INTERACTABLE.DOOR:
                Door(pt, objStore)
            

    def spawnEnemy(self):
        for _ in range(0, randint(400, 500)):
            pt = choice(choice(rooms).floors)
            if objStore.get_by_position(pt) is None:
                Enemy(pt, objStore)

        
    # def AttemptMove(self, username, position):
    #     player = players[username]
    #     if interactable[position] == 3:
    #         return False
    #     if interactable[position] > 3:
    #         mb = objStore.get_by_position(position)
    #         damage = mb.kick(player.attack)
    #         player.hp = player.hp - damage
    #         if damage > 0 :
    #             messages.append(f'「{mb.name}」对你造成了「{damage}」点伤害。')
    #         return False

    #     return True


    def spawnPlayer(self, username):
        pt = choice(choice(rooms).floors)
        player = Player(pt, objStore, username)
        players[username] = player
        return
        

    def send_init_message(self, user):
        player = players.get(user)
        if player is None:
            return
        payload = msgpack.packb(dict(
            messageType='INIT',
            data = dict(
                layers=dict(
                    floor=floor.rawData,
                ),
                mapWidth=dungeon_width,
                mapLength=dungeon_height,
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
        for _, obj in objStore.uid_dict.items():
            obj.energy += 100
            obj.excuteAction()

        for _, player in players.items():
            redis_key = REDISKEYS.CHANNEL + player.username
            payload = msgpack.packb(dict(
                messageType='UPDATE',
                data = objStore.dumps()
            ))
            redis_conn.publish(redis_key, payload) #type: ignore 
            


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
    else:
        return


if __name__ == '__main__':
    gm = GameManager()
    gm.spawnEnemy()
    i = 0
    while True:
        command = redis_conn.rpop(REDISKEYS.CLIENTCOMMANDS)
        if command:
            command_controller(gm, command)
        i += 1
        if i == 2:
            gm.nextTurn()
            i = 0
        time.sleep(0.1)
