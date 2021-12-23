from typing import Final

class FLOOR(object):
    NORMAL: Final = 1


class WALL(object):
    NORMAL: Final = 3


class INTERACTABLE(object):
    PLAYER: Final = 2
    ENEMY: Final = 5
    DOOR: Final = 4
    
class REDISKEYS(object):
    FLOORLEVEL: Final = "floor_level_matrix_"
    LOOTLEVEL: Final =  "loot_level_matrix_"
    INTERACTABLELEVEL: Final =  "interactable_level_matrix_"
    ROOMS: Final =  "rooms_"
