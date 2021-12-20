#!/usr/bin/env python

import asyncio

import websockets
import json
import logging
from random import randint, choice
from common import Vector2
from dungeon_generator import DungeonGenerator

logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("websockets.client")

from abc import ABCMeta

dungeon =  DungeonGenerator()
dungeon.generate()

floor = dungeon.floor_level_matrix
obj = dungeon.interactable_level_matrix

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
        obj[position] = self.type_code
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
        obj[self.position] = 0
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


class InitMessage(object):

    layers = dict(
        floor = floor,
        obj = obj
    )
    tp = "init"
    playerPosition: Vector2
    player: Player

    def __init__(self):
        for x in range(0, randint(30, 100)):
            pt = choice(choice(dungeon.rooms).floors)
            Enemy(pt)

        pt = choice(choice(dungeon.rooms).floors)
        self.player = Player(pt)
        self.playerPosition = self.player.position

        
    @property
    def obj(self):
        return self.layers['obj']

    def AttemptMove(self, position):
        if self.obj[position] == 3:
            return False
        if self.obj[position] == 4:
            Door(position)

        if self.obj[position] > 3:
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
            self.obj[self.playerPosition] = 0
            self.obj[position] = 2
            self.playerPosition = position


    def moveDown(self):
        position = self.playerPosition.copy()
        position.y = position.y -1
        if self.AttemptMove(position) :
            self.obj[self.playerPosition] = 0
            self.obj[position] = 2
            self.playerPosition = position

    def moveLeft(self):
        position = self.playerPosition.copy()
        position.x = position.x - 1
        if self.AttemptMove(position) :
            self.obj[self.playerPosition] = 0
            self.obj[position] = 2
            self.playerPosition = position

    def moveRight(self):
        position = self.playerPosition.copy()
        position.x = position.x + 1
        if self.AttemptMove(position) :
            self.obj[self.playerPosition] = 0
            self.obj[position] = 2
            self.playerPosition = position

    def __str__(self):
        msg = messages.copy()
        messages.clear()

        return json.dumps(dict(
            tp=self.tp,
            layers=dict(
                floor=floor.toHex(),
                obj=obj.toHex()
            ),
            mapWidth=dungeon.map_width,
            mapLength=dungeon.map_height,
            messages=msg,
            hp=self.player.hp,
            maxHp=self.player.max_hp,
            objStore = objStore.json()
        ))

    def update(self):
        msg = messages.copy()
        messages.clear()

        return json.dumps(dict(
            tp=self.tp,
            layers=dict(
                floor="",
                obj=obj.toHex()
            ),
            mapWidth=dungeon.map_width,
            mapLength=dungeon.map_height,
            messages=msg,
            hp=self.player.hp,
            maxHp=self.player.max_hp,
            objStore = objStore.json()
        ))

init = InitMessage()

async def first_message_handler(websocket):
    user = None




connected = set()

response = []

async def consumer(message, user):
    if message == "init":
        return str(init)
    elif message == "up":
        init.moveUp();
    elif message == "down":
        init.moveDown();
    elif message == "left":
        init.moveLeft();
    elif message == "right":
        init.moveRight();

async def producer():
    message = "Hello, World!"
    await asyncio.sleep(5)
    return message


async def consumer_handler(websocket, user):
    async for message in websocket:
        await consumer(message, user)

async def producer_handler(websocket, user):
    while True:
        message = await producer()
        await websocket.send(message)


async def handler(websocket):
    logger.info('=connected=')
    token = await websocket.recv()
    user = None
    if token == "1":
        user = 1
    if token == "2":
        user = 2
    if user is None:
        await websocket.close(1011, "authentication failed")
        return
    connected.add(websocket)
    await asyncio.gather(
        consumer_handler(websocket, user),
        producer_handler(websocket, user),
    )

async def main():
    async with websockets.serve(handler, "", 8001): # type:ignore
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
