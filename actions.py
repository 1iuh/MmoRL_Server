from abc import ABCMeta, abstractmethod
from consts import INSTRUCT


class Action(metaclass=ABCMeta):
    cast:int

    def __init__(self):
        pass

    @staticmethod
    def factory(instruct, *args):
        if instruct == INSTRUCT.MOVE: return Move(*args)

    @abstractmethod
    def excute(self, target, obj_store):
        return



class Move(Action):
    direction:str
    cast = 100


    def __init__(self, direction):
        self.direction = direction

    def excute(self, target, obj_store):
        # 能量是否够
        if target.energy < self.cast:
            self.cast -= target.energy
            target.energy = 0
            return
        
        target.energy -= self.cast
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

        if obj_store.has_wall(position):
            return

        other = obj_store.get_by_position(position)

        # 如果有其他对象 TODO
        if other is not None:
            return
        del obj_store[target.uid]
        target.position = position
        obj_store.update(target)
        # 是否有其他对象