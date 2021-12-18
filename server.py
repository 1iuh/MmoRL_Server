#!/usr/bin/env python

import asyncio

import websockets
import json
import logging
from random import randint

logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("websockets.client")

from abc import ABCMeta

floor = [
    [0, 0, 0, 0, 0, 0 ,0, 0, 0, 0, 0, 0, 0, 0 ,0, 0, 0],
    [0, 1, 1, 1, 1, 1 ,1, 1, 1, 1, 1, 1, 1, 1 ,1, 1, 0],
    [0, 1, 1, 1, 1, 1 ,1, 1, 1, 1, 1, 1, 1, 1 ,1, 1, 0],
    [0, 1, 1, 1, 1, 1 ,1, 1, 1, 1, 1, 1, 1, 1 ,1, 1, 0],
    [0, 1, 1, 1, 1, 1 ,1, 1, 1, 1, 1, 1, 1, 1 ,1, 1, 0],
    [0, 1, 1, 1, 1, 1 ,1, 1, 1, 1, 1, 1, 1, 1 ,1, 1, 0],
    [0, 1, 1, 1, 1, 1 ,1, 1, 1, 1, 1, 1, 1, 1 ,1, 1, 0],
    [0, 1, 1, 1, 1, 1 ,1, 1, 1, 1, 1, 1, 1, 1 ,1, 1, 0],
    [0, 1, 1, 1, 1, 1 ,1, 1, 1, 1, 1, 1, 1, 1 ,1, 1, 0],
    [0, 1, 1, 1, 1, 1 ,1, 1, 1, 1, 1, 1, 1, 1 ,1, 1, 0],
    [1, 1, 1, 1, 1, 1 ,1, 1, 1, 1, 1, 1, 1, 1 ,1, 1, 1],
    [0, 1, 1, 1, 1, 1 ,1, 1, 1, 1, 1, 1, 1, 1 ,1, 1, 0],
    [0, 1, 1, 1, 1, 1 ,1, 1, 1, 1, 1, 1, 1, 1 ,1, 1, 0],
    [0, 1, 1, 1, 1, 1 ,1, 1, 1, 1, 1, 1, 1, 1 ,1, 1, 0],
    [0, 1, 1, 1, 1, 1 ,1, 1, 1, 1, 1, 1, 1, 1 ,1, 1, 0],
    [0, 1, 1, 1, 1, 1 ,1, 1, 1, 1, 1, 1, 1, 1 ,1, 1, 0],
    [0, 1, 1, 1, 1, 1 ,1, 1, 1, 1, 1, 1, 1, 1 ,1, 1, 0],
    [0, 1, 1, 1, 1, 1 ,1, 1, 1, 1, 1, 1, 1, 1 ,1, 1, 0],
    [0, 1, 1, 1, 1, 1 ,1, 1, 1, 1, 1, 1, 1, 1 ,1, 1, 0],
    [0, 1, 1, 1, 1, 1 ,1, 1, 1, 1, 1, 1, 1, 1 ,1, 1, 0],
    [0, 1, 1, 1, 1, 1 ,1, 1, 1, 1, 1, 1, 1, 1 ,1, 1, 0],
    [0, 0, 0, 0, 0, 0 ,0, 0, 0, 0, 0, 0, 0, 0 ,0, 0, 0]
]

obj = [
    [0, 0, 0, 0, 0, 0 ,0, 0, 0, 0, 0, 0, 0, 0 ,0, 0, 0],
    [0, 3, 3, 3, 3, 3 ,0, 0, 0, 0, 0, 0, 3, 3 ,3, 3, 0],
    [0, 3, 0, 0, 0, 3 ,0, 0, 0, 0, 0, 0, 3, 0 ,0, 3, 0],
    [0, 3, 0, 0, 0, 3 ,0, 0, 0, 0, 0, 0, 3, 0 ,0, 3, 0],
    [0, 3, 0, 0, 0, 3 ,0, 0, 0, 0, 0, 0, 3, 0 ,0, 3, 0],
    [0, 3, 0, 0, 0, 3 ,3, 3, 3, 3, 3, 3, 3, 0 ,0, 3, 0],
    [0, 3, 0, 0, 0, 0 ,0, 0, 0, 0, 0, 0, 0, 0 ,0, 3, 0],
    [0, 3, 0, 0, 0, 3 ,3, 3, 3, 3, 3, 3, 3, 0 ,0, 3, 0],
    [0, 3, 0, 0, 0, 3 ,0, 0, 0, 0, 0, 0, 3, 0 ,0, 3, 0],
    [0, 3, 0, 0, 0, 3 ,0, 0, 0, 0, 0, 0, 3, 0 ,0, 3, 0],
    [0, 3, 0, 0, 0, 3 ,0, 0, 0, 0, 0, 0, 3, 0 ,0, 3, 0],
    [0, 3, 3, 3, 3, 3 ,0, 0, 0, 0, 0, 0, 3, 0 ,0, 3, 0],
    [0, 0, 0, 0, 0, 0 ,0, 0, 0, 0, 0, 0, 3, 0 ,0, 3, 0],
    [0, 0, 0, 0, 0, 0 ,0, 0, 0, 0, 0, 0, 3, 3 ,3, 3, 0],
    [0, 0, 0, 0, 0, 0 ,0, 0, 0, 0, 0, 0, 0, 0 ,0, 0, 0],
    [0, 0, 0, 0, 0, 0 ,0, 0, 0, 0, 0, 0, 0, 0 ,0, 0, 0],
    [0, 0, 0, 0, 0, 0 ,0, 0, 0, 0, 0, 0, 0, 0 ,0, 0, 0],
    [0, 0, 0, 0, 0, 0 ,0, 0, 0, 0, 0, 0, 0, 0 ,0, 0, 0],
    [0, 0, 0, 0, 0, 0 ,0, 0, 0, 0, 0, 0, 0, 0 ,0, 0, 0],
    [0, 0, 0, 0, 0, 0 ,0, 0, 0, 0, 0, 0, 0, 0 ,0, 0, 0],
    [0, 0, 0, 0, 0, 0 ,0, 0, 0, 0, 0, 0, 0, 0 ,0, 0, 0],
    [0, 0, 0, 0, 0, 0 ,0, 0, 0, 0, 0, 0, 0, 0 ,0, 0, 0]
]

objStore = {}
messages = []

class Vector2(object):
    x: int
    y: int

    def __init__ (self, x, y):
        self.x = x
        self.y = y

    def copy(self):
        return Vector2(self.x, self.y)

class MoveObject(metaclass=ABCMeta):
    hp:int
    min_attack:int
    max_attack:int
    type_code:int
    position: Vector2
    name: str

    @property
    def attack(self):
        return randint(self.min_attack, self.max_attack)

    def __init__(self, position:Vector2):
        self.position = position
        obj[position.x][position.y] = self.type_code
        objStore[str(position.x) + str(position.y)] = self

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
        obj[self.position.x][self.position.y] = 0
        objStore[str(self.position.x) + str(self.position.y)] = None


    def __str__(self):
        return self.type_code


class Door(MoveObject):
    hp = 1
    min_attack = 0
    max_attack = 0
    type_code = 4
    name = "门"


class Enemy(MoveObject):
    hp = 20
    min_attack = 4
    max_attack = 7
    type_code = 5
    name = "吸血鬼"


class Player(MoveObject):
    hp = 30
    min_attack = 3
    max_attack = 5
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
        Door(Vector2(6,5))
        Enemy(Vector2(6,10))
        self.player = Player(Vector2(6,3))
        self.playerPosition = self.player.position

        
    @property
    def obj(self):
        return self.layers['obj']

    def AttemptMove(self, position):
        if self.obj[position.x][position.y] == 3:
            return False
        if self.obj[position.x][position.y] > 3:
            mb = objStore[str(position.x) + str(position.y)]
            damage = mb.kick(self.player.attack)
            self.player.hp = self.player.hp - damage
            if damage > 0 :
                messages.append(f'「{mb.name}」对你造成了「{damage}」点伤害。')
            return False

        return True

    def moveUp(self):
        position = self.playerPosition.copy()
        position.x = position.x + 1
        if self.AttemptMove(position) :
            self.obj[self.playerPosition.x][self.playerPosition.y] = 0
            self.obj[position.x][position.y] = 2
            self.playerPosition = position


    def moveDown(self):
        position = self.playerPosition.copy()
        position.x = position.x - 1
        if self.AttemptMove(position) :
            self.obj[self.playerPosition.x][self.playerPosition.y] = 0
            self.obj[position.x][position.y] = 2
            self.playerPosition = position

    def moveLeft(self):
        position = self.playerPosition.copy()
        position.y = position.y -1
        if self.AttemptMove(position) :
            self.obj[self.playerPosition.x][self.playerPosition.y] = 0
            self.obj[position.x][position.y] = 2
            self.playerPosition = position

    def moveRight(self):
        position = self.playerPosition.copy()
        position.y = position.y + 1
        if self.AttemptMove(position) :
            self.obj[self.playerPosition.x][self.playerPosition.y] = 0
            self.obj[position.x][position.y] = 2
            self.playerPosition = position

    def __str__(self):
        msg = messages.copy()
        messages.clear()

        return json.dumps(dict(
            tp=self.tp,
            layers=self.layers,
            mapWidth=len(self.layers['floor']),
            mapLength=len(self.layers['floor'][0]),
            messages=msg,
            hp=self.player.hp
        ))

init = InitMessage()


async def handler(websocket):
    while True:
        message = await websocket.recv()
        if message == "init":
            await websocket.send(str(init))
        elif message == "up":
            init.moveUp();
        elif message == "down":
            init.moveDown();
        elif message == "left":
            init.moveLeft();
        elif message == "right":
            init.moveRight();


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
