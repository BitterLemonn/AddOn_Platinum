# -*- coding: utf-8 -*-
from Util import Math

class Vec3(object):
    """ QuMod Vec3向量类 用于描述坐标/向量
        PS: Vec3的方法大多是自我操作并返回self的链式设计 如需产生新的对象请使用克隆方法
    """
    def __init__(self, x = 0.0, y = 0.0, z = 0.0):
        self._disableUpdate = False
        self._tuple = None      # type: tuple
        self.x = x
        self.y = y
        self.z = z
        self._upDate()

    def getTuple(self):
        # type: () -> tuple[float, float, float]
        """ 获取元组 """
        return self._tuple
    
    def _upDate(self):
        """ 刷新Tuple资源 """
        self._tuple = (self.x, self.y, self.z)
    
    def __getitem__(self, index):
        return self._tuple[index]

    def __setitem__(self, index, value):
        if index >= len(self):
            raise Exception("索引错误 {} 无效的坐标系".format(index))
        elif not (isinstance(value, int) or isinstance(value, float)):
            raise Exception(str(value)+" 不是有效的数值")
        setattr(self, chr(120 - index), value)
        self._upDate()
    
    def __setattr__(self, __name, __value):
        attrTuple = ("x", "y", "z")
        if __name in attrTuple and all(hasattr(self, x) for x in attrTuple):
            if not (isinstance(__value, int) or isinstance(__value, float)):
                raise Exception(str(__value)+" 无效")
            object.__setattr__(self, __name, __value)
            if self._disableUpdate:
                return
            self._upDate()
        return object.__setattr__(self, __name, __value)

    def __len__(self):
        return 3

    def __str__(self):
        return "<{} {}>".format(self.__class__.__name__, self._tuple.__str__())
    
    @staticmethod
    def tupleToVec(tuple):
        # type: (tuple[float | int]) -> Vec3
        """ 将元组转换到Vec """
        return Vec3(*tuple)

    def copy(self):
        # type: () -> Vec3
        """ 拷贝一份新的Vec3对象 """
        return Vec3(self.x, self.y, self.z)
    
    def getLength(self):
        # type: () -> float
        """ 获取向量的长度 """
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5
    
    def convertToUnitVector(self):
        # type: () -> Vec3
        """ 转换为单位向量 返回self """
        length = self.getLength()
        self._disableUpdate = True
        self.x = self.x / length
        self.y = self.y / length
        self.z = self.z / length
        self._disableUpdate = False
        self._upDate()
        return self

    def addVec(self, nextVec3):
        # type: (Vec3) -> Vec3
        """ 向量加法运算 返回self """
        self._disableUpdate = True
        self.x += nextVec3.x
        self.y += nextVec3.y
        self.z += nextVec3.z
        self._disableUpdate = False
        self._upDate()
        return self
    
    def vectorSubtraction(self, nextVec3):
        # type: (Vec3) -> Vec3
        """ 向量减法运算 返回self """
        self._disableUpdate = True
        self.x -= nextVec3.x
        self.y -= nextVec3.y
        self.z -= nextVec3.z
        self._disableUpdate = False
        self._upDate()
        return self
    
    def addTuple(self, nextTuple):
        # type: (tuple[float, float, float]) -> Vec3
        """ 向量加法运算 使用元组 """
        return self.addVec(Vec3.tupleToVec(nextTuple))

    def multiplyOf(self, mutNumber):
        # type: (int | float) -> Vec3
        """ 向量乘法运算 返回self """
        self._disableUpdate = True
        self.x *= mutNumber
        self.y *= mutNumber
        self.z *= mutNumber
        self._disableUpdate = False
        self._upDate()
        return self

    def rotateVector(self, axis, angle):
        # type: (Vec3, float) -> Vec3
        """ 向量旋转
            @axis: 旋转轴(单位向量)
            @angle: 旋转角度(欧拉角)
            @return: self
        """
        import math
        angleRad = math.radians(angle)
        # 计算旋转矩阵分量
        cosTheta = math.cos(angleRad)
        sin_theta = math.sin(angleRad)
        ux, uy, uz = axis.copy().convertToUnitVector()
        vector = self
        # 根据旋转公式计算旋转
        self._disableUpdate = True
        self.x = (cosTheta + (1 - cosTheta) * ux**2) * vector[0] + ((1 - cosTheta) * ux * uy - sin_theta * uz) * vector[1] + ((1 - cosTheta) * ux * uz + sin_theta * uy) * vector[2]
        self.y = (cosTheta + (1 - cosTheta) * uy**2) * vector[1] + ((1 - cosTheta) * ux * uy + sin_theta * uz) * vector[0] + ((1 - cosTheta) * uy * uz - sin_theta * ux) * vector[2]
        self.z = (cosTheta + (1 - cosTheta) * uz**2) * vector[2] + ((1 - cosTheta) * ux * uz - sin_theta * uy) * vector[0] + ((1 - cosTheta) * uy * uz + sin_theta * ux) * vector[1]
        self._disableUpdate = False
        self._upDate()
        return self


class Vec2(Vec3):
    """ QuMod Vec2向量类 用于描述2D坐标/2D向量/2D旋转 继承于Vec3 """
    def __init__(self, x = 0, y = 0):
        Vec3.__init__(self, x, y, 0)

    def __len__(self):
        return 2

    def _upDate(self):
        """ 刷新Tuple资源 """
        self._tuple = (self.x, self.y)

    @staticmethod
    def tupleToVec(tuple):
        # type: (tuple[float | int]) -> Vec2
        """ 将元组转换到Vec """
        return Vec2(*tuple)

    def copy(self):
        # type: () -> Vec2
        """ 拷贝一份新的Vec2对象 """
        return Vec2(self.x, self.y)