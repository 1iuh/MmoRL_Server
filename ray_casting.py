from common import Vector2, MyMatrix
from consts import WALL, INTERACTABLE
from math import copysign
from random import randint
from time import time


def ray_casting(blocks: MyMatrix, origin:Vector2, range_limit: int):
    map_width = blocks.width
    map_height = blocks.height

    vision = MyMatrix(map_width, map_height)
    vision.fillMatrixWithZero()

    def set_vision(x:int, y:int):
        vision[Vector2(x, y)] = 0xff

    def is_block(vect: Vector2)-> bool:
        if blocks[vect] == 1: 
            return True
        return False

    def trace_line(origin, x, y):
        # Bresenham's line algorithm

        xDiff = x - origin.x
        yDiff = y - origin.y
        xy_diff = origin.x - origin.y
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

        x0 = origin.x
        y0 = origin.y

        for _ in range(1, xLen+1):
            error += errorInc
            x0 += xInc
            if error > 0:
                error -= errorReset
                y0 += yInc

            x, y = x0, y0
            if steep:
                x, y = y+xy_diff, x-xy_diff
            if x < 0 or y < 0:
                break
            if x >= map_width or y >= map_height:
                break
            set_vision(x, y)
            if is_block(Vector2(x,y)):
                break
            
        return

    set_vision(origin.x, origin.y)

    for ix in range(0, range_limit*2):
        for iy in range(0, range_limit*2):
            trace_line(origin, origin.x - range_limit + ix, origin.y - range_limit + iy)
    # top and bottom
    # for i in range(0, range_limit*2):
    #     trace_line(origin, origin.x - range_limit + i, origin.y + range_limit)
    # for i in range(0, range_limit*2):
    #     trace_line(origin, origin.x + range_limit - i, origin.y - range_limit)
    # right and left
    # for i in range(0, range_limit*2):
    #     trace_line(origin, origin.x + range_limit, origin.y + range_limit - i)
    # for i in range(0, range_limit*2):
    #     trace_line(origin, origin.x - range_limit, origin.y - range_limit + i)

    return vision


def trace_line(origin, x, y):
    # Bresenham's line algorithm
    result = []

    
    xDiff = x - origin.x
    yDiff = y - origin.y
    xy_diff = origin.x - origin.y
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

    x0 = origin.x
    y0 = origin.y

    for _ in range(1, xLen+1):
        error += errorInc
        x0 += xInc
        if error > 0:
            error -= errorReset
            y0 += yInc

        x, y = x0, y0
        if steep:
            x, y = y+xy_diff, x-xy_diff
        if x < 0 or y < 0:
            break
        result.append(Vector2(x,y))
        
    return result



if __name__ == '__main__':
    from common import MyMatrix

    dungeon = MyMatrix(20, 20)
    dungeon.fillMatrixWithZero()

    pos = Vector2(19, 0)

    vision = ray_casting(dungeon, pos, 4)

    vision[pos] = 0xcc

    print(vision.output())
