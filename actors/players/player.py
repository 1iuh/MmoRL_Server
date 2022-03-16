from actors import Actor
from consts import ACTOR
from utils import MyMatrix
from random import randint

class Player(Actor):

    username: str
    max_hp = 30
    min_attack = 3
    max_attack = 8
    type_code = 2
    tile_code = ACTOR.PLAYER
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

    def damaged(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.endgame()

    def endgame(self):
        pass

    @property
    def name(self):
        return self.username
