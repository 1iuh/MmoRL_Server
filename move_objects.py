from abc import ABCMeta
from common import Vector2
from consts import WALL, INTERACTABLE
from random import choice
from actions import Move
from uuid import uuid4
from random import randint
import logging
logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger("GameManager")


class MoveObject(metaclass=ABCMeta):
    uid: str
    hp:int
    max_hp:int
    min_attack:int
    max_attack:int
    position: Vector2
    name: str
    action = None
    energy: int
    sign: int

    @property
    def attack(self):
        return randint(self.min_attack, self.max_attack)

    def __init__(self, position,  objStore):
        self.position = position
        self.uid = str(uuid4())
        objStore[self.uid] = self
        self.hp = self.max_hp
        self.energy = 0
        self.objStore = objStore

    def excuteAction(self):
        if self.action is None:
            self.think()
        if self.action is None:
            return
        self.action.excute(self, self.objStore)

    def kick(self, damage):
        logger.info('kick ' + self.__class__.__name__)
        # messages.append(f'你攻击「{self.name}」造成了「{damage}」点伤害。')
        self.hp = self.hp - damage
        if (self.hp < 0):
            self.destroy()
            return 0
        else:
            return self.attack

    def destroy(self):
        logger.info(self.__class__.__name__ + ' destroy!')
        # messages.append(f'「{self.name}」被摧毁了。')

    def think(self):
        return None

    def __str__(self):
        return self.sign



class Door(MoveObject):
    max_hp = 1
    min_attack = 0
    max_attack = 0
    name = "门"
    sign = INTERACTABLE.DOOR


class Enemy(MoveObject):
    max_hp = 10
    min_attack = 4
    max_attack = 7
    name = "吸血鬼"
    sign = INTERACTABLE.ENEMY

    def think(self):
        self.action = Move(choice(["UP","DOWN","LEFT","RIGHT"]))

class Player(MoveObject):

    username: str
    max_hp = 30
    min_attack = 3
    max_attack = 8
    type_code = 2
    sign = INTERACTABLE.PLAYER

    def __init__(self, vender, objStore, username):
        self.username = username
        super().__init__(vender, objStore)

