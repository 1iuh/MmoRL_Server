from abc import ABCMeta
from utils import Vector2, MyMatrix
from uuid import uuid4
from random import randint
import logging
logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger("GameManager")


class Actor(metaclass=ABCMeta):
    uid: int
    hp:int
    max_hp:int
    min_attack:int
    max_attack:int
    position: Vector2
    name: str
    action = None
    tile_code: int
    vision: MyMatrix
    vision_range = 5

    is_player = False

    def __init__(self, position,  objStore):
        self.position = position
        self.uid = uuid4().int & (1<<64)-1
        objStore[self.uid] = self
        self.hp = self.max_hp
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

    def attack(self, target):
        damage = randint(self.min_attack,self.max_attack)
        target.underAttack(damage, self)
