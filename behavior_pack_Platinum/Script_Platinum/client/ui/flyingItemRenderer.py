# coding=utf-8
if 1 > 2:
    from Script_Platinum.QuModLibs.UI import ScreenNode

from Script_Platinum.data.itemStack import ItemStack
from Script_Platinum.utils import developLogging as logging
from Script_Platinum.QuModLibs.Client import *


# coding=utf-8
class FlyingItemRenderer:

    class FlyingItemParam:
        def __init__(self, itemDict, fromPos, toPos, size):
            self.itemDict = ItemStack.fromDict(itemDict)
            self.fromPos = fromPos
            self.toPos = toPos
            self.size = size

    class _FlyingItemRendererParam:
        def __init__(self):
            self.count = 0
            self.itemParams = []  # type: list[FlyingItemRenderer.FlyingItemParam]

        def createPropertyBag(self, itemComp):
            result = {"flying_item_count": self.count}
            for index, itemParam in enumerate(self.itemParams):
                itemIdAux = itemComp.GetItemBasicInfo(itemParam.itemDict.name, itemParam.itemDict.aux).get("id_aux", 0)
                result["flying_item_id_aux%d" % index] = itemIdAux
                result["flying_item_origin_position_x%d" % index] = itemParam.fromPos[0]
                result["flying_item_origin_position_y%d" % index] = itemParam.fromPos[1]
                result["flying_item_origin_scale%d" % index] = itemParam.size
                result["flying_item_destination_position_x%d" % index] = itemParam.toPos[0]
                result["flying_item_destination_position_y%d" % index] = itemParam.toPos[1]
                result["flying_item_destination_scale%d" % index] = itemParam.size
            return result

    def __init__(self, screen, basePath):
        self.screen = screen  # type: ScreenNode
        self.basePath = basePath
        self.itemComp = compFactory.CreateItem(levelId)

        self.flyingItemRenderer = self.screen.GetBaseUIControl(self.basePath)

    def flyingItem(self, paramList):  # type: (list[FlyingItemParam]) -> None
        """
        开始渲染飞行物品动画
        :type paramList: list
        """
        propertyBag = self._FlyingItemRendererParam()
        for param in paramList:
            propertyBag.itemParams.append(param)
            propertyBag.count += 1
        self.flyingItemRenderer.SetPropertyBag(propertyBag.createPropertyBag(self.itemComp))
