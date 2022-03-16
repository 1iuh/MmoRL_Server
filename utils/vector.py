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
