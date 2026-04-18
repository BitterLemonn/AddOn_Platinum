# coding=utf-8
from mod.server import extraServerApi as serverApi

from Script_Platinum import commonConfig
from Script_Platinum.utils.serverUtils import compFactory


class BaubleServer(serverApi.GetServerSystemCls()):

    def __init__(self, namespace, systemName):
        super(BaubleServer, self).__init__(namespace, systemName)
        self.listenEvent()

    def listenEvent(self):
        self.ListenForEvent(
            commonConfig.PLATINUM_NAMESPACE,
            commonConfig.PLATINUM_BROADCAST_SERVER,
            commonConfig.BAUBLE_EQUIPPED_EVENT,
            self,
            self.onBaubleEquipped,
        )
        self.ListenForEvent(
            commonConfig.PLATINUM_NAMESPACE,
            commonConfig.PLATINUM_BROADCAST_SERVER,
            commonConfig.BAUBLE_UNEQUIPPED_EVENT,
            self,
            self.onBaubleUnequipped,
        )

    def onBaubleEquipped(self, data):
        """
        饰品装备事件
        :param data: {"slotIndex": Int, "playerId": str, "isFirstLoad": bool, "baubleSlot": str, "baubleSlotId": str "itemDict": dict}
        """
        playerId = data["playerId"]  # 玩家ID
        bauble = data["itemDict"]  # 饰品信息
        isFirstLoad = data["isFirstLoad"]  # 是否是第一次加载
        slot = data["baubleSlot"]  # 饰品槽名称(旧版)
        slotId = data["baubleSlotId"]  # 饰品槽ID
        slotIndex = data["slotIndex"]  # 饰品槽索引
        if bauble["newItemName"] == "lemon_platinum:traveler_belt":
            comp = compFactory.CreateAttr(playerId)
            comp.SetStepHeight(1.0625)

    def onBaubleUnequipped(self, data):
        """
        饰品脱落事件
        :param data: {"slotIndex": Int, "playerId": str, "baubleSlot": str, "baubleSlotId": str "itemDict": dict}
        """
        playerId = data["playerId"]  # 玩家ID
        bauble = data["itemDict"]  # 饰品信息
        slot = data["baubleSlot"]  # 饰品槽名称(旧版)
        slotId = data["baubleSlotId"]  # 饰品槽ID
        slotIndex = data["slotIndex"]  # 饰品槽索引
        if bauble["newItemName"] == "lemon_platinum:traveler_belt":
            comp = compFactory.CreateAttr(playerId)
            comp.SetStepHeight(0.5626)
