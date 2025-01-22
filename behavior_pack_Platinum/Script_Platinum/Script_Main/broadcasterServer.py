# coding=utf-8
from .. import developLogging as logging

from ..BroadcastEvent.getBaubleSlotInfoEvent import GetGlobalBaubleSlotInfoEvent, GetTargetBaubleSlotInfoEvent
from ..BroadcastEvent.getPlayerBaubleInfoEvent import GetPlayerBaubleInfoServerEvent
from ..QuModLibs.Server import *
from ..QuModLibs.Modules.Services.Server import BaseService
from .. import commonConfig
from .. import oldVersionFixer
from ..DataManager.baubleInfoManager import BaubleInfoManager
from ..DataManager.baubleSlotServerService import BaubleSlotServerService
from ..Script_UI.baubleServer import BaubleServerService


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
        customTips = data.get("customTips", None)
        # 直接设置的自定义提示优先级更高
        if not customTips:
            comp = serverApi.GetEngineCompFactory().CreateItem(levelId)
            info = comp.GetItemBasicInfo(baubleName, 0)
            customTips = info.get("customTips", None)

        if not serverApi.GetEngineCompFactory().CreateGame(levelId).LookupItemByName(baubleName):
            logging.error("铂: 物品 {} 不存在,请检查标识符是否正确".format(baubleName))
            return

        self.__BaubleRegister(baubleName, baubleSlot, customTips)

    def __BaubleRegister(self, baubleName, baubleSlot, customTips):
        baubleSlot = [slot for slot in baubleSlot] if isinstance(baubleSlot, tuple) else baubleSlot if isinstance(
            baubleSlot, list) else [baubleSlot]
        baubleSlot = oldVersionFixer.oldSlotTypeChanger(baubleSlot)

        for slot in baubleSlot:
            if slot not in BaubleSlotServerService.access().getBaubleSlotTypeList():
                logging.error("铂: 饰品 {} 插槽 {} 不存在,请检查饰品槽位是否正确".format(baubleName, slot))
                return

        comp = serverApi.GetEngineCompFactory().CreateItem(levelId)
        baseInfo = comp.GetItemBasicInfo(baubleName, 0)
        if baseInfo["maxStackSize"] > 1:
            logging.error("铂: 饰品 {} 最大堆叠数量大于1".format(baubleName))
            return

        BaubleInfoManager.registerBaubleInfo(baubleName, baubleSlot, customTips)

    @staticmethod
    def GetPlayerBaubleInfo(playerId):
        """
        获取玩家饰品信息
        :param playerId: 玩家ID
        :return:
        """
        BaubleServerService.access().getPlayerBaubleInfo(playerId)

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
        BaubleServerService.access().setBaubleSlotInfo(playerId, baubleDict)

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
        BaubleServerService.access().setBaubleSlotInfoBySlotId(playerId, slotName, baubleInfo)

    @staticmethod
    def DecreaseBaubleDurability(playerId, slotName, num=1):
        """
        减少饰品耐久度
        :param playerId: 玩家ID
        :param num: 减少的耐久度
        :param slotName: 饰品槽位
        :return:
        """
        BaubleServerService.access().decreaseBaubleDurability(playerId, slotName, num)

    @staticmethod
    def AddTargetBaubleSlot(playerId, slotId, slotType, slotName=None, slotPlaceHolderPath=None):
        """
        添加目标饰品槽位
        :param playerId: 玩家ID
        :param slotId: 槽位标识符
        :param slotType: 槽位类型
        :param slotName: 槽位名称
        :param slotPlaceHolderPath: 槽位占位符图片路径
        :return:
        """
        BaubleServerService.access().addTargetBaubleSlot(playerId, slotId, slotType, slotName, slotPlaceHolderPath)

    @staticmethod
    def AddGlobalBaubleSlot(slotId, slotType, slotName=None, slotPlaceHolderPath=None, isDefault=False):
        """
        添加全局饰品槽位
        :param slotId: 槽位标识符
        :param slotType: 槽位类型
        :param slotName: 槽位名称
        :param slotPlaceHolderPath: 槽位占位符图片路径
        :param isDefault: 是否为默认槽位
        :return:
        """
        BaubleServerService.access().addGlobalBaubleSlot(slotId, slotType, slotName, slotPlaceHolderPath, isDefault)

    @staticmethod
    def DeleteTargetBaubleSlot(playerId, slotId):
        """
        删除目标饰品槽位
        :param playerId: 玩家ID
        :param slotId: 槽位标识符
        :return:
        """
        BaubleServerService.access().removeTargetBaubleSlot(playerId, slotId)

    @staticmethod
    def DeleteGlobalBaubleSlot(slotId):
        """
        删除全局饰品槽位
        :param slotId: 槽位标识符
        :return:
        """
        BaubleServerService.access().removeGlobalBaubleSlot(slotId)


@BaseService.Init
class BroadcasterServerService(BaseService):
    def __init__(self):
        BaseService.__init__(self)

    @BaseService.REG_API("platinum/onBaublePutOn")
    def onBaublePutOn(self, data):
        server = serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER)
        server.BroadcastEvent(commonConfig.BAUBLE_EQUIPPED_EVENT, data)

    @BaseService.REG_API("platinum/onBaubleTakeOff")
    def onBaubleTakeOff(self, data):
        server = serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER)
        server.BroadcastEvent(commonConfig.BAUBLE_UNEQUIPPED_EVENT, data)

    @BaseService.ServiceListen(GetPlayerBaubleInfoServerEvent)
    def onGetPlayerBaubleInfo(self, data):
        data = GetPlayerBaubleInfoServerEvent.getData(data)
        playerId = data.playerId
        baubleDict = data.baubleDict
        server = serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER)
        server.BroadcastEvent(commonConfig.BAUBLE_GET_INFO_EVENT, {"playerId": playerId, "baubleDict": baubleDict})

    @BaseService.ServiceListen(GetGlobalBaubleSlotInfoEvent)
    def onGetGlobalBaubleSlotInfo(self, data):
        data = GetGlobalBaubleSlotInfoEvent.getData(data)
        baubleSlotList = data.baubleSlotList
        server = serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER)
        server.BroadcastEvent(commonConfig.BAUBLE_GET_GLOBAL_INFO_EVENT, {"baubleSlotList": baubleSlotList})

    @BaseService.ServiceListen(GetTargetBaubleSlotInfoEvent)
    def onGetPlayerBaubleInfo(self, data):
        data = GetTargetBaubleSlotInfoEvent.getData(data)
        playerId = data.playerId
        baubleSlotList = data.baubleSlotList
        server = serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER)
        server.BroadcastEvent(commonConfig.BAUBLE_GET_TARGET_INFO_EVENT,
                              {"playerId": playerId, "baubleSlotList": baubleSlotList})
