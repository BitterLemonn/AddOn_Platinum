# coding=utf-8
from abc import ABCMeta, abstractmethod

from Script_Platinum import commonConfig
from Script_Platinum.QuModLibs.Server import *
from Script_Platinum.server.registry.slotRegistry import checkSlotValid
from Script_Platinum.data.itemStack import ItemStack
from Script_Platinum.utils.ItemFactory import ItemFactory
from Script_Platinum.utils import developLogging as logging


class BaubleInfo(object):
    __metaclass__ = ABCMeta

    def __init__(self, targetId):
        self.targetId = targetId
        self.baubleInfo = {}  # type: dict[str, ItemStack]
        self.dropProbability = {}  # type: dict[str, float]

    def _getTargetId(self):
        return getattr(self, "targetId", getattr(self, "playerId", None))

    def loadFromDataInit(self):
        """从持久化数据加载饰品后恢复穿戴事件。"""
        for slotId, itemStack in self.baubleInfo.items():
            if itemStack is not None and not itemStack.isEmpty():
                self.boardcastPutOnEvent(slotId, itemStack, True)

    def getEmptyOrFirstSlotByList(self, slotTypeList):
        """根据槽位类型列表获取一个空槽位，没有空槽位则返回该类型第一个槽位。"""
        from Script_Platinum.server.registry.slotRegistry import SlotRegistry

        for slotType in slotTypeList:
            slotIds = SlotRegistry().getSlotIdByType(slotType)
            if not slotIds:
                continue
            for slotId in slotIds:
                itemStack = self.baubleInfo.get(slotId)
                if itemStack is None or itemStack.isEmpty():
                    return slotId
            return slotIds[0]
        return None

    def getBaubleInfoBySlotId(self, slotId):  # type: (str) -> ItemStack|None
        """根据槽位ID获取目标佩戴的饰品信息。"""
        return self.baubleInfo.get(slotId, None)

    def changeBaubleInfoBySlotId(
        self, slotId, itemStack, index=-1, isChanged=True, dropProbability=1.0
    ):  # type: (str, int, ItemStack, bool, float) -> None
        """设置目标佩戴的饰品信息。"""
        if not checkSlotValid(slotId):
            logging.w("铂: 尝试设置目标{}槽位{}的饰品信息,但该槽位ID无效".format(self._getTargetId(), slotId))
            return
        oldItemStack = self.baubleInfo.get(slotId, None)
        if oldItemStack is not None and not oldItemStack.isEmpty() and isChanged:
            self._returnReplacedBauble(oldItemStack, index)
        self.baubleInfo[slotId] = itemStack
        self._updateDropProbability(slotId, itemStack, dropProbability)
        self._syncToClient()
        if oldItemStack is not None and not oldItemStack.isEmpty():
            self.boardcastTakeOffEvent(slotId, oldItemStack)
        if itemStack is not None and not itemStack.isEmpty():
            self.boardcastPutOnEvent(slotId, itemStack)
        self._save()

    def setBaubleDict(
        self, baubleDict, isFirstLoad=False, needSave=True, dropProbability=None
    ):  # type: (dict[str, dict], bool, bool, float|dict[str, float]|None) -> None
        """直接设置目标佩戴的饰品信息字典。"""
        if not isinstance(baubleDict, dict):
            return
        for slotId, itemDict in baubleDict.items():
            if itemDict is None:
                continue
            if not isinstance(itemDict, dict):
                logging.warning("铂: 目标{}槽位{}的饰品数据无效".format(self._getTargetId(), slotId))
                continue
            if checkSlotValid(slotId):
                oldItemStack = self.baubleInfo.get(slotId, None)
                self.baubleInfo[slotId] = ItemStack.fromDict(itemDict)
                self._updateLoadedDropProbability(slotId, dropProbability)
                if oldItemStack is not None and not oldItemStack.isEmpty():
                    self.boardcastTakeOffEvent(slotId, oldItemStack)
                self.boardcastPutOnEvent(slotId, self.baubleInfo[slotId], isFirstLoad)
            else:
                logging.warning("铂: 尝试设置目标{}槽位{}的饰品信息,但该槽位ID无效".format(self._getTargetId(), slotId))
        self._syncToClient()
        if needSave:
            self._save()

    def setBaubleDurabilityBySlotId(self, slotId, durability):  # type: (str, int) -> None
        """设置目标佩戴的饰品耐久度。"""
        if not checkSlotValid(slotId):
            logging.warning("铂: 尝试设置目标{}槽位{}的饰品耐久度,但该槽位ID无效".format(self._getTargetId(), slotId))
            return
        if slotId in self.baubleInfo:
            if durability <= 0:
                self._playBreakSound()
                self.boardcastTakeOffEvent(slotId, self.baubleInfo[slotId])
                self.baubleInfo[slotId] = None
                self._syncToClient()
                self._save()
                return
            itemStack = self.baubleInfo[slotId]
            itemStack.setDurability(durability)
            self.baubleInfo[slotId] = itemStack
            self._syncToClient()
        else:
            logging.warning("铂: 尝试设置目标{}槽位{}的饰品耐久度,但该槽位没有饰品".format(self._getTargetId(), slotId))
        self._save()

    def decreaseBaubleDurabilityBySlotId(self, slotId, decreaseAmount):  # type: (str, int) -> None
        """减少目标佩戴的饰品耐久度。"""
        if not checkSlotValid(slotId):
            logging.warning("铂: 尝试减少目标{}槽位{}的饰品耐久度,但该槽位ID无效".format(self._getTargetId(), slotId))
            return
        if slotId in self.baubleInfo:
            itemStack = self.baubleInfo[slotId]
            item = ItemFactory.fromDict(itemStack.toDict())
            itemDict = item.setDurability(item.getDurability() - decreaseAmount).build()
            itemDict = itemDict if item.getDurability() > 0 else None
            self.baubleInfo[slotId] = ItemStack.fromDict(itemDict) if itemDict is not None else None
            if itemDict is None:
                self._playBreakSound()
                self.boardcastTakeOffEvent(slotId, itemStack)
            self._syncToClient()
        else:
            logging.warning("铂: 尝试减少目标{}槽位{}的饰品耐久度,但该槽位没有饰品".format(self._getTargetId(), slotId))
        self._save()

    def boardcastTakeOffEvent(self, slotId, itemStack):
        """广播目标饰品脱落事件。"""
        from Script_Platinum.server.registry.slotRegistry import SlotRegistry
        from Script_Platinum.utils.oldVersionFixer import newSlotTypeToOld

        system = serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER)
        slotType = SlotRegistry().getSlotTypeById(slotId)
        oldSlotType = newSlotTypeToOld(slotType)
        slotIndex = SlotRegistry().getSlotIndexById(slotId)
        baubleData, eventName = self._createTakeOffEventData(slotId, oldSlotType, slotIndex, itemStack)
        eventDict = baubleData.dumpToDict()
        system.BroadcastEvent(eventName, eventDict)
        self._syncBaubleEvent("client/bauble/unequipBaubleBoardcast", eventDict)

    def boardcastPutOnEvent(self, slotId, itemStack, isFirstLoad=False):
        """广播目标饰品佩戴事件。"""
        from Script_Platinum.server.registry.slotRegistry import SlotRegistry
        from Script_Platinum.utils.oldVersionFixer import newSlotTypeToOld

        system = serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER)
        slotType = SlotRegistry().getSlotTypeById(slotId)
        oldSlotType = newSlotTypeToOld(slotType)
        slotIndex = SlotRegistry().getSlotIndexById(slotId)
        baubleData, eventName = self._createPutOnEventData(slotId, oldSlotType, slotIndex, itemStack, isFirstLoad)
        eventDict = baubleData.dumpToDict()
        system.BroadcastEvent(eventName, eventDict)
        self._syncBaubleEvent("client/bauble/equipBaubleBoardcast", eventDict)

    def _returnReplacedBauble(self, itemStack, index):
        pass

    def _updateDropProbability(self, slotId, itemStack, dropProbability):
        pass

    def _updateLoadedDropProbability(self, slotId, dropProbability):
        pass

    def _syncToClient(self):
        self._refreshOpenContainer()

    def _refreshOpenContainer(self):
        """饰品数据变化时, 刷新打开中的饰品栏容器界面物品(如API移除饰品后同步清除容器内物品)。"""
        from Script_Platinum.server.player.baubleContainer import BaubleContainerServerService

        BaubleContainerServerService.access().refreshTargetContainers(self._getTargetId())

    @abstractmethod
    def _save(self):
        raise NotImplementedError

    def _playBreakSound(self):
        return None

    def _syncBaubleEvent(self, requestName, eventDict):
        pass

    @abstractmethod
    def _createTakeOffEventData(self, slotId, slotType, slotIndex, itemStack):
        raise NotImplementedError

    @abstractmethod
    def _createPutOnEventData(self, slotId, slotType, slotIndex, itemStack, isFirstLoad):
        raise NotImplementedError
