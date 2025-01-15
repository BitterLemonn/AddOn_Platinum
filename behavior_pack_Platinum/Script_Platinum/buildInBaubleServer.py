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
        # 测试事件
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
                            "ServerChatEvent", self, self.onServerChatEvent)

    def onClientLoadAddonsFinish(self, data):
        """
        客户端加载模组完毕事件
        """
        travelerBelt = {
            "baubleName": "lemon_platinum:traveler_belt",
            "baubleSlot": BaubleEnum.BELT
        }
        testHelmet = {
            "baubleName": "minecraft:diamond_helmet",
            "baubleSlot": BaubleEnum.HELMET
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

    def onBaubleInfoEvent(self, data):
        logging.debug("铂 测试: 玩家饰品栏数据: {}".format(data))

    def onServerChatEvent(self, data):
        playerId = data["playerId"]
        msg = data["message"]
        if msg.startswith("#platinum_"):
            msg = msg.replace("#platinum_", "")
            if msg == "info":
                data["cancel"] = True
                serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE,
                                    commonConfig.PLATINUM_BROADCAST_SERVER).GetPlayerBaubleInfo(playerId)
            elif msg == "set":
                data["cancel"] = True
                serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE,
                                    commonConfig.PLATINUM_BROADCAST_SERVER).SetPlayerBaubleInfo(
                    playerId,
                    {"bauble_belt": {"newItemName": "lemon_platinum:traveler_belt", "count": 1, "newAuxValue": 0}})
            elif msg == "add":
                data["cancel"] = True
                serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE,
                                    commonConfig.PLATINUM_BROADCAST_SERVER).SetPlayerBaubleInfoWithSlot(
                    playerId,
                    {"newItemName": "lemon_platinum:traveler_belt", "count": 1, "newAuxValue": 0},
                    "bauble_belt")
            elif msg == "dec":
                data["cancel"] = True
                serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE,
                                    commonConfig.PLATINUM_BROADCAST_SERVER).DecreaseBaubleDurability(playerId,
                                                                                                     "bauble_helmet", 100)
