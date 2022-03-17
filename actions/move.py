from actions.actions import Action
from gods import Nvwa


class Move(Action):
    direction:str
    cast = 100

    def __init__(self, direction):
        self.direction = direction

    def excute(self, target, nvwa: Nvwa):
        if target.hp <= 0:
            return

        target.action = None
        position = target.position.copy()
        if self.direction == 'UP':
            position.y = position.y + 1
        elif self.direction == 'DOWN':
            position.y = position.y - 1
        elif self.direction == 'LEFT':
            position.x = position.x - 1
        elif self.direction == 'RIGHT':
            position.x = position.x + 1

        # 如果有门就开门
        if nvwa.has_door(position):
            nvwa.open_door(position)
        # 如果是墙
        elif nvwa.has_wall(position):
            pass
            return
        else:  
            # 如果有敌人
            other = nvwa.get_by_position(position)
            # 如果有其他对象, 就攻击
            if other is not None and other.hp >0:
                target.attack(other)
                return
            nvwa.move(target, position)
        nvwa.update_actor(target)


