# coding=utf-8
from mod.server import extraServerApi as serverApi
from Script_Platinum import commonConfig
from Script_Platinum.data.eventData import BaubleInfoData
from Script_Platinum.data.slotData import BaubleSlotData
from Script_Platinum.server.attribute.attributeModifier import (
    PlatinumAttributeModifierService,
    PlatinumAttributeType,
)
from Script_Platinum.server.registry.baubleRegistry import BaubleRegistry
from Script_Platinum.server.registry.slotRegistry import SlotRegistry
from Script_Platinum.utils import developLogging as logging


class BroadcasterServer(serverApi.GetServerSystemCls()):
    AttrType = PlatinumAttributeType
    AttributeModifierOperation = serverApi.GetMinecraftEnum().AttributeModifierOperation
    AttributeOperands = serverApi.GetMinecraftEnum().AttributeOperands

    def __init__(self, namespace, name):
        super(BroadcasterServer, self).__init__(namespace, name)
        self.baubleRegistry = BaubleRegistry()
        self.slotRegistry = SlotRegistry()

    def AddModifier(self, entityId, attributeType, modifierId, amount, operation, operand):
        """添加实体属性修饰符；modifierId 已存在时返回 False。"""
        return PlatinumAttributeModifierService.access().addModifier(
            entityId, attributeType, modifierId, amount, operation, operand
        )

    def UpdateModifier(self, entityId, attributeType, modifierId, amount, operation, operand):
        """更新实体属性修饰符；modifierId 不存在时返回 False。"""
        return PlatinumAttributeModifierService.access().updateModifier(
            entityId, attributeType, modifierId, amount, operation, operand
        )

    def RemoveModifier(self, entityId, attributeType, modifierId):
        """移除实体属性修饰符，并返回操作结果。"""
        return PlatinumAttributeModifierService.access().removeModifier(entityId, attributeType, modifierId)

    def HasModifier(self, entityId, attributeType, modifierId):
        """返回实体属性是否存在指定修饰符。"""
        return PlatinumAttributeModifierService.access().hasModifier(entityId, attributeType, modifierId)

    def GetAllModifiers(self, entityId, attributeType):
        """返回实体属性全部修饰符的副本列表。"""
        return PlatinumAttributeModifierService.access().getAllModifiers(entityId, attributeType)

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
        from Script_Platinum.utils.oldVersionFixer import oldSlotTypeToNew

        slotType = oldSlotTypeToNew(slotType)
        baubleSlotData = BaubleSlotData(slotName, slotPlaceHolderPath, slotId, slotType, isDefault)
        self.slotRegistry.registerSlot(baubleSlotData)

    def SetPlayerBaubleInfo(self, playerId, baubleDict):
        """
        设置玩家饰品信息
        :param playerId: 玩家ID
        :param baubleDict: 饰品字典(兼容Readme八.4包装结构 {"playerId":..., "baubleDict":{槽位id: itemDict}} 或直接传裸dict)
        :type baubleDict: dict
        :type playerId: str
        :return:
        """
        from Script_Platinum.server.player.playerBaubleInfo import getPlayerBaubleInfo, PlayerBaubleInfo

        if isinstance(baubleDict, dict) and set(baubleDict.keys()) == {"playerId", "baubleDict"}:
            baubleDict = baubleDict["baubleDict"]
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

        slotId = oldSlotIdFixer(slotName)
        playerBaubleInfo = getPlayerBaubleInfo(playerId)  # type: PlayerBaubleInfo
        playerBaubleInfo.changeBaubleInfoBySlotId(
            slotId, ItemStack.fromDict(baubleInfo) if baubleInfo else None, isChanged=False
        )

    def SetEntityBaubleInfo(self, entityId, baubleDict, dropProbability=1.0):
        """设置非玩家实体全部饰品信息及掉落几率；数据只保留到实体移除。"""
        from Script_Platinum.server.player.playerBaubleInfo import getEntityBaubleInfo

        if not isinstance(entityId, str) or not entityId:
            logging.error("铂: 设置实体饰品失败, entityId必须为非空str")
            return False
        if isinstance(baubleDict, dict) and set(baubleDict.keys()) in (
            {"entityId", "baubleDict"},
            {"playerId", "baubleDict"},
        ):
            baubleDict = baubleDict["baubleDict"]
        if not isinstance(baubleDict, dict):
            logging.error("铂: 设置实体{}饰品失败, baubleDict必须为dict".format(entityId))
            return False
        getEntityBaubleInfo(entityId).setBaubleDict(baubleDict, dropProbability=dropProbability)
        return True

    def SetEntityBaubleInfoWithSlot(self, entityId, baubleInfo, slotName, dropProbability=1.0):
        """设置非玩家实体指定槽位饰品及掉落几率。"""
        from Script_Platinum.data.itemStack import ItemStack
        from Script_Platinum.server.player.playerBaubleInfo import getEntityBaubleInfo
        from Script_Platinum.utils.oldVersionFixer import oldSlotIdFixer

        if not isinstance(entityId, str) or not entityId:
            logging.error("铂: 设置实体饰品失败, entityId必须为非空str")
            return False
        if baubleInfo is not None and not isinstance(baubleInfo, dict):
            logging.error("铂: 设置实体{}饰品失败, baubleInfo必须为dict或None".format(entityId))
            return False
        getEntityBaubleInfo(entityId).changeBaubleInfoBySlotId(
            oldSlotIdFixer(slotName),
            ItemStack.fromDict(baubleInfo) if baubleInfo else None,
            isChanged=False,
            dropProbability=dropProbability,
        )
        return True

    def GetEntityBaubleInfo(self, entityId):
        """获取实体饰品信息。"""
        from Script_Platinum.server.player.playerBaubleInfo import getEntityBaubleInfo

        if not isinstance(entityId, str) or not entityId:
            return None
        baubleInfo = getEntityBaubleInfo(entityId)
        return { 
            "entityId": entityId,
            "baubleDict": {
                slotId: itemStack.toDict()
                for slotId, itemStack in baubleInfo.baubleInfo.items()
                if itemStack is not None
            },
        }

    def DecreaseEntityBaubleDurability(self, entityId, slotName, num=1):
        """减少实体指定槽位饰品耐久度。"""
        from Script_Platinum.server.player.playerBaubleInfo import getEntityBaubleInfo
        from Script_Platinum.utils.oldVersionFixer import oldSlotIdFixer

        if not isinstance(entityId, str) or not entityId:
            return False
        getEntityBaubleInfo(entityId).decreaseBaubleDurabilityBySlotId(oldSlotIdFixer(slotName), num)
        return True

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
        baubleInfoDict = {
            slotId: baubleInfo.toDict()
            for slotId, baubleInfo in playerBaubleInfo.baubleInfo.items()
            if baubleInfo is not None
        }
        baubleInfoData = {"playerId": playerId, "baubleDict": baubleInfoDict}
        # 兼容旧方法发送事件
        self.BroadcastEvent(commonConfig.BAUBLE_GET_INFO_EVENT, baubleInfoData)
        return baubleInfoData

    def GetGlobalBaubleSlotInfo(self):
        """
        获取全局饰品槽位信息
        :return:
        """
        slotList = self.slotRegistry.getBaubleSlotList()
        slotInfoList = [{slot.identifier: self._slotToInfoDict(slot)} for slot in slotList]
        slotInfoData = {"baubleSlotList": slotInfoList}
        # 兼容旧方法发送事件
        self.BroadcastEvent(commonConfig.BAUBLE_GET_GLOBAL_INFO_EVENT, slotInfoData)
        return slotInfoData

    def GetTargetBaubleSlotInfo(self, playerId):
        """
        获取玩家饰品槽位信息
        :param playerId: 玩家ID
        :return:
        """
        from Script_Platinum.server.player.playerBaubleSlot import getPlayerSlotList

        playerSlotList = getPlayerSlotList(playerId)
        slotInfoList = [{slot.identifier: self._slotToInfoDict(slot)} for slot in playerSlotList]
        slotInfoData = {"playerId": playerId, "baubleSlotList": slotInfoList}
        # 兼容旧方法发送事件
        self.BroadcastEvent(commonConfig.BAUBLE_GET_TARGET_INFO_EVENT, slotInfoData)
        return slotInfoData

    @staticmethod
    def _slotToInfoDict(slot):
        # type: (BaubleSlotData) -> dict
        """槽位数据转Readme规定的字段结构"""
        return {
            "slotId": slot.identifier,
            "slotType": slot.slotType,
            "slotName": slot.name,
            "isDefault": slot.isDefault,
        }
