# coding=utf-8
# 计算向量长度
import math
import logging
from math import *
from mod.common import minecraftEnum


def normalizeVector(vector):
    """
    将向量归一化
    :param vector: 向量
    :return: 归一化后的向量
    """
    length = sqrt(sum(coord ** 2 for coord in vector))
    return (coord / length for coord in vector)


def findPointBehind(posXZ, sight, distance):  # type: (tuple, tuple, float) -> tuple[int, int]
    dir_x, dir_y = normalizeVector(sight)
    new_x = posXZ[0] - dir_x * distance
    new_y = posXZ[1] - dir_y * distance
    return int(new_x), int(new_y)


def isInChunk(pos, chunk):
    chunkIndexX, chunkIndexZ = chunk
    return chunkIndexX * 16 <= pos[0] < chunkIndexX * 16 + 15 and chunkIndexZ * 16 <= pos[2] < chunkIndexZ * 16 + 15


def rotateVectorY(vector, angle_degrees):
    """
    以y轴为旋转轴旋转向量
    :param vector: 向量
    :param angle_degrees: 旋转角度
    :return: 旋转后的向量
    """
    angle_radians = radians(angle_degrees)
    x = vector[0] * cos(angle_radians) - vector[2] * sin(angle_radians)
    z = vector[0] * sin(angle_radians) + vector[2] * cos(angle_radians)
    return x, vector[1], z


def rotateVectorX(vector, angle_degrees):
    """
    以x轴为旋转轴旋转向量
    :param vector: 向量
    :param angle_degrees: 旋转角度
    :return: 旋转后的向量
    """
    angle_radians = radians(angle_degrees)
    y = vector[1] * cos(angle_radians) - vector[2] * sin(angle_radians)
    z = vector[1] * sin(angle_radians) + vector[2] * cos(angle_radians)
    return vector[0], y, z


def unitVector(fromPos, toPos):
    """
    计算fromPos到toPos两点之间的单位向量
    :param fromPos:
    :param toPos:
    :return: 单位向量 (x, y, z)
    """
    delta_x = toPos[0] - fromPos[0]
    delta_y = toPos[1] - fromPos[1]
    delta_z = toPos[2] - fromPos[2]
    magnitude = sqrt(delta_x ** 2 + delta_y ** 2 + delta_z ** 2)
    return delta_x / magnitude, delta_y / magnitude, delta_z / magnitude


def getAngleBetweenVectors(v1, v2, isDismissY=False):
    """
    计算两个单位向量之间的夹角
    :param v1: 单位向量1
    :param v2: 单位向量2
    :param isDismissY: 是否忽略y轴
    :return: 夹角 弧度
    """
    if isDismissY:
        v1 = (v1[0], 0, v1[2])
        v2 = (v2[0], 0, v2[2])
    dot_product = sum(v1[i] * v2[i] for i in range(3))
    mod_product = sqrt(sum(v1[i] ** 2 for i in range(3)) * sum(v2[i] ** 2 for i in range(3)))
    cos_angle = dot_product / mod_product
    return acos(cos_angle)


def isFrontOf(p1, p2, sight):
    """
    判断p2是否在p1的视线前方
    :param p1: 视线起点
    :param p2: 目标点
    :param sight: 视线方向
    :return: 是否在视线前方
    """
    return sum((p2[i] - p1[i]) * sight[i] for i in range(3)) > 0


def getIntPos(floatPos):
    """
    将浮点坐标转换为整数坐标
    """
    return int(floor(floatPos[0])), int(floor(floatPos[1])), int(floor(floatPos[2]))


def getDistance(p1, p2):
    return sqrt(sum((p1[i] - p2[i]) ** 2 for i in range(3)))


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def getChunkCenter(x, z):
    chunkX = (x // 16) * 16 + 8
    chunkZ = (z // 16) * 16 + 8
    return chunkX, chunkZ


def getRGBFloatByStr(colorStr):
    colorStr = colorStr[1:]
    r = int(colorStr[0:2], 16) / 255.0
    g = int(colorStr[2:4], 16) / 255.0
    b = int(colorStr[4:6], 16) / 255.0
    return r, g, b


def getPosFromFacing(pos, facing):
    """
    根据方向获取目标坐标
    :type pos: tuple[int, int, int]
    :param pos: 原坐标
    :param facing: 方向
    :return: 目标坐标
    """
    x, y, z = pos
    if facing == minecraftEnum.Facing.Up:
        y += 1
    elif facing == minecraftEnum.Facing.Down:
        y -= 1
    elif facing == minecraftEnum.Facing.North:
        z -= 1
    elif facing == minecraftEnum.Facing.South:
        z += 1
    elif facing == minecraftEnum.Facing.West:
        x -= 1
    elif facing == minecraftEnum.Facing.East:
        x += 1
    return x, y, z


def getFacingFromPos(pos, targetPos):
    """
    根据坐标获取方向
    :type pos: tuple[int, int, int]
    :type targetPos: tuple[int, int, int]
    :param pos: 当前坐标
    :param targetPos: 目标坐标
    :return: 目标在当前坐标的方向
    """
    x, y, z = pos
    targetX, targetY, targetZ = targetPos
    if targetX > x:
        return minecraftEnum.Facing.East
    elif targetX < x:
        return minecraftEnum.Facing.West
    elif targetZ > z:
        return minecraftEnum.Facing.South
    elif targetZ < z:
        return minecraftEnum.Facing.North
    elif targetY > y:
        return minecraftEnum.Facing.Up
    elif targetY < y:
        return minecraftEnum.Facing.Down
    return None
