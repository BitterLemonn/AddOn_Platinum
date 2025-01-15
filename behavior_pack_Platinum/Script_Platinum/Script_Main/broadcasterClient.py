# coding=utf-8
from ..QuModLibs.Client import *
from ..QuModLibs.Modules.Services.Client import BaseService, QRequests
from .. import commonConfig
from ..Script_UI.baubleClient import BaubleBroadcastService


class BroadcasterClient(clientApi.GetClientSystemCls()):

    def __init__(self, namespace, name):
        super(BroadcasterClient, self).__init__(namespace, name)

    @staticmethod
    def GetBaubleInfo():
        """
        获取玩家饰品信息
        """
        BroadcasterClientService.access().onGetBaubleInfo(BaubleBroadcastService.access().getBaubleInfo())

    @staticmethod
    def SetBaubleInfo(baubleDict):
        """
        设置玩家饰品信息
        :param baubleDict: dict
        """
        BaubleBroadcastService.access().setBaubleInfo(baubleDict)

    @staticmethod
    def SetPlayerBaubleInfoWithSlot(baubleInfo, slotName):
        """
        设置玩家饰品信息
        :param baubleInfo: dict
        :param slotName: str
        """
        BaubleBroadcastService.access().setPlayerBaubleInfoWithSlot(baubleInfo, slotName)

    @staticmethod
    def DecreaseBaubleDurability(slotName, decrease=1):
        """
        减少饰品耐久度
        :param slotName: str
        :param decrease: int
        """
        BaubleBroadcastService.access().decreaseBaubleDurability(slotName, decrease)


@BaseService.Init
class BroadcasterClientService(BaseService):

    def __init__(self):
        BaseService.__init__(self)

    @BaseService.REG_API("platinum/onBaubleTakeOff")
    def onBaubleTakeOff(self, data):
        client = clientApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_CLIENT)
        client.BroadcastEvent(commonConfig.BAUBLE_UNEQUIPPED_EVENT, data)

    @BaseService.REG_API("platinum/onBaublePutOn")
    def onBaublePutOn(self, data):
        client = clientApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_CLIENT)
        client.BroadcastEvent(commonConfig.BAUBLE_EQUIPPED_EVENT, data)

    def onGetBaubleInfo(self, data):
        baubleDict = data["baubleDict"]
        client = clientApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_CLIENT)
        client.BroadcastEvent(commonConfig.BAUBLE_GET_INFO_EVENT, {"baubleDict": baubleDict})
