from typing import Final

class FLOOR(object):
    NORMAL: Final = 1

class WALL(object):
    NORMAL: Final = 3

class INTERACTABLE(object):
    PLAYER: Final = 2
    ENEMY: Final = 5
    DOOR: Final = 4
