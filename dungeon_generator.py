#!/usr/bin/env python
from common import Vector2, MyMatrix, Room, Point, Road
from consts import FLOOR, WALL, INTERACTABLE, REDISKEYS
from random import randint
import redis
from uuid import uuid4

redis_conn = redis.Redis(host='localhost', port=6379, db=0)

class DungeonGenerator(object):
    max_room_size = 12
    min_room_size = 7
    map_width =  99
    map_height = 99
    room_number = 10
    floor_level_matrix: MyMatrix
    loot_level_matrix: MyMatrix
    interactable_level_matrix: MyMatrix
    dungeon_id:str
    rooms: list[Room]
    roads: list[Road]

    def __init__(self):
        self.rooms = []
        self.roads = []
        self.dungeon_id = str(uuid4())
        print(self.dungeon_id )


    def generate(self):
        self.floor_level_matrix = MyMatrix(self.map_width, self.map_height)
        self.floor_level_matrix.fillMatrixWithZero()
        self.loot_level_matrix = MyMatrix(self.map_width, self.map_height)
        self.loot_level_matrix.fillMatrixWithZero()
        self.interactable_level_matrix = MyMatrix(self.map_width, self.map_height)
        self.interactable_level_matrix.fillMatrixWithZero()

        for _ in range(0, self.room_number):
            self.digOneRoom()
        self.link_rooms()

        
    def digOneRoom(self)->None:
        if self.floor_level_matrix is None:
            raise Exception('floor_level_matrix not generate.')
        if self.interactable_level_matrix is None:
            raise Exception('interactable_level_matrix not generate.')

        times = 0
        while (True):
            room_width = randint(self.min_room_size, self.max_room_size)
            room_lenght = randint(self.min_room_size, self.max_room_size)
            room_x = randint(0, self.map_width-room_width)
            room_y = randint(0, self.map_height-room_lenght)

            room = Room(Point(room_x, room_y), room_width, room_lenght)
            is_cover = False
            for _room in self.rooms:
                if self.is_rooms_covered(_room, room):
                    is_cover = True
                    break
            if is_cover == False:
                break
            times += 1
            if (times>100):
                return
        self.rooms.append(room)
        # write_floor
        self.write_matrix(self.floor_level_matrix, room.points, FLOOR.NORMAL)
        # write_wall
        self.write_matrix(self.interactable_level_matrix, room.walls, WALL.NORMAL)


    @staticmethod
    def write_matrix(mtx: MyMatrix, points: list[Point], code: int):
        for pt in points:
            vect = Vector2(pt.x, pt.y)
            mtx[vect] = code

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

    def link_rooms(self):
        self.sort_rooms()
        unlink_rooms = [] + self.rooms;
        while len(unlink_rooms) > 1:
            ur_room = unlink_rooms.pop();
            self.link_room(ur_room, unlink_rooms);

    def link_room(self, cur_room: Room, rooms: list[Room]) -> None:
        def get_road_points(start_point: Point, end_point: Point)-> list[Point]:
            points: list[Point] = []
            x = start_point.x
            y = start_point.y
            while True:
                points.append(Point(x, y))
                if x < end_point.x:
                    x += 1
                elif x > end_point.x:
                    x -= 1
                elif y < end_point.y:
                    y += 1
                elif y > end_point.y:
                    y -= 1
                else:
                    break
            return points

        def get_road_wall_points(passageway: list[Point]) -> list[Point]:
            points = []
            for index  in range(0, len(passageway)):
                pt = passageway[index]
                npt = Point(pt.x, pt.y-1)
                if self.floor_level_matrix[npt] == 0:
                    points.append(npt)
                npt = Point(pt.x, pt.y+1)
                if self.floor_level_matrix[npt] == 0:
                    points.append(npt)
                npt = Point(pt.x-1, pt.y)
                if self.floor_level_matrix[npt] == 0:
                    points.append(npt)
                npt = Point(pt.x+1, pt.y)
                if self.floor_level_matrix[npt] == 0:
                    points.append(npt)
                npt = Point(pt.x+1, pt.y+1)
                if self.floor_level_matrix[npt] == 0:
                    points.append(npt)
                npt = Point(pt.x-1, pt.y-1)
                if self.floor_level_matrix[npt] == 0:
                    points.append(npt)
                npt = Point(pt.x-1, pt.y+1)
                if self.floor_level_matrix[npt] == 0:
                    points.append(npt)
                npt = Point(pt.x+1, pt.y-1)
                if self.floor_level_matrix[npt] == 0:
                    points.append(npt)
            return points

        min_distance = 999
        road_arr = []
        start:Point
        end: Point
        angles1 = cur_room.angles
        doors1 = cur_room.doors

        angles2 = [] 
        doors2 = []

        for _room in rooms:
            angles2 += _room.angles
            doors2 += _room.doors

        for p1_index in range(0, len(angles1)):
            for p2_index in range(0, len(angles2)):
                p1 = angles1[p1_index]
                p2 = angles2[p2_index]
                d1 = doors1[p1_index]
                d2 = doors2[p2_index]
                _road = get_road_points(p1, p2)
                if not self.can_points_dig(_road):
                    continue
                if len(_road) <= min_distance:
                    min_distance = len(_road)
                    road_arr = _road
                    start = d1
                    end = d2

        # 把路画上
        road = Road(start, end, road_arr)
        self.write_matrix(self.floor_level_matrix, road.passageway, FLOOR.NORMAL)
        # 如果对路上有墙， 就把墙换成门
        for pt in road.passageway:
            if self.interactable_level_matrix[pt] == WALL.NORMAL:
                self.interactable_level_matrix[pt] = INTERACTABLE.DOOR;
        # 把路边的墙画上
        road_wall = get_road_wall_points(road_arr) 
        self.roads.append(road)
        self.write_matrix(self.interactable_level_matrix, road_wall, WALL.NORMAL)

        # 把门画上
        self.write_matrix(self.interactable_level_matrix, [start, end], INTERACTABLE.DOOR) #type: ignore

        return

    def can_points_dig(self, road: list[Point])-> bool:
        # 感觉任何时候都可以挖
        return True

    def sort_rooms(self):
        from functools import cmp_to_key

        def room_compare(room1: Room, room2:Room):
            return room1.anchor.x * room1.anchor.x + room1.anchor.y * room1.anchor.y - room2.anchor.x * room2.anchor.x - room2.anchor.y * room2.anchor.y

        sorted(self.rooms, key=cmp_to_key(room_compare))

    def save(self):
        floor_redis_key = REDISKEYS.FLOORLEVEL + self.dungeon_id
        loot_redis_key = REDISKEYS.LOOTLEVEL + self.dungeon_id
        interactable_redis_key= REDISKEYS.INTERACTABLELEVEL + self.dungeon_id
        room_redis_key= REDISKEYS.ROOMS + self.dungeon_id
        redis_conn.set(floor_redis_key, self.floor_level_matrix.toBytes())
        redis_conn.set(loot_redis_key, self.loot_level_matrix.toBytes())
        redis_conn.set(interactable_redis_key, self.interactable_level_matrix.toBytes())
        for room in self.rooms:
            redis_conn.lpush(room_redis_key, str(room))



if __name__ == '__main__':
    gen = DungeonGenerator()
    gen.generate()
    gen.save()
