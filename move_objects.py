from abc import ABCMeta
from common import Vector2, MyMatrix
from consts import INTERACTABLE
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
    uid: int
    hp:int
    max_hp:int
    min_attack:int
    max_attack:int
    position: Vector2
    name: str
    action = None
    energy: int
    sign: int
    vision: MyMatrix
    vision_range = 8

    is_player = False

    def __init__(self, position,  objStore):
        self.position = position
        self.uid = uuid4().int & (1<<64)-1
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

    def destroy(self):
        logger.info(self.__class__.__name__ + ' destroy!')
        # messages.append(f'「{self.name}」被摧毁了。')

    def think(self):
        return

    def __str__(self):
        return self.sign

    def attack(self, target):
        damage = randint(self.min_attack,self.max_attack)
        target.underAttack(damage, self)

    def underAttack(self, damage, target):
        self.hp -= damage
        return f'你攻击「{self.name}」造成了「{damage}」点伤害。'



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
        return

class Player(MoveObject):

    username: str
    max_hp = 30
    min_attack = 3
    max_attack = 8
    type_code = 2
    sign = INTERACTABLE.PLAYER
    is_player = True
    explored_floor: MyMatrix

    messages: list[str]

    def __init__(self, vender, objStore, username):
        self.username = username
        self.messages = []
        super().__init__(vender, objStore)

    def inti_explored_floor(self, map_width, map_length):
        self.explored_floor = MyMatrix(map_width, map_length)
        self.explored_floor.fillMatrixWithZero()

    def attack(self, target):
        damage = randint(self.min_attack,self.max_attack)
        battle_log = target.underAttack(damage, self)
        if self.is_player:
            self.messages.append(battle_log)

    def underAttack(self, damage, target):
        self.hp -= damage
        battle_log = f'「{target.name}」攻击你造成了「{damage}」点伤害。'
        if self.is_player:
            self.messages.append(battle_log)
        return f'你攻击「{self.name}」造成了「{damage}」点伤害。'

    @property
    def name(self):
        return self. username
