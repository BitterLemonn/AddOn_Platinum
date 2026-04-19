# coding=utf-8
from mod.server import extraServerApi as serverApi
from Script_Platinum import commonConfig
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
        from Script_Platinum.utils.oldVersionFixer import oldSlotTypeToNew

        # 兼容旧版本直接传入字符串的槽位类型, 将其转换为列表并进行旧槽位类型到新槽位类型的转换
        slotType = oldSlotTypeToNew(data["baubleSlot"])
        baubleData = BaubleInfoData(data["baubleName"], slotType, data.get("customTips", None))
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
        from Script_Platinum.utils.oldVersionFixer import oldSlotTypeListToNew

        slotType = oldSlotTypeListToNew(slotType)
        baubleSlotData = BaubleSlotData(slotName, slotPlaceHolderPath, slotId, slotType, isDefault)
        self.slotRegistry.registerSlot(baubleSlotData)

    def SetPlayerBaubleInfo(self, playerId, baubleDict):
        """
        设置玩家饰品信息
        :param playerId: 玩家ID
        :param baubleDict: 饰品字典
        :type baubleDict: dict
        :type playerId: str
        :return:
        """
        from Script_Platinum.server.player.playerBaubleInfo import getPlayerBaubleInfo, PlayerBaubleInfo

        playerBaubleInfo = getPlayerBaubleInfo(playerId)  # type: PlayerBaubleInfo
        playerBaubleInfo.setBaubleDict(baubleDict)

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
        from Script_Platinum.server.player.playerBaubleInfo import getPlayerBaubleInfo, PlayerBaubleInfo
        from Script_Platinum.utils.oldVersionFixer import oldSlotIdFixer
        from Script_Platinum.data.itemStack import ItemStack

        if not baubleInfo:
            logging.error("铂: SetPlayerBaubleInfoWithSlot方法的必要参数baubleInfo为None, 请检查是否正确传入")
            return

        slotId = oldSlotIdFixer(slotName)
        playerBaubleInfo = getPlayerBaubleInfo(playerId)  # type: PlayerBaubleInfo
        playerBaubleInfo.changeBaubleInfoBySlotId(slotId, ItemStack.fromDict(baubleInfo))

    def DecreaseBaubleDurability(self, playerId, slotName, num=1):
        """
        减少饰品耐久度
        :param playerId: 玩家ID
        :param num: 减少的耐久度
        :param slotName: 饰品槽位
        :return:
        """
        from Script_Platinum.server.player.playerBaubleInfo import getPlayerBaubleInfo, PlayerBaubleInfo
        from Script_Platinum.utils.oldVersionFixer import oldSlotIdFixer

        slotId = oldSlotIdFixer(slotName)
        playerBaubleInfo = getPlayerBaubleInfo(playerId)  # type: PlayerBaubleInfo
        playerBaubleInfo.decreaseBaubleDurabilityBySlotId(slotId, num)

    def AddTargetBaubleSlot(self, playerId, slotId, slotType, slotName=None, slotPlaceHolderPath=None):
        """
        添加目标饰品槽位
        :param playerId: 玩家ID
        :param slotId: 槽位标识符
        :param slotType: 槽位类型
        :param slotName: 槽位名称
        :param slotPlaceHolderPath: 槽位占位符图片路径
        :return:
        """
        from Script_Platinum.server.player.playerBaubleSlot import addPlayerSlot
        from Script_Platinum.utils.oldVersionFixer import oldSlotTypeToNew

        # 推荐用法
        if slotType is None and self.slotRegistry.isSlotIdExist(slotId):
            # 将已注册槽位添加到特定玩家
            slotData = self.slotRegistry.getSlotDataById(slotId)
            addPlayerSlot(playerId, slotData)
        else:
            # 兼容旧方法直接添加槽位
            slotType = oldSlotTypeToNew(slotType)
            slotData = BaubleSlotData(slotName, slotPlaceHolderPath, slotId, slotType, False)
            if self.slotRegistry.isSlotIdExist(slotId) or self.slotRegistry.registerSlot(slotData):
                registeredSlotData = self.slotRegistry.getSlotDataById(slotId)
                addPlayerSlot(playerId, registeredSlotData)

    def AddGlobalBaubleSlot(self, slotId, slotType, slotName=None, slotPlaceHolderPath=None, isDefault=False):
        """
        添加全局饰品槽位
        :param slotId: 槽位标识符
        :param slotType: 槽位类型
        :param slotName: 槽位名称
        :param slotPlaceHolderPath: 槽位占位符图片路径
        :param isDefault: 是否为默认槽位(旧参数已废弃)
        :return:
        """
        from Script_Platinum.utils.oldVersionFixer import oldSlotTypeToNew

        if self.slotRegistry.isSlotIdExist(slotId):
            logging.error("铂: 尝试添加全局槽位{}, 但该槽位ID已存在, 请检查是否重复添加".format(slotId))
            return

        slotType = oldSlotTypeToNew(slotType)
        slotData = BaubleSlotData(slotName, slotPlaceHolderPath, slotId, slotType, True)
        self.slotRegistry.registerSlot(slotData)

    def DeleteTargetBaubleSlot(self, playerId, slotId):
        """
        删除目标饰品槽位
        :param playerId: 玩家ID
        :param slotId: 槽位标识符
        :return:
        """
        from Script_Platinum.server.player.playerBaubleSlot import deletePlayerSlotById

        slotData = self.slotRegistry.getSlotDataById(slotId)
        if slotData is None:
            logging.error("铂: 尝试删除玩家{}的槽位{}, 但该槽位不存在".format(playerId, slotId))
            return
        if slotData.isDefault:
            logging.error("铂: 尝试删除玩家{}的槽位{}, 但该槽位为默认槽位, 无法删除".format(playerId, slotId))
            return
        deletePlayerSlotById(playerId, slotId)

    def DeleteGlobalBaubleSlot(self, slotId):
        """
        删除全局饰品槽位
        :param slotId: 槽位标识符
        :return:
        """
        # 不支持删除全局槽位, 仅支持删除特定玩家槽位
        logging.error("铂: 尝试删除全局槽位{}, 但不支持删除全局槽位, 仅支持删除特定玩家槽位".format(slotId))
        pass

    def GetPlayerBaubleInfo(self, playerId):
        """
        获取玩家饰品信息
        :param playerId: 玩家ID
        :return:
        """
        from Script_Platinum.server.player.playerBaubleInfo import getPlayerBaubleInfo, PlayerBaubleInfo

        playerBaubleInfo = getPlayerBaubleInfo(playerId)  # type: PlayerBaubleInfo
        # 兼容旧方法发送事件
        self.BroadcastEvent(commonConfig.BAUBLE_GET_INFO_EVENT, playerBaubleInfo.baubleInfo)
        return playerBaubleInfo.baubleInfo

    def GetGlobalBaubleSlotInfo(self):
        """
        获取全局饰品槽位信息
        :return:
        """
        slotList = self.slotRegistry.getBaubleSlotList()
        slotInfoList = [slot.__dict__ for slot in slotList]
        # 兼容旧方法发送事件
        self.BroadcastEvent(commonConfig.BAUBLE_GET_GLOBAL_INFO_EVENT, slotInfoList)
        return slotInfoList

    def GetTagetBaubleSlotInfo(self, playerId):
        """
        获取玩家饰品槽位信息
        :param playerId: 玩家ID
        :return:
        """
        from Script_Platinum.server.player.playerBaubleSlot import getPlayerSlotList

        playerSlotList = getPlayerSlotList(playerId)
        slotInfoList = [slot.__dict__ for slot in playerSlotList]
        # 兼容旧方法发送事件
        self.BroadcastEvent(commonConfig.BAUBLE_GET_TARGET_INFO_EVENT, slotInfoList)
        return slotInfoList
