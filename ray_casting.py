
from common import Vector2
from math import copysign


def ray_casting(blocks, origin:Vector2, range_limit: int, mapWidth: int, mapLength: int):
    vision = []

    def set_vision(x:int, y:int):
        print(x, y)
        vision.append(Vector2(x, y))

    def trace_line(origin, x, y):
        # Bresenham's line algorithm
        xDiff = x - origin.x
        yDiff = y - origin.y
        xLen = abs(xDiff)
        yLen = abs(yDiff)
        xInc = int(copysign(1, xDiff))
        yInc = int(copysign(1, yDiff))
        steep = 0
        if xLen < yLen:
            steep = 1
            xLen, yLen = yLen, xLen
            xInc, yInc = yInc, xInc
        errorInc = yLen*2
        error = -xLen
        errorReset = xLen*2
        x = origin.x
        y = origin.y
        for _ in range(1, xLen+1):
            error += errorInc
            x += xInc
            if error > 0:
                error -= errorReset
                y += yInc
            if steep:
                set_vision(y, x)
            else:
                set_vision(x, y)
        return

    set_vision(origin.x, origin.y)
    # top 
    for i in range(0, range_limit):
        trace_line(origin, origin.x - range_limit + i, origin.y + range_limit)
    # right
    for i in range(0, range_limit):
        trace_line(origin, origin.x + range_limit, origin.y + range_limit - i)
    # bottom
    for i in range(0, range_limit):
        trace_line(origin, origin.x + range_limit - 1, origin.y - range_limit)
    # left
    for i in range(0, range_limit):
        trace_line(origin, origin.x - range_limit, origin.y - range_limit + i)
