# coding=utf-8
from mod.server import extraServerApi as serverApi
from Script_Platinum.data.eventData import BaubleInfoData
from Script_Platinum.data.slotData import BaubleSlotData
from Script_Platinum.server.registry.baubleRegistry import BaubleRegistry
from Script_Platinum.server.registry.slotRegistry import SlotRegistry
from Script_Platinum.utils import developLogging as logging


class BroadcasterServer(serverApi.GetServerSystemCls()):

    def __init__(self, namespace, name):
        super(BroadcasterServer, self).__init__(namespace, name)
        self.baubleRegistry = BaubleRegistry()
        self.slotRegistry = SlotRegistry()

    def BaubleRegister(self, data):
        """
        饰品注册事件
        :param data: {baubleName: str, baubleSlot: str/list, *customTips: str}
        :return:
        """
        if not data.get("baubleName", None) or not data.get("baubleSlot", None):
            logging.error("铂: 饰品注册事件缺少必要参数, 请检查是否正确传入baubleName和baubleSlot")
            return
        baubleData = BaubleInfoData(data["baubleName"], data["baubleSlot"], data.get("customTips", None))
        self.baubleRegistry.registerBauble(baubleData)

    def AddGlobalBaubleSlot(self, slotId, slotType, slotName=None, slotPlaceHolderPath=None, isDefault=False):
        """
        添加全局饰品槽位
        :param slotId: 槽位标识符
        :param slotType: 槽位类型
        :param slotName: 槽位名称
        :param slotPlaceHolderPath: 槽位占位符图片路径
        :param isDefault: 是否为默认槽位
        :return:
        """
        baubleSlotData = BaubleSlotData(slotName, slotPlaceHolderPath, slotId, slotType, isDefault)
        self.slotRegistry.registerSlot(baubleSlotData)
