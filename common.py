class Vector2(object):
    x: int
    y: int

    def __init__ (self, x:int, y:int):
        self.x = x
        self.y = y

    def copy(self):
        return Vector2(self.x, self.y)


class MyMatrix(object):
    rawData: bytearray
    width: int
    height: int

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def fillMatrixWithZero(self):
        self.rawData = bytearray(self.width*self.height)

    def setMatrix(self, byte_array):
        self.rawData = bytearray(byte_array)

    def __getitem__(self, vect):
        index  = vect.x + vect.y * self.width
        return self.rawData[index] 

    def __setitem__(self, vect, v):
        index  = vect.x + vect.y * self.width
        self.rawData[index] = v 

    def __len__(self):
        return len(self.rawData)

    def __str__(self):
        output = ''
        for v in range(0, self.height):
            start = v * self.width
            end = start + self.width
            output = ''.join(str(i) for i in self.rawData[start: end]) + '\n' + output
        return output

    def __iter__(self):
        self._iter_num = 0
        return self

    def __next__(self):
        if self._iter_num > (self.width * self.height - 1):
            raise StopIteration
        y, x = divmod(self._iter_num, self.width)
        pt = Vector2(x, y)
        v = self[pt]
        self._iter_num += 1
        return pt, v

    def toHex(self):
        return self.rawData.hex()


    def toBytes(self):
        return bytes(self.rawData)


class Point(Vector2):

    def copy(self):
        return Point(self.x, self.y)


class Room(object):
    anchor: Point
    width: int
    height: int
    attached_rooms: list

    def __init__(self, anchor:Point, width:int, height:int):
        self.anchor = anchor
        self.width = width
        self.height = height

    def __str__(self):
        return "|".join([str(self.anchor.x), str(self.anchor.y), str(self.width), str(self.height)])

    @classmethod
    def fromStr(cls, room_str:str):
        x, y, width, height = room_str.split('|')
        return cls(Point(int(x), int(y)), int(width), int(height))

    @property
    def floors(self) -> list[Point]:
        pts = []
        for x in range(1, self.width-1):
            for y in range(1, self.height-1):
                pts.append(Point(x+self.anchor.x, y+self.anchor.y))
        return pts

    @property
    def walls(self) -> list[Point]:
        return self.top_walls + self.bottom_walls + self.left_walls + self.right_walls

    @property
    def top_walls(self) -> list[Point]:
        pts = []
        for x in range(1, self.width):
            pts.append( Point(self.anchor.x + x, self.anchor.y))
        return pts

    @property
    def bottom_walls (self) -> list[Point]:
        pts =  []
        for x in range(1, self.width):
            pts.append( Point(self.anchor.x + x, self.anchor.y+self.height-1))
        return pts

    @property
    def left_walls(self) -> list[Point]:
        pts = []
        for y in range(0, self.height):
            pts.append( Point(self.anchor.x, self.anchor.y+y))
        return pts

    @property
    def right_walls(self) -> list[Point]:
        pts =  list[Point]()
        for y in range(1, self.height-1):
            pts.append( Point(self.anchor.x+self.width-1, self.anchor.y+y))
        return pts

    @property
    def points(self) -> list[Point]:
        pts =  list[Point]()
        pts += self.floors
        pts += self.walls
        return pts

    @property
    def top(self) -> Point:
        pt = self.top_door.copy()
        pt.y -= 1
        return pt

    @property
    def left_bottom (self) -> Point:
        return  Point(self.anchor.x, self.anchor.y)

    @property
    def right_bottom (self) -> Point:
        return  Point(self.anchor.x + self.width -1, self.anchor.y)

    @property
    def bottom (self) -> Point:
        return  Point(self.bottom_door.x, self.bottom_door.y+1)

    @property
    def left (self) -> Point:
        return  Point(self.left_door.x - 1, self.left_door.y)

    @property
    def right (self) -> Point:
        return  Point(self.right_door.x + 1, self.right_door.y)

    @property
    def top_door(self) -> Point :
        return  Point(self.anchor.x + int((self.width-1)/2), self.anchor.y)

    @property
    def bottom_door(self) -> Point:
        return  Point(self.anchor.x + int((self.width-1)/2), self.anchor.y + self.height - 1)

    @property
    def left_door(self) ->  Point :
        return  Point(self.anchor.x, self.anchor.y+int((self.height-1)/2))

    @property
    def right_door(self) -> Point:
        return  Point(self.anchor.x + self.width -1, self.anchor.y+int((self.height-1)/2))

    @property
    def angles(self)-> list[Point]:
        st = []
        st.append(self.top)
        st.append(self.bottom)
        st.append(self.left)
        st.append(self.right)
        return st

    @property
    def doors(self)-> list[Point]:
        st = []
        st.append(self.top_door)
        st.append(self.bottom_door)
        st.append(self.left_door)
        st.append(self.right_door)
        return st


class Road(object):
    start: Point
    end: Point
    passageway: list[Point]

    def __init__(self, start, end, passageway):
        self.start = start
        self.end = end
        self.passageway = passageway


def command_generater(user:str, inst:str):
    return '|'.join([user, inst])

