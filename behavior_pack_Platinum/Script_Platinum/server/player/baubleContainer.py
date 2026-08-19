# coding=utf-8
from Script_Platinum.QuModLibs.Server import *
from Script_Platinum.QuModLibs.Modules.Services.Server import BaseService
from Script_Platinum.data.itemStack import ItemStack
from Script_Platinum.server.player.playerBaubleInfo import getPlayerBaubleInfo
from Script_Platinum.server.player.playerBaubleSlot import getPlayerSlotList
from Script_Platinum.server.registry.baubleRegistry import BaubleRegistry
from Script_Platinum.utils.serverUtils import compFactory, givePlayerItem

BAUBLE_CONTAINER_SCREEN = "bauble_reborn_screen.screen"
BAUBLE_CONTAINER_NAME = "bauble_reborn.screen.name"
RESERVED_UI_SLOT_INDEX = 50
# ponytail: 网易自定义容器当前验证上限为107个逻辑槽；引擎支持更高数量后同步调整客户端与服务端。
BAUBLE_CONTAINER_SLOT_LIMIT = 107


def _toItemStack(itemDict):
    itemStack = ItemStack.fromDict(itemDict)
    return None if itemStack.isEmpty() else itemStack


def _isSameItem(first, second):
    if first is None or second is None:
        return first is second
    return first.count == second.count and first.isSameItem(second)


def _getContainerIndex(slotIndex):
    return slotIndex + (1 if slotIndex >= RESERVED_UI_SLOT_INDEX else 0)


def _getSlotIndex(slotList, containerIndex):
    if not isinstance(containerIndex, (int, long)) or containerIndex < 0 or containerIndex == RESERVED_UI_SLOT_INDEX:
        return None
    slotIndex = containerIndex - (1 if containerIndex > RESERVED_UI_SLOT_INDEX else 0)
    return slotIndex if slotIndex < min(len(slotList), BAUBLE_CONTAINER_SLOT_LIMIT) else None


@BaseService.Init
class BaubleContainerServerService(BaseService):

    def __init__(self):
        BaseService.__init__(self)
        self.pendingSlotIndices = {}

    @staticmethod
    def _isBaubleContainer(data):
        return (
            data.get("collectionType") == "netease_ui_container" and data.get("collectionName") == BAUBLE_CONTAINER_NAME
        )

    @staticmethod
    def _getSlotData(playerId, index):
        slotList = getPlayerSlotList(playerId)
        slotIndex = _getSlotIndex(slotList, index)
        return slotList[slotIndex] if slotIndex is not None else None

    @staticmethod
    def _isValidBauble(itemStack, slotData):
        return (
            itemStack is not None
            and itemStack.count == 1
            and BaubleRegistry().isValidBauble(itemStack.name, slotData.slotType)
        )

    @BaseService.REG_API("server/player/openBaubleContainer")
    def openBaubleContainer(self, _=None):
        playerId = getLoaderSystem().rpcPlayerId
        if playerId in self.pendingSlotIndices:
            self._syncPlayerSlots(playerId)
        slotList = getPlayerSlotList(playerId)
        baubleInfo = getPlayerBaubleInfo(playerId)
        itemComp = compFactory.CreateItem(playerId)

        for slotIndex, slotData in enumerate(slotList[:BAUBLE_CONTAINER_SLOT_LIMIT]):
            itemStack = baubleInfo.getBaubleInfoBySlotId(slotData.identifier)
            itemDict = itemStack.toDict() if itemStack is not None and not itemStack.isEmpty() else None
            itemComp.SetPlayerUIItem(playerId, _getContainerIndex(slotIndex), itemDict, False, True)

        playerComp = compFactory.CreatePlayer(playerId)
        isOpen = playerComp.OpenNeteaseContainer(BAUBLE_CONTAINER_SCREEN, BAUBLE_CONTAINER_NAME, False)
        # ponytail: 客户端规则按打开界面时快照同步；运行时新增饰品后重新打开界面刷新。
        return {
            "opened": isOpen,
            "rules": {baubleId: list(info["slot"]) for baubleId, info in BaubleRegistry().baubles.iteritems()},
        }

    @BaseService.Listen("PlayerTryPutCustomContainerItemServerEvent")
    def onTryPutItem(self, data):
        if not self._isBaubleContainer(data):
            return
        slotData = self._getSlotData(data.get("playerId"), data.get("collectionIndex"))
        itemStack = _toItemStack(data.get("itemDict"))
        if slotData is None or not self._isValidBauble(itemStack, slotData):
            data["cancel"] = True

    @BaseService.Listen("PlayerTryAddCustomContainerItemServerEvent")
    def onTryAddItem(self, data):
        self.onTryPutItem(data)

    @BaseService.Listen("PlayerAddCustomContainerItemServerEvent")
    def onAddItem(self, data):
        if not self._isBaubleContainer(data):
            return
        playerId = data.get("playerId")
        index = data.get("collectionIndex")
        slotData = self._getSlotData(playerId, index)
        itemStack = _toItemStack(data.get("afterItemDict"))
        if slotData is None:
            if isinstance(index, (int, long)) and index >= 0 and index != RESERVED_UI_SLOT_INDEX:
                self._restoreSlot(playerId, index, None, data.get("changedItemDict"))
            return
        if itemStack is not None and not self._isValidBauble(itemStack, slotData):
            self._restoreSlot(playerId, index, slotData.identifier, data.get("changedItemDict"))
            return
        self._queuePlayerSync(playerId, index)

    @BaseService.Listen("PlayerRemoveCustomContainerItemServerEvent")
    def onRemoveItem(self, data):
        if self._isBaubleContainer(data):
            self._queuePlayerSync(data.get("playerId"), data.get("collectionIndex"))

    def _queuePlayerSync(self, playerId, index):
        if not playerId or _getSlotIndex(getPlayerSlotList(playerId), index) is None:
            return
        isPending = playerId in self.pendingSlotIndices
        self.pendingSlotIndices.setdefault(playerId, set()).add(index)
        if isPending:
            return
        # ponytail: 当前按下一服务 tick 合并同次移动事件；跨 tick 事件批次出现时改为带版本的事务队列。
        self.addTimer(self.Timer(self._syncPlayerSlots, (playerId,)))

    def _syncPlayerSlots(self, playerId):
        changedIndices = self.pendingSlotIndices.pop(playerId, set())
        slotList = getPlayerSlotList(playerId)
        baubleInfo = getPlayerBaubleInfo(playerId)
        itemComp = compFactory.CreateItem(playerId)
        changedSlots = []
        for containerIndex in sorted(changedIndices):
            slotIndex = _getSlotIndex(slotList, containerIndex)
            if slotIndex is None:
                continue
            slotData = slotList[slotIndex]
            itemStack = _toItemStack(itemComp.GetPlayerUIItem(playerId, containerIndex, True, True))
            if itemStack is not None and not self._isValidBauble(itemStack, slotData):
                self._restoreSlot(playerId, containerIndex, slotData.identifier)
                continue
            oldItemStack = baubleInfo.getBaubleInfoBySlotId(slotData.identifier)
            if not _isSameItem(oldItemStack, itemStack):
                changedSlots.append((slotData.identifier, oldItemStack, itemStack))

        # 先全部卸下再穿上，避免容器移动事件乱序导致同一饰品短暂重复生效。
        for slotId, oldItemStack, _ in changedSlots:
            if oldItemStack is not None and not oldItemStack.isEmpty():
                baubleInfo.changeBaubleInfoBySlotId(slotId, None, -1, False)
        for slotId, _, itemStack in changedSlots:
            if itemStack is not None:
                baubleInfo.changeBaubleInfoBySlotId(slotId, itemStack, -1, False)

    @staticmethod
    def _restoreSlot(playerId, index, slotId, returnItemDict=None):
        itemStack = getPlayerBaubleInfo(playerId).getBaubleInfoBySlotId(slotId) if slotId is not None else None
        itemDict = itemStack.toDict() if itemStack is not None and not itemStack.isEmpty() else None
        compFactory.CreateItem(playerId).SetPlayerUIItem(playerId, index, itemDict, False, True)
        if _toItemStack(returnItemDict) is not None:
            givePlayerItem(returnItemDict, playerId)
