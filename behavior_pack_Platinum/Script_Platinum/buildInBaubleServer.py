# coding=utf-8
import loggingUtils as logging

import commonConfig
import mod.server.extraServerApi as serverApi


class BuildInBaubleServer(serverApi.GetServerSystemCls()):

    def __init__(self, namespace, name):
        super(BuildInBaubleServer, self).__init__(namespace, name)
        self.listenEvent()

    def listenEvent(self):
        # 监听饰品装备事件
        self.ListenForEvent(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER,
                            commonConfig.BAUBLE_EQUIPPED_EVENT, self, self.onBaubleEquipped)
        # 监听饰品卸下事件
        self.ListenForEvent(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER,
                            commonConfig.BAUBLE_UNEQUIPPED_EVENT, self, self.onBaubleUnequipped)

    def onBaubleEquipped(self, data):
        """
        饰品装备事件
        :param data: {playerId: str, itemDict: dict, baubleSlot: str}
        """
        playerId = data["playerId"]
        bauble = data["itemDict"]
        slot = data["baubleSlot"]

        if bauble["newItemName"] == "lemon_platinum:traveler_belt":
            comp = serverApi.GetEngineCompFactory().CreateAttr(playerId)
            comp.SetStepHeight(1.0625)

    def onBaubleUnequipped(self, data):
        """
        饰品卸下事件
        :param data: {playerId: str, itemDict: dict, baubleSlot: str}
        :return:
        """
        playerId = data["playerId"]
        bauble = data["itemDict"]
        slot = data["baubleSlot"]

        if bauble["newItemName"] == "lemon_platinum:traveler_belt":
            comp = serverApi.GetEngineCompFactory().CreateAttr(playerId)
            comp.SetStepHeight(0.5626)
