from actors.actor import Actor
from consts import ACTOR
# from random import choice
# from actions import Move


class Zombie(Actor):
    max_hp = 5
    name = "僵尸"
    tile_code = ACTOR.zombie

    def damaged(self, damage:int):
        self.hp -= damage
        if self.hp < 0:
            self.destroy()

    def think(self):
        # self.action = Move(choice(["UP","DOWN","LEFT","RIGHT"]))
        return

