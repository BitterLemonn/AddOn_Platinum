# coding=utf-8
import re

from ..QuModLibs.Server import *
from .. import commonConfig
from .. import loggingUtils as logging


class BroadcasterServer(serverApi.GetServerSystemCls()):

    def __init__(self, namespace, name):
        super(BroadcasterServer, self).__init__(namespace, name)

    def BaubleRegister(self, data):
        """
        饰品注册事件
        :param data: {baubleName: str, baubleSlot: str/list, *customTips: str}
        :return:
        """

        baubleName = data["baubleName"]
        baubleSlot = data["baubleSlot"]
        customTips = data.get("customTips", "")
        # 直接设置的自定义提示优先级更高
        if customTips == "":
            comp = serverApi.GetEngineCompFactory().CreateItem(levelId)
            info = comp.GetItemBasicInfo(baubleName, 0)
            customTips = info.get("customTips", "")
        comp = serverApi.GetEngineCompFactory().CreateGame(levelId)
        exist = comp.LookupItemByName(baubleName)

        if not exist:
            logging.error("铂: 物品 {} 不存在,请检查标识符是否正确".format(baubleName))
            return

        if isinstance(baubleSlot, list):
            baubleSlot = tuple(baubleSlot)
            self.__BaubleRegister(baubleName, baubleSlot, customTips)
        else:
            self.__BaubleRegister(baubleName, baubleSlot, customTips)

    @staticmethod
    def __BaubleRegister(baubleName, baubleSlot, customTips):

        if isinstance(baubleSlot, tuple):
            for slot in baubleSlot:
                if slot not in commonConfig.BaubleEnum.__dict__.values():
                    logging.error("铂: 饰品 {} 插槽 {} 不存在,请检查饰品槽位是否正确".format(baubleName, slot))
                    return
        else:
            if baubleSlot not in commonConfig.BaubleEnum.__dict__.values():
                logging.error("铂: 饰品 {} 插槽 {} 不存在,请检查饰品槽位是否正确".format(baubleName, baubleSlot))
                return

        comp = serverApi.GetEngineCompFactory().CreateItem(levelId)
        baseInfo = comp.GetItemBasicInfo(baubleName, 0)
        if baseInfo["maxStackSize"] > 1:
            logging.error("铂: 饰品 {} 最大堆叠数量大于1".format(baubleName))
            return

        if baubleName in commonConfig.BaubleDict:
            logging.error("铂: 饰品 {} 已存在,请勿重复注册".format(baubleName))
            return

        if len(customTips) > 0:
            if isinstance(baubleSlot, tuple):
                commonConfig.BaubleDict[baubleName] = {
                    "baubleSlot": [slot for slot in baubleSlot],
                    "customTips": customTips
                }
            else:
                commonConfig.BaubleDict[baubleName] = {
                    "baubleSlot": [baubleSlot],
                    "customTips": customTips
                }
        else:
            if isinstance(baubleSlot, tuple):
                commonConfig.BaubleDict[baubleName] = {
                    "baubleSlot": [slot for slot in baubleSlot]
                }
            else:
                commonConfig.BaubleDict[baubleName] = {
                    "baubleSlot": [baubleSlot]
                }

        logging.info("铂: 饰品 {} 注册成功".format(baubleName))

    @staticmethod
    def GetPlayerBaubleInfo(playerId):
        """
        获取玩家饰品信息
        :param playerId: 玩家ID
        :return:
        """
        Call(playerId, "GetPlayerBaubleInfo")

    @staticmethod
    def SetPlayerBaubleInfo(playerId, baubleDict):
        """
        设置玩家饰品信息
        :param playerId: 玩家ID
        :param baubleDict: 饰品字典
        :type baubleDict: dict
        :type playerId: str
        :return:
        """
        Call(playerId, "SetPlayerBaubleInfo", baubleDict)

    @staticmethod
    def SetPlayerBaubleInfoWithSlot(playerId, baubleInfo, slotName):
        """
        设置玩家饰品信息
        :param playerId: 玩家ID
        :param baubleInfo: 饰品信息
        :param slotName: 饰品槽位
        :type baubleInfo: dict
        :type playerId: str
        :type slotName: str
        :return:
        """
        Call(playerId, "SetPlayerBaubleInfoWithSlot", baubleInfo, slotName)

    @staticmethod
    def DecreaseBaubleDurability(playerId, slotName, num=1):
        """
        减少饰品耐久度
        :param playerId: 玩家ID
        :param num: 减少的耐久度
        :param slotName: 饰品槽位
        :return:
        """
        Call(playerId, "DecreaseBaubleDurability", num, slotName)


@AllowCall
def BaubleEquipped(data):
    server = serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER)
    server.BroadcastEvent(commonConfig.BAUBLE_EQUIPPED_EVENT, data)


@AllowCall
def BaubleUnequipped(data):
    server = serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER)
    server.BroadcastEvent(commonConfig.BAUBLE_UNEQUIPPED_EVENT, data)


# 接收玩家饰品信息回调
@AllowCall
def OnGetPlayerBaubleInfo(data):
    playerId = data["playerId"]
    baubleDict = data["baubleInfo"]
    server = serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER)
    server.BroadcastEvent(commonConfig.BAUBLE_GET_INFO_EVENT, {"playerId": playerId, "baubleDict": baubleDict})
