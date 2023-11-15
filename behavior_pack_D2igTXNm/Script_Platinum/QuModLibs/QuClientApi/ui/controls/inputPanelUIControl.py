# -*- coding: utf-8 -*-

class InputPanelUIControl(object):
    def SetIsModal(self, isModal):
        # type: (bool) -> bool
        """
        设置当前面板是否为模态框
        """
        pass

    def GetIsModal(self):
        # type: () -> bool
        """
        判断当前面板是否为模态框
        """
        pass

    def SetIsSwallow(self, isSwallow):
        # type: (bool) -> bool
        """
        设置当前面板输入是否会吞噬事件，isSwallow为Ture时，点击时，点击事件不会穿透到世界。如破坏方块、镜头转向不会被响应
        """
        pass

    def GetIsSwallow(self):
        # type: () -> bool
        """
        判断当前面板输入是否会吞噬事件，isSwallow为Ture时，点击时，点击事件不会穿透到世界。如破坏方块、镜头转向不会被响应
        """
        pass

    def SetOffsetDelta(self, offset_delta):
        # type: (tuple[float,float]) -> bool
        """
        设置点击面板的拖拽偏移量
        """
        pass

    def GetOffsetDelta(self):
        # type: () -> tuple[float,float]
        """
        获得点击面板的拖拽偏移量
        """
        pass

