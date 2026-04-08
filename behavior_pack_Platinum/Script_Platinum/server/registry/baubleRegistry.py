# coding=UTF-8
from Script_Platinum.QuModLibs.Server import *
from Script_Platinum.utils.serverUtils import compFactory
from Script_Platinum.utils import developLogging as logging


class BaubleRegistry(object):

    INSTANCE = None

    def __new__(cls):
        if cls.INSTANCE is None:
            cls.INSTANCE = super(BaubleRegistry, cls).__new__(cls)
            cls.INSTANCE.baubles = {}
        return cls.INSTANCE

    def registerBauble(self, data):  # type: (dict[str, str|list[str], str]) -> bool
        """
        注册饰品(对外接口)
        :param data: {baubleName: str, baubleSlot: str/list, *customTips: str}
        """
        baubleName = data.get("baubleName", None)
        baubleSlot = data.get("baubleSlot", None)
        customTips = data.get("customTips", None)
        # 直接设置的自定义提示优先级更高
        if not customTips:
            comp = compFactory.CreateItem(levelId)
            info = comp.GetItemBasicInfo(baubleName, 0)
            customTips = info.get("customTips", None)

        if not compFactory.CreateGame(levelId).LookupItemByName(baubleName):
            logging.error("铂: 物品 {} 不存在,请检查标识符是否正确".format(baubleName))
            return False
        return self._registerBauble(baubleName, baubleSlot, customTips)

    def _registerBauble(self, baubleName, baubleSlot, customTips):  # type: (str, str|list[str], str) -> bool
        """
        注册饰品(内部接口)
        :param baubleName: 饰品名称
        :param baubleSlot: 饰品槽位
        :param customTips: 自定义提示
        :return: 是否注册成功
        """
        if baubleName in self.baubles:
            logging.error("铂: 物品 {} 已注册, 请勿重复注册".format(baubleName))
            return False
        baubleSlot = baubleSlot if isinstance(baubleSlot, list) else [baubleSlot]
        self.baubles[baubleName] = {"slot": baubleSlot, "customTips": customTips}
        logging.info("铂: 物品 {} 注册成功".format(baubleName))
        return True
