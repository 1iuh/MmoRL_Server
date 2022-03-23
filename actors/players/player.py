from actors import Actor
from consts import ACTOR
from utils import MyMatrix
from random import randint

class Player(Actor):

    username: str
    max_hp = 30
    type_code = 2
    tile_code = ACTOR.PLAYER
    is_player = True
    hit_bonus = 3
    damage_bonus = 3
    explored_floor: MyMatrix


    def __init__(self, username):
        self.username = username
        super().__init__()

    def inti_explored_floor(self, map_width, map_length):
        self.explored_floor = MyMatrix(map_width, map_length)
        self.explored_floor.fillMatrixWithZero()

    def destroy(self):
        pass

    @property
    def name(self):
        return self.username

    def add_message(self, message):
        self.messages.append(message)
