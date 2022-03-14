#!/usr/bin/env python
from common import Vector2, MyMatrix, Vector2, Road
from room import Room
from consts import FLOOR, WALL, DOOR
from math import copysign
from random import randint
import redis
from uuid import uuid4

import pickle


redis_conn = redis.Redis(host='localhost', port=6379, db=0)

class DungeonGenerator(object):

    max_room_size = 12
    min_room_size = 6
    map_width =  45
    map_height = 40
    room_number = 15

    dungeon_id:str

    rooms: list[Room]
    passways: list

    tiles: MyMatrix
    passable: MyMatrix
    los_blocking: MyMatrix
    open_space: MyMatrix
    doors: MyMatrix
    

    def __init__(self):
        self.rooms = []
        self.passways = []
        self.dungeon_id = str(uuid4())
        redis_key = 'currency_dungeon'
        redis_conn.hset(redis_key, 'dungeon_id', self.dungeon_id )

    def generate(self):

        self.tiles  = MyMatrix(self.map_width, self.map_height)
        self.tiles.fillMatrixWithZero()
        self.passable = MyMatrix(self.map_width, self.map_height)
        self.passable.fillMatrixWithZero()
        self.los_blocking = MyMatrix(self.map_width, self.map_height)
        self.los_blocking.fillMatrixWithZero()
        self.open_space= MyMatrix(self.map_width, self.map_height)
        self.open_space.fillMatrixWithTrue()
        self.doors= MyMatrix(self.map_width, self.map_height)
        self.doors.fillMatrixWithZero()

        for _ in range(0, self.room_number):
            self.digOneRoom()
        self.conncet_rooms()
        self.printer()

        
    def digOneRoom(self)->None:
        times = 0
        while (True):
            room_width = randint(self.min_room_size, self.max_room_size)
            room_lenght = randint(self.min_room_size, self.max_room_size)
            room_x = randint(0, self.map_width-room_width)
            room_y = randint(0, self.map_height-room_lenght)

            room = Room(Vector2(room_x, room_y), room_width, room_lenght)
            is_cover = False
            for _room in self.rooms:
                if self.is_rooms_covered(_room, room):
                    is_cover = True
                    break
            if is_cover == False:
                break
            times += 1
            if (times>100000):
                return
        self.rooms.append(room)
        # write_floor
        self.write_matrix(self.passable, room.points, 1)
        self.write_matrix(self.open_space, room.points, 0)
        # write_wall
        self.write_matrix(self.los_blocking, room.walls, 1)
        self.write_matrix(self.open_space, room.walls, 0)

    @staticmethod
    def write_matrix(mtx: MyMatrix, points: list[Vector2], code: int):
        for pt in points:
            vect = Vector2(pt.x, pt.y)
            mtx[vect] = code

    @staticmethod
    def build_passway(p1:Vector2, p2:Vector2):
        passway = []
        dx = p1.x - p2.x
        dy = p1.y - p2.y
        
        diffx = int(copysign(1, dx))
        diffy = int(copysign(1, dy))

        x = p1.x
        y = p1.y
        while True:
            if dx != 0:
                x -= diffx
            elif dy != 0:
                y -= diffy
            else:
                return passway

            passway.append(Vector2(x, y))
            dx = x - p2.x
            dy = y - p2.y

    def is_rooms_covered(self, room1: Room , room2: Room):
        x1 = room1.anchor.x
        x2 = room2.anchor.x
        w1 = room1.width
        w2 = room2.width
        y1 = room1.anchor.y
        y2 = room2.anchor.y
        h1 = room1.height
        h2 = room2.height

        if ( x2 + w2 > x1 -2) and (x2 < x1 + w1 + 2):
            if ( y2 + h2 > y1 -2) and (y2 < y1 + h1 +2):
                return True
        return False



    def conncet_rooms(self):

        unlink_rooms = [] + self.rooms;
        linked_rooms = []

        for cur_room in unlink_rooms:
            min_distance = 999999
            neighbor:Room 
            for room in self.rooms:
                if room == cur_room:
                    continue
                if cur_room in room.neighbor:
                    continue
                distance = len(self.build_passway(cur_room.anchor, room.anchor))
                if distance < min_distance:
                    min_distance = distance
                    neighbor = room

            neighbor.neighbor.append(cur_room)
            cur_room.neighbor.append( neighbor)
            linked_rooms.append((cur_room, neighbor))

        for r1, r2 in linked_rooms:
            self.conncet_two_rooms(r1, r2)


    def conncet_two_rooms(self, r1: Room, r2: Room):
        min_distance = 99999
        min_path: list[Vector2] = []

        for p1 in r1.outer_floors:
            for p2 in r2.outer_floors:
                path = self.build_passway(p1, p2)
                if len(path) < min_distance:
                    # 如果路径上的墙超过了2片，则放弃
                    wall_num = 0
                    for pt in path:
                        if self.los_blocking[pt] == 1:
                            wall_num += 1
                    if wall_num > 2:
                        continue
                    min_distance = len(path)
                    min_path = path

        self.passways.append(min_path)
        self.write_matrix(self.passable, min_path, 1)
        self.write_matrix(self.open_space, min_path, 0)
        for pt in min_path:
            if self.los_blocking[pt] == 1:
                self.los_blocking[pt]= 0
                self.doors[pt] = 1

    def printer(self):

        # 画地板
        index = 0
        for n in self.passable.rawData:
            if n == 1:
                self.tiles.rawData[index] = FLOOR.NORMAL
            index += 1
        # 画房间的墙
        for rm in self.rooms:
            # 上
            for p in rm.top_walls:
                self.tiles[p] = WALL.top
            # 下
            for p in rm.bottom_walls:
                self.tiles[p] = WALL.bottom
            # 左
            for p in rm.left_walls:
                self.tiles[p] = WALL.left
            # 右
            for p in rm.right_walls:
                self.tiles[p] = WALL.right
            # 左上角
            self.tiles[rm.top_left_angle] = WALL.top_left_angle
            # 右上角
            self.tiles[rm.top_right_angle] = WALL.top_right_angle
            # 左下角
            self.tiles[rm.bottom_left_angle] = WALL.bottom_left_angle
            # 右下角
            self.tiles[rm.bottom_right_angle] = WALL.bottom_right_angle

        # 画走廊的墙
        for pw in self.passways:
            for pt in pw:
                # 上
                cpt = Vector2(pt.x, pt.y+1)
                if self.open_space[cpt] == 1:
                    self.tiles[cpt] = WALL.top
                    self.los_blocking[cpt] = 1
                    self.open_space[cpt] = 0
                # 下
                cpt = Vector2(pt.x, pt.y-1)
                if self.open_space[cpt] == 1:
                    self.tiles[cpt] = WALL.bottom
                    self.los_blocking[cpt] = 1
                    self.open_space[cpt] = 0
                # 左
                cpt = Vector2(pt.x-1, pt.y)
                if self.open_space[cpt] == 1:
                    self.tiles[cpt] = WALL.left
                    self.los_blocking[cpt] = 1
                    self.open_space[cpt] = 0
                # 右
                cpt = Vector2(pt.x+1, pt.y)
                if self.open_space[cpt] == 1:
                    self.tiles[cpt] = WALL.right
                    self.los_blocking[cpt] = 1
                    self.open_space[cpt] = 0

            for pt in pw:
                # 左上
                cpt = Vector2(pt.x-1, pt.y+1)
                if self.open_space[cpt] == 1:
                    self.tiles[cpt] = WALL.top_left_angle
                    self.los_blocking[cpt] = 1
                    self.open_space[cpt] = 0
                # 右上
                cpt = Vector2(pt.x+1, pt.y+1)
                if self.open_space[cpt] == 1:
                    self.tiles[cpt] = WALL.top_right_angle
                    self.los_blocking[cpt] = 1
                    self.open_space[cpt] = 0
                # 左下
                cpt = Vector2(pt.x-1, pt.y-1)
                if self.open_space[cpt] == 1:
                    self.tiles[cpt] = WALL.bottom_left_angle
                    self.los_blocking[cpt] = 1
                    self.open_space[cpt] = 0
                # 右下
                cpt = Vector2(pt.x+1, pt.y-1)
                if self.open_space[cpt] == 1:
                    self.tiles[cpt] = WALL.bottom_right_angle
                    self.los_blocking[cpt] = 1
                    self.open_space[cpt] = 0

        # 门
        index = 0
        for n in self.doors.rawData:
            if n == 1:
                self.tiles.rawData[index] = DOOR.opened
            index += 1

    def save(self):
        with open('tmp/dungeon_dumps_' + self.dungeon_id, 'wb') as fp:
            fp.write(pickle.dumps(self))
            print(f'save success: {self.dungeon_id}')
        

if __name__ == '__main__':
    gen = DungeonGenerator()
    gen.generate()
    # print(gen.passable.output())
    # print(gen.passable.output())
    gen.save()
