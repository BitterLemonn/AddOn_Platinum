# coding=UTF-8
from Script_Platinum.QuModLibs.Server import *
from Script_Platinum.data.eventData import BaubleInfoData
from Script_Platinum.data.itemStack import ItemStack
from Script_Platinum.utils.serverUtils import compFactory
from Script_Platinum.utils import developLogging as logging


class BaubleRegistry(object):

    INSTANCE = None

    def __new__(cls):
        if cls.INSTANCE is None:
            cls.INSTANCE = super(BaubleRegistry, cls).__new__(cls)
            cls.INSTANCE.baubles = {}  # 饰品信息字典, key: baubleId, value: {"slot": str/list, "customTips": str}
        return cls.INSTANCE

    def isValidBauble(self, baubleId, slotType):
        """判断饰品是否适合某个槽位"""
        if baubleId not in self.baubles:
            return False
        baubleInfo = self.baubles[baubleId]
        return slotType in baubleInfo["slot"]

    def getBaubleInfo(self, baubleId):  # type: (str) -> dict|None
        """获取饰品信息"""
        return self.baubles.get(baubleId, None)

    def registerBauble(self, data):  # type: (BaubleInfoData) -> bool
        """
        注册饰品(对外接口)
        :param data: {baubleName: str, baubleSlot: str/list, *customTips: str}
        """
        if not compFactory.CreateGame(levelId).LookupItemByName(data.baubleId):
            logging.error("铂: 物品 {} 不存在, 请检查标识符是否正确".format(data.baubleId))
            return False
        if ItemStack(data.baubleId, 1).maxStackSize > 1:
            logging.error("铂: 饰品 {} 的最大堆叠数大于1, 无法注册为饰品".format(data.baubleId))
            return False
        # 直接设置的自定义提示优先级更高
        if not data.customTips:
            comp = compFactory.CreateItem(levelId)
            info = comp.GetItemBasicInfo(data.baubleId, 0)
            data.customTips = info.get("customTips", None)

        return self._registerBauble(data.baubleId, data.slotType, data.customTips)

    def _registerBauble(self, baubleName, baubleSlot, customTips):  # type: (str, str|list[str], str) -> bool
        """
        注册饰品(内部接口)
        :param baubleName: 饰品名称
        :param baubleSlot: 饰品槽位
        :param customTips: 自定义提示
        :return: 是否注册成功
        """
        if baubleName in self.baubles:
            logging.error("铂: 饰品 {} 已注册, 请勿重复注册".format(baubleName))
            return False
        baubleSlot = baubleSlot if isinstance(baubleSlot, list) else [baubleSlot]
        self.baubles[baubleName] = {"slot": baubleSlot, "customTips": customTips}
        logging.success("铂: 饰品 {} 注册成功".format(baubleName))
        return True
