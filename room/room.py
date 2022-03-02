from common import Vector2
from random import randint

class Room(object):
    anchor: Vector2
    width: int
    height: int
    attached_rooms: list
    neighbor: list
    passway: list

    def __init__(self, anchor:Vector2, width:int, height:int):
        self.anchor = anchor
        self.width = width
        self.height = height
        self.neighbor = []
        self.passway = []

    def __str__(self):
        return "|".join([str(self.anchor.x), str(self.anchor.y), str(self.width), str(self.height)])

    @classmethod
    def fromStr(cls, room_str:str):
        x, y, width, height = room_str.split('|')
        return cls(Vector2(int(x), int(y)), int(width), int(height))

    @property
    def floors(self) -> list[Vector2]:
        pts = []
        for x in range(1, self.width-1):
            for y in range(1, self.height-1):
                pts.append(Vector2(x+self.anchor.x, y+self.anchor.y))
        return pts

    @property
    def outer_floors(self) -> list[Vector2]:
        pts = []
        for x in [2, self.width-2]:
            for y in [2, self.height-2]:
                    pts.append(Vector2(x+self.anchor.x, y+self.anchor.y))
        return pts

    @property
    def walls(self) -> list[Vector2]:
        return self.top_walls + self.bottom_walls + self.left_walls + self.right_walls

    @property
    def top_walls(self) -> list[Vector2]:
        pts = []
        for x in range(1, self.width):
            pts.append( Vector2(self.anchor.x + x, self.anchor.y + self.height-1))
        return pts

    @property
    def bottom_walls (self) -> list[Vector2]:
        pts =  []
        for x in range(1, self.width):
            pts.append( Vector2(self.anchor.x + x, self.anchor.y))
        return pts

    @property
    def left_walls(self) -> list[Vector2]:
        pts = []
        for y in range(0, self.height):
            pts.append( Vector2(self.anchor.x, self.anchor.y+y))
        return pts

    @property
    def right_walls(self) -> list[Vector2]:
        pts =  list[Vector2]()
        for y in range(1, self.height-1):
            pts.append( Vector2(self.anchor.x+self.width-1, self.anchor.y+y))
        return pts

    @property
    def points(self) -> list[Vector2]:
        pts =  list[Vector2]()
        pts += self.floors
        return pts

    @property
    def top(self) -> Vector2:
        pt = self.top_door.copy()
        pt.y -= 1
        return pt

    @property
    def left_bottom (self) -> Vector2:
        return  Vector2(self.anchor.x, self.anchor.y)

    @property
    def right_bottom (self) -> Vector2:
        return  Vector2(self.anchor.x + self.width -1, self.anchor.y)

    @property
    def bottom (self) -> Vector2:
        return  Vector2(self.bottom_door.x, self.bottom_door.y+1)

    @property
    def left (self) -> Vector2:
        return  Vector2(self.left_door.x - 1, self.left_door.y)

    @property
    def right (self) -> Vector2:
        return  Vector2(self.right_door.x + 1, self.right_door.y)

    @property
    def top_door(self) -> Vector2 :
        return  Vector2(self.anchor.x + int((self.width-1)/2), self.anchor.y)

    @property
    def bottom_door(self) -> Vector2:
        return  Vector2(self.anchor.x + int((self.width-1)/2), self.anchor.y + self.height - 1)

    @property
    def left_door(self) ->  Vector2 :
        return  Vector2(self.anchor.x, self.anchor.y+int((self.height-1)/2))

    @property
    def right_door(self) -> Vector2:
        return  Vector2(self.anchor.x + self.width -1, self.anchor.y+int((self.height-1)/2))

    @property
    def top_left_angle(self) -> Vector2:
        return  Vector2(self.anchor.x, self.anchor.y+self.height-1)

    @property
    def top_right_angle(self) -> Vector2:
        return  Vector2(self.anchor.x+self.width-1, self.anchor.y+self.height-1)

    @property
    def bottom_left_angle(self) -> Vector2:
        return  Vector2(self.anchor.x, self.anchor.y)

    @property
    def bottom_right_angle(self) -> Vector2:
        return  Vector2(self.anchor.x+self.width-1, self.anchor.y)

    @property
    def angles(self)-> list[Vector2]:
        st = []
        st.append(self.top)
        st.append(self.bottom)
        st.append(self.left)
        st.append(self.right)
        return st

    @property
    def doors(self)-> list[Vector2]:
        st = []
        st.append(self.top_door)
        st.append(self.bottom_door)
        st.append(self.left_door)
        st.append(self.right_door)
        return st
