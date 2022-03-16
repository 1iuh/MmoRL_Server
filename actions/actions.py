from abc import ABCMeta, abstractmethod

class Action(metaclass=ABCMeta):
    cast:int

    def __init__(self):
        pass

    @abstractmethod
    def excute(self, target, obj_store):
        return
