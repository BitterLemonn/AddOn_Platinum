# coding=utf-8
from ..QuModLibs.Server import *
from .. import commonConfig
from .. import loggingUtils as logging


class BroadcasterServer(serverApi.GetServerSystemCls()):

    def __init__(self, namespace, name):
        super(BroadcasterServer, self).__init__(namespace, name)

    def BaubleRegister(self, data):
        """
        饰品注册事件
        :param data: {baubleName: str, baubleSlot: str, *customTips: str}
        :return:
        """

        baubleName = data["baubleName"]
        baubleSlot = data["baubleSlot"]
        customTips = data.get("customTips", "")
        comp = serverApi.GetEngineCompFactory().CreateGame(serverApi.GetLevelId())
        exist = comp.LookupItemByName(baubleName)

        if baubleSlot in commonConfig.BaubleEnum.__dict__.values():
            if exist:
                comp = serverApi.GetEngineCompFactory().CreateItem(levelId)
                baseInfo = comp.GetItemBasicInfo(baubleName, 0)
                if baseInfo["maxStackSize"] > 1:
                    logging.error("铂: 饰品 {} 最大堆叠数量大于1".format(baubleName))
                    return

                if baubleName in commonConfig.BaubleDict:
                    logging.error("铂: 饰品 {} 已存在,请勿重复注册".format(baubleName))
                    return

                if len(customTips) > 0:
                    commonConfig.BaubleDict[baubleName] = [baubleSlot, customTips]
                else:
                    commonConfig.BaubleDict[baubleName] = baubleSlot
                logging.info("铂: 饰品 {} 注册成功".format(baubleName))

            else:
                logging.error("铂: 物品 {} 不存在,请检查标识符是否正确".format(baubleName))
        else:
            logging.error("铂: 饰品 {} 插槽 {} 不存在,请检查饰品槽位是否正确".format(baubleName, baubleSlot))

    def GetPlayerBaubleInfo(self, playerId):
        """
        获取玩家饰品信息
        :param playerId: 玩家ID
        :return:
        """
        GetPlayerBaubleInfo(playerId)

    def SetPlayerBaubleInfo(self, playerId, baubleDict):
        """
        设置玩家饰品信息
        :param playerId: 玩家ID
        :param baubleDict: 饰品字典
        :type baubleDict: dict
        :type playerId: str
        :return:
        """
        SetPlayerBaubleInfo(playerId, baubleDict)

    def SetPlayerBaubleInfoWithSlot(self, playerId, baubleInfo, slotName):
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
        SetPlayerBaubleInfoWithSlot(playerId, baubleInfo, slotName)


@AllowCall
def BaubleEquipped(data):
    server = serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER)
    server.BroadcastEvent(commonConfig.BAUBLE_EQUIPPED_EVENT, data)


@AllowCall
def BaubleUnequipped(data):
    server = serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER)
    server.BroadcastEvent(commonConfig.BAUBLE_UNEQUIPPED_EVENT, data)


# 获取玩家饰品信息
def GetPlayerBaubleInfo(playerId):
    Call(playerId, "GetPlayerBaubleInfo")


# 设置玩家饰品信息
def SetPlayerBaubleInfo(playerId, baubleDict):
    Call(playerId, "SetPlayerBaubleInfo", baubleDict)


def SetPlayerBaubleInfoWithSlot(playerId, baubleInfo, slotName):
    Call(playerId, "SetPlayerBaubleInfoWithSlot", baubleInfo, slotName)


# 接收玩家饰品信息回调
@AllowCall
def OnGetPlayerBaubleInfo(data):
    playerId = data["playerId"]
    baubleDict = data["baubleInfo"]
    server = serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER)
    server.BroadcastEvent(commonConfig.BAUBLE_GET_INFO_EVENT, {"playerId": playerId, "baubleDict": baubleDict})
