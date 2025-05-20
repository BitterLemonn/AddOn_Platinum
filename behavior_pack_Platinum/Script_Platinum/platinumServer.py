# coding=utf-8
class PlatinumServer():
    def BaubleRegister(self, data):
        """
        饰品注册事件
        :param data: {baubleName: str, baubleSlot: str/list, *customTips: str}
        :type data: dict
        :return: None
        """
        pass

    @staticmethod
    def GetPlayerBaubleInfo(playerId):
        """
        获取玩家饰品信息
        :param playerId: 玩家ID
        :type playerId: str
        :return: None
        """
        pass

    @staticmethod
    def SetPlayerBaubleInfo(playerId, baubleDict):
        """
        设置玩家饰品信息
        :param playerId: 玩家ID
        :param baubleDict: 饰品字典
        :type baubleDict: dict
        :type playerId: str
        :return: None
        """
        pass

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
        :return: None
        """
        pass

    @staticmethod
    def DecreaseBaubleDurability(playerId, slotName, num=1):
        """
        减少饰品耐久度
        :param playerId: 玩家ID
        :param num: 减少的耐久度
        :param slotName: 饰品槽位
        :return: None
        """
        pass

    @staticmethod
    def AddTargetBaubleSlot(playerId, slotId, slotType, slotName=None, slotPlaceHolderPath=None):
        """
        添加目标饰品槽位
        :param playerId: 玩家ID
        :param slotId: 槽位标识符
        :param slotType: 槽位类型
        :param slotName: 槽位名称
        :param slotPlaceHolderPath: 槽位占位符图片路径
        :return: None
        """
        pass

    @staticmethod
    def AddGlobalBaubleSlot(slotId, slotType, slotName=None, slotPlaceHolderPath=None, isDefault=False):
        """
        添加全局饰品槽位
        :param slotId: 槽位标识符
        :param slotType: 槽位类型
        :param slotName: 槽位名称
        :param slotPlaceHolderPath: 槽位占位符图片路径
        :param isDefault: 是否为默认槽位
        :return: None
        """
        pass

    @staticmethod
    def DeleteTargetBaubleSlot(playerId, slotId):
        """
        删除目标饰品槽位
        :param playerId: 玩家ID
        :param slotId: 槽位标识符
        :return: None
        """
        pass

    @staticmethod
    def DeleteGlobalBaubleSlot(slotId):
        """
        删除全局饰品槽位
        :param slotId: 槽位标识符
        :return: None
        """
        pass
