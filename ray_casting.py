from common import Vector2, MyMatrix
from consts import WALL, INTERACTABLE
from math import copysign
from random import randint
from time import time


def ray_casting(blocks: MyMatrix, origin:Vector2, range_limit: int):
    vision = []

    def set_vision(x:int, y:int):
        vision.append(Vector2(x, y))

    def is_block(vect: Vector2)-> bool:
        if blocks[vect] in (WALL.NORMAL, INTERACTABLE.DOOR):
            return True
        return False

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

            if x < 0 or y < 0:
                break
            if steep:
                set_vision(y, x)
            else:
                set_vision(x, y)
            if is_block(Vector2(x,y)):
                break
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

    return vision
