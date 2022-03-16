from actors.actor import Actor
from actions import Move
from consts import ACTOR
from random import choice


class Zombie(Actor):
    max_hp = 10
    min_attack = 4
    max_attack = 7
    name = "吸血鬼"
    tile_code = ACTOR.zombie

    def think(self):
        self.action = Move(choice(["UP","DOWN","LEFT","RIGHT"]))
        return

