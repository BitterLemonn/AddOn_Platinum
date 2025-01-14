# coding=utf-8
import logging
from ..QuModLibs.Client import *

if 0 > 1:
    from mod.client.ui.screenNode import ScreenNode
    from mod.client.ui.controls.baseUIControl import BaseUIControl


# coding=utf-8
class FlyingItemRenderer:
    __FLYING_ITEM_DEF = "bauble_reborn.flying_item"

    def __init__(self, screen, basePath):
        self.flyingTime = 5  # 帧

        self.screen = screen  # type: ScreenNode
        self.basePath = basePath

        self.flyingItemPanel = self.screen.GetBaseUIControl(self.basePath)

        self.flyingPool = []  # type: list[BaseUIControl]
        self.flyingUsing = []  # type: list[BaseUIControl]

    def OnDestroy(self):
        for flyingRender in self.flyingPool:
            self.screen.RemoveChildControl(flyingRender)
        for flyingRender in self.flyingBigPool:
            self.screen.RemoveChildControl(flyingRender)

    def __CreateFlying(self, size):
        count = len(self.flyingPool)
        flyingItem = self.screen.CreateChildControl(self.__FLYING_ITEM_DEF, "flying_item{}".format(count),
                                                    self.flyingItemPanel).asItemRenderer()
        flyingItem.SetVisible(False)
        flyingItem.SetAnchorFrom("top_left")
        flyingItem.SetAnchorTo("top_left")
        flyingItem.SetSize(size)
        self.flyingPool.append(flyingItem)
        return flyingItem

    def FlyingItem(self, itemDict, fromPos, toPos, size=None):
        """
        开始渲染飞行物品动画
        :type itemDict: dict
        :param itemDict: 物品信息字典
        :type fromPos: list
        :param fromPos: 开始位置(左上)
        :type toPos: list
        :param toPos: 结束位置(左上)
        :type size: tuple
        :param size: 大小(默认为18, 18)
        :return:
        """
        itemRender = None

        if size is None:
            size = (18, 18)
        for flyingRender in self.flyingPool:
            if flyingRender not in self.flyingUsing:
                itemRender = flyingRender
                itemRender.SetSize(size)
                break

        if not itemRender:
            itemRender = self.__CreateFlying(size)

        self.flyingUsing.append(itemRender)
        itemRender.SetUiItem(itemDict["newItemName"], itemDict["newAuxValue"], False, itemDict.get("userData"))
        self.__StartFlying(itemRender, fromPos, toPos)

    def __StartFlying(self, itemRender, fromPos, toPos):
        flyingPanelOffset = self.flyingItemPanel.GetGlobalPosition()
        fromPos = [fromPos[0] - flyingPanelOffset[0], fromPos[1] - flyingPanelOffset[1]]
        toPos = [toPos[0] - flyingPanelOffset[0], toPos[1] - flyingPanelOffset[1]]

        offsetAnimateData = {
            "namespace": "PlatinumFlyingItem",
            "flying_animation": {
                "anim_type": "offset",
                "duration": self.flyingTime / 30.0,
                "from": fromPos,
                "to": toPos
            }
        }
        clientApi.RegisterUIAnimations(offsetAnimateData, True)
        itemRender.SetVisible(True)
        itemRender.SetAnimation("offset", "PlatinumFlyingItem", "flying_animation", True)

        comp = clientApi.GetEngineCompFactory().CreateGame(levelId)
        comp.AddTimer(self.flyingTime / 30.0, self.__EndFlying, itemRender)

    def __EndFlying(self, itemRender):
        itemRender.SetVisible(False)
        itemRender.RemoveAnimation("offset")
        if itemRender in self.flyingUsing:
            self.flyingUsing.remove(itemRender)
