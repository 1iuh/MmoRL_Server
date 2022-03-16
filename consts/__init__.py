from typing import Final

class FLOOR(object):
    _range = range(1, 10)
    NORMAL: Final = 1

class WALL(object):
    _range = range(10, 50)
    top: Final = 10
    bottom : Final = 11
    left: Final = 12
    right: Final = 13
    top_left_angle: Final = 14
    top_right_angle: Final = 15
    bottom_left_angle: Final = 16
    bottom_right_angle: Final = 17

class DOOR(object):
    _range = range(50, 60)
    closed: Final = 50
    opened: Final = 51


class ACTOR(object):
    PLAYER: Final = 2
    zombie: Final = 5
    DOOR: Final = 4
    
class REDISKEYS(object):
    FLOORLEVEL: Final = "floor_level_matrix_"
    LOOTLEVEL: Final =  "loot_level_matrix_"
    INTERACTABLELEVEL: Final =  "interactable_level_matrix_"
    ROOMS: Final =  "rooms_"
    TOKENS: Final = "mmorl_tokens"
    USERS: Final = "mmorl_users"
    CLIENTCOMMANDS: Final = "mmorl_client_commands"
    CHANNEL: Final = "mmorl_channel:"


class INSTRUCT(object):
    INIT: Final = 'INIT'
    SPAWNPLAYER: Final = 'SPAWNPLAYER'
    MOVE: Final = 'MOVE'
    DISCONNECT: Final = 'DISCONNECT'
