class Vector2(object):
    x: int
    y: int

    def __init__ (self, x:int, y:int):
        self.x = x
        self.y = y

    def copy(self):
        return Vector2(self.x, self.y)

    def __repr__(self):
        return '(' + str(self.x) + ',' + str(self.y) +')'

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class MyMatrix(object):
    rawData: bytearray
    width: int
    height: int

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def fillMatrixWithZero(self):
        self.rawData = bytearray(b'\x00') * self.width * self.height

    def fillMatrixWithTrue(self):
        self.rawData = bytearray(b'\x01') * self.width * self.height

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

    def output(self):
        h = self.rawData
        out = []
        for i in range(0, self.height):
            0 + i * self.width
            out.insert(0, h[0 + i * self.width: (i+1) * self.width].hex())
        return '\n'.join(out)

    def toBytes(self):
        return bytes(self.rawData)

    def toInt(self):
        return int.from_bytes(self.rawData, 'big')


class Road(object):
    start: Vector2
    end: Vector2
    passageway: list[Vector2]

    def __init__(self, start, end, passageway):
        self.start = start
        self.end = end
        self.passageway = passageway


def command_generater(user:str, inst:str):
    return '|'.join([user, inst])

