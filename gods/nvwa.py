from __future__ import annotations

from utils import Vector2, ray_casting, MyMatrix
from actors import Actor, Player
from dungeon_generator import DungeonGenerator
from consts import DOOR

import logging
logger = logging.getLogger("Nvwa")

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

    def move(self, actor, position):
        self.position_dict[self.get_position_key(actor.position)] = None
        actor.position = position
        self.position_dict[self.get_position_key(actor.position)] = actor


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
                    "tile_code": v.tile_code
                })
        return res

    def get_actors_by_vision(self, vision:MyMatrix):
        res = []
        for _,v in self.uid_dict.items():
            if vision[v.position] == 255:
                res.append(v)
        return res

    def dump_by_vision(self, vision:MyMatrix):
        res = []
        for _,v in self.uid_dict.items():
            if vision[v.position] == 255:
                res.append({
                    "uid": v.uid,
                    "x": v.position.x,
                    "y": v.position.y,
                    "hp": v.hp,
                    "maxHp": v.max_hp,
                    "tile_code": v.tile_code,
                    "hurt": v.hurt
                })
                v.hurt = []
        return res


    def has_wall(self, position:Vector2):
        if self.dungeon.los_blocking[position] == 1: 
            return True
        return False

    def has_door(self, position:Vector2):
        if self.dungeon.passable[position] == 1:
            return False
        if self.dungeon.doors[position] == 1: 
            return True
        return False

    def open_door(self, position: Vector2):
        if self.dungeon.doors[position] == 1: 
            self.dungeon.los_blocking[position] = 0
            self.dungeon.passable[position] = 1
            self.dungeon.tiles[position] = DOOR.opened

    def spawn_actor(self, actor:Actor, position:Vector2):
        if self.get_by_position(position) is not None:
            logger.warning(f'{str(position)} already has something')
            return
        actor.position = position
        actor.nvwa = self
        actor.vision = ray_casting(self.dungeon.los_blocking, actor.position, actor.vision_range) 
        self.uid_dict[actor.uid] = actor
        self.position_dict[self.get_position_key(actor.position)] = actor
        if isinstance(actor, Player):
            dungeon_width = self.dungeon.map_width
            dungeon_height = self.dungeon.map_height
            actor.inti_explored_floor(dungeon_width, dungeon_height)
            actor.explored_floor.setMatrix((self.dungeon.tiles.toInt() & actor.vision.toInt()).to_bytes(dungeon_height*dungeon_width, 'big')) 

    def update_actor(self, actor:Actor):
        actor.vision = ray_casting(self.dungeon.los_blocking, actor.position, actor.vision_range) 
        if isinstance(actor, Player):
            dungeon_width = self.dungeon.map_width
            dungeon_height = self.dungeon.map_height
            actor.explored_floor.setMatrix(
                (actor.explored_floor.toInt() | (self.dungeon.tiles.toInt() & actor.vision.toInt())
                 ).to_bytes(dungeon_height*dungeon_width, 'big'))

    def destroy(self, actor:Actor):
        del self.uid_dict[actor.uid]
        del self.position_dict[self.get_position_key(actor.position)]
        del actor
