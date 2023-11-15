# -*- coding: utf-8 -*-

class ImageUIControl(object):
    def SetSprite(self, texturePath):
        # type: (str) -> None
        """
        给图片控件换指定贴图
        """
        pass

    def SetSpriteColor(self, color):
        # type: (tuple[float,float,float]) -> None
        """
        设置图片颜色
        """
        pass

    def SetSpriteGray(self, gray):
        # type: (bool) -> None
        """
        给图片控件置灰，比直接SetSprite一张灰图片效率要高
        """
        pass

    def SetSpriteUV(self, uv):
        # type: (tuple[float,float]) -> None
        """
        设置图片的起始uv，与json中的"uv"属性作用一致
        """
        pass

    def SetSpriteUVSize(self, uvSize):
        # type: (tuple[float,float]) -> None
        """
        设置图片的uv大小，与json中的"uv_size"属性作用一致
        """
        pass

    def SetSpriteClipRatio(self, clipRatio):
        # type: (float) -> None
        """
        设置图片的裁剪区域比例（不改变控件尺寸）。可以配合image控件的clip_ratio属性控制方向。
        """
        pass

    def SetSpritePlatformHead(self):
        # type: () -> None
        """
        设置图片为我的世界移动端启动器当前帐号的头像
        """
        pass

    def SetSpritePlatformFrame(self):
        # type: () -> None
        """
        设置图片为我的世界移动端启动器当前帐号的头像框
        """
        pass

    def SetClipDirection(self, clipDirection):
        # type: (str) -> bool
        """
        设置图片控件的裁剪方向
        """
        pass

    def GetClipDirection(self):
        # type: () -> str
        """
        获取图片控件的裁剪方向
        """
        pass

    def SetImageAdaptionType(self, imageAdaptionType, imageAdaptionData=None):
        # type: (str, tuple[float,float,float,float]) -> bool
        """
        设置图片控件的图片适配方式以及信息
        """
        pass

    def Rotate(self, angle):
        # type: (float) -> None
        """
        图片相对自身的旋转锚点进行旋转
        """
        pass

    def RotateAround(self, point, angle):
        # type: (tuple[float,float], float) -> None
        """
        图片相对全局坐标系中某个固定的点进行旋转
        """
        pass

    def SetRotatePivot(self, pivot):
        # type: (tuple[float,float]) -> None
        """
        设置图片自身旋转锚点，该点并不是固定的点，而是相对于自身位置的点
        """
        pass

    def GetRotatePivot(self):
        # type: () -> tuple[float,float]
        """
        获取图片相对自身的旋转锚点
        """
        pass

    def GetRotateAngle(self):
        # type: () -> float
        """
        获取图片相对自身的旋转锚点旋转的角度
        """
        pass

    def GetGlobalRotateAngle(self):
        # type: () -> float
        """
        获取图片通过RotateAround函数设置进去的角度值
        """
        pass

    def GetGlobalRotatePoint(self):
        # type: () -> tuple[float,float]
        """
        获取图片通过RotateAround函数设置进去的point值
        """
        pass

    def GetRotateRect(self):
        # type: () -> tuple[tuple[float,float],tuple[float,float],tuple[float,float],tuple[float,float]]
        """
        获取图片当前的四个边角点
        """
        pass


