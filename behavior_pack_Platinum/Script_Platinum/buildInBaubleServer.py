# coding=utf-8
import logging

import commonConfig
import mod.server.extraServerApi as serverApi
from commonConfig import BaubleEnum


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
        # 监听模组加载完毕事件
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
                            "ClientLoadAddonsFinishServerEvent", self, self.onClientLoadAddonsFinish)
        # 监听玩家饰品栏信息回调
        self.ListenForEvent(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER,
                            commonConfig.BAUBLE_GET_INFO_EVENT, self, self.onBaubleInfoEvent)

    def onBaubleInfoEvent(self, data):
        pass

    def onClientLoadAddonsFinish(self, data):
        """
        客户端加载模组完毕事件
        """
        serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE,
                            commonConfig.PLATINUM_BROADCAST_SERVER).AddGlobalBaubleSlot(
            "test_helmet", "test_helmet", "测试头盔", "textures/ui/bauble_helmet_slot", True
        )
        travelerBelt = {
            "baubleName": "lemon_platinum:traveler_belt",
            "baubleSlot": BaubleEnum.BELT
        }
        testHelmet = {
            "baubleName": "minecraft:diamond_helmet",
            "baubleSlot": "test_helmet"
        }
        serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE,
                            commonConfig.PLATINUM_BROADCAST_SERVER).BaubleRegister(travelerBelt)
        serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE,
                            commonConfig.PLATINUM_BROADCAST_SERVER).BaubleRegister(testHelmet)

    def onBaubleEquipped(self, data):
        """
        饰品装备事件
        :param data: {playerId: str, itemDict: dict, baubleSlot: str, slotIndex: int}
        """
        playerId = data["playerId"]
        bauble = data["itemDict"]
        slot = data["baubleSlot"]
        slotIndex = data["slotIndex"]

        if bauble["newItemName"] == "lemon_platinum:traveler_belt":
            comp = serverApi.GetEngineCompFactory().CreateAttr(playerId)
            comp.SetStepHeight(1.0625)
        elif bauble["newItemName"] == "minecraft:diamond_helmet":
            system = serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER)
            system.AddTargetBaubleSlot(playerId, "test_helmet2", "test_helmet")

    def onBaubleUnequipped(self, data):
        """
        饰品卸下事件
        :param data: {playerId: str, itemDict: dict, baubleSlot: str, slotIndex: int}
        :return:
        """
        playerId = data["playerId"]
        bauble = data["itemDict"]
        slot = data["baubleSlot"]
        slotIndex = data["slotIndex"]

        if bauble["newItemName"] == "lemon_platinum:traveler_belt":
            comp = serverApi.GetEngineCompFactory().CreateAttr(playerId)
            comp.SetStepHeight(0.5626)
        elif bauble["newItemName"] == "minecraft:diamond_helmet":
            system = serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER)
            system.DeleteTargetBaubleSlot(playerId, "test_helmet2")
