#!/usr/bin/env python

from random import randint, choice
from common import Vector2, MyMatrix, Room
from abc import ABCMeta
from consts import REDISKEYS
import logging
import redis

dungeon_id = '978b95e2-1de3-43f1-880f-44254a7a6ee5'
dungeon_width = 300
dungeon_height = 300

redis_conn = redis.Redis(host='localhost', port=6379, db=0)

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
room_redis_key = REDISKEYS.ROOMS

rooms = []
for room_str in redis_conn.lrange(room_redis_key, 0, -1):
    rooms.append(Room.fromStr(room_str.decode('utf-8')))

messages = []

class ObjectStore(object):
    store: dict

    def __init__(self):
        self.store = dict()

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, val):
        self.store[key] = val

    def __delitem__(self, key):
        del self.store[key]

    def json(self):
        res = dict()

        for k,v in self.store.items():
            res[k] = {
                "hp": v.hp,
                "maxHp": v.max_hp
            }
            
        return res

objStore = ObjectStore()


class MoveObject(metaclass=ABCMeta):
    hp:int
    max_hp:int
    min_attack:int
    max_attack:int
    type_code:int
    position: Vector2
    name: str

    @property
    def attack(self):
        return randint(self.min_attack, self.max_attack)

    def __init__(self, position):
        self.position = position
        interactable[position] = self.type_code
        objStore[str(position.x) + str(position.y)] = self
        self.hp = self.max_hp

    def kick(self, damage):
        logger.info('kick ' + self.__class__.__name__)
        messages.append(f'你攻击「{self.name}」造成了「{damage}」点伤害。')
        self.hp = self.hp - damage
        if (self.hp < 0):
            self.destroy()
            return 0
        else:
            return self.attack

    def destroy(self):
        logger.info(self.__class__.__name__ + ' destroy!')
        messages.append(f'「{self.name}」被摧毁了。')
        interactable[self.position] = 0
        del objStore[str(self.position.x) + str(self.position.y)]


    def __str__(self):
        return self.type_code


class Door(MoveObject):
    max_hp = 1
    min_attack = 0
    max_attack = 0
    type_code = 4
    name = "门"


class Enemy(MoveObject):
    max_hp = 10
    min_attack = 4
    max_attack = 7
    type_code = 5
    name = "吸血鬼"


class Player(MoveObject):
    max_hp = 30
    min_attack = 3
    max_attack = 8
    type_code = 2


class GameManager(object):

    playerPosition: Vector2
    player: Player

    def __init__(self):
        for _ in range(0, randint(30, 100)):
            pt = choice(choice(rooms).floors)
            Enemy(pt)

        pt = choice(choice(rooms).floors)
        self.player = Player(pt)
        self.playerPosition = self.player.position

        
    def AttemptMove(self, position):
        if interactable[position] == 3:
            return False
        if interactable[position] == 4:
            Door(position)
        if interactable[position] > 3:
            mb = objStore[str(position.x) + str(position.y)]
            damage = mb.kick(self.player.attack)
            self.player.hp = self.player.hp - damage
            if damage > 0 :
                messages.append(f'「{mb.name}」对你造成了「{damage}」点伤害。')
            return False

        return True

    def moveUp(self):
        position = self.playerPosition.copy()
        position.y = position.y + 1
        if self.AttemptMove(position) :
            interactable[self.playerPosition] = 0
            interactable[position] = 2
            self.playerPosition = position


    def moveDown(self):
        position = self.playerPosition.copy()
        position.y = position.y -1
        if self.AttemptMove(position) :
            interactable[self.playerPosition] = 0
            interactable[position] = 2
            self.playerPosition = position

    def moveLeft(self):
        position = self.playerPosition.copy()
        position.x = position.x - 1
        if self.AttemptMove(position) :
            interactable[self.playerPosition] = 0
            interactable[position] = 2
            self.playerPosition = position

    def moveRight(self):
        position = self.playerPosition.copy()
        position.x = position.x + 1
        if self.AttemptMove(position) :
            interactable[self.playerPosition] = 0
            interactable[position] = 2
            self.playerPosition = position

    def __str__(self):
        pass
        # msg = messages.copy()
        # messages.clear()

        # return json.dumps(dict(
        #     tp=self.tp,
        #     layers=dict(
        #         floor=floor.toHex(),
        #         obj=obj.toHex()
        #     ),
        #     mapWidth=dungeon.map_width,
        #     mapLength=dungeon.map_height,
        #     messages=msg,
        #     hp=self.player.hp,
        #     maxHp=self.player.max_hp,
        #     objStore = objStore.json()
        # ))


    def update(self):
        pass
        # msg = messages.copy()
        # messages.clear()

        # return json.dumps(dict(
        #     tp=self.tp,
        #     layers=dict(
        #         floor="",
        #         obj=obj.toHex()
        #     ),
        #     mapWidth=dungeon.map_width,
        #     mapLength=dungeon.map_height,
        #     messages=msg,
        #     hp=self.player.hp,
        #     maxHp=self.player.max_hp,
        #     objStore = objStore.json()
        # ))
