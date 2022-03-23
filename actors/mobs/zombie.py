from actors.actor import Actor
from consts import ACTOR
from actions import Move


class Zombie(Actor):
    max_hp = 5
    name = "僵尸"
    tile_code = ACTOR.zombie


    def think(self):
        # 找到视野中的敌人
        actors = self.nvwa.get_actors_by_vision(self.vision)
        for actor in actors:
            if actor.is_player:
                if actor.position.x > self.position.x:
                    self.action = Move("RIGHT")
                    break
                if actor.position.y > self.position.y:
                    self.action = Move("UP")
                    break
                if actor.position.x < self.position.x:
                    self.action = Move("LEFT")
                    break
                if actor.position.y < self.position.y:
                    self.action = Move("DOWN")
                    break
        return
