
from utils import Vector2
from actors import Actor
from dungeon_generator import DungeonGenerator
from consts import DOOR

class Nvwa(object):
    uid_dict: dict
    position_dict: dict
    dungeon: DungeonGenerator

    def __init__(self, dungeon):
        self.uid_dict = dict()
        self.position_dict = dict()
        self.dungeon = dungeon
            
    @staticmethod
    def get_position_key(position:Vector2):
        return "_".join([str(position.x), str(position.y)])

    def get_by_position(self, position:Vector2):
        return self.position_dict.get(self.get_position_key(position))

    def __getitem__(self, uid)->Actor:
        return self.uid_dict[uid]

    def __setitem__(self, uid, obj):
        self.uid_dict[uid] = obj
        self.position_dict[self.get_position_key(obj.position)] = obj

    def move(self, obj, position):
        self.position_dict[self.get_position_key(obj.position)] = None
        obj.position = position
        self.position_dict[self.get_position_key(obj.position)] = obj

    def delete(self, uid):
        obj = self.uid_dict[uid]
        if obj is None:
            return
        del self.position_dict[self.get_position_key(obj.position)]
        del self.uid_dict[uid]

    def dumps(self):
        res = []
        for _,v in self.uid_dict.items():
            if v.hp > 0:
                res.append({
                    "uid": v.uid,
                    "x": v.position.x,
                    "y": v.position.y,
                    "hp": v.hp,
                    "maxHp": v.max_hp,
                    "sign": v.tile_code
                })
        return res


    def has_wall(self, position:Vector2):
        if self.dungeon.los_blocking[position] == 1: 
            return True
        return False

    def has_door(self, position:Vector2):
        if self.dungeon.doors[position] == 1: 
            return True
        return False

    def open_door(self, position: Vector2):
        if self.dungeon.doors[position] == 1: 
            self.dungeon.doors[position] = 0
            self.dungeon.los_blocking[position] = 0
            self.dungeon.passable[position] = 1
            self.dungeon.tiles[position] = DOOR.opened

        
