# coding=utf-8
from Script_Platinum.QuModLibs.Server import *
from Script_Platinum.QuModLibs.Modules.Services.Server import BaseService
from Script_Platinum.data.itemStack import ItemStack
from Script_Platinum.server.player.playerBaubleInfo import getPlayerBaubleInfo
from Script_Platinum.server.entity.entityBaubleInfo import getEntityBaubleInfo
from Script_Platinum.server.player.playerBaubleSlot import getPlayerSlotList
from Script_Platinum.server.registry.baubleRegistry import BaubleRegistry
from Script_Platinum.server.registry.slotRegistry import SlotRegistry
from Script_Platinum.utils.serverUtils import compFactory, givePlayerItem
from Script_Platinum.utils import developLogging as logging

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
    return first.count == second.count and first.getDurability() == second.getDurability() and first.isSameItem(second)


def _getContainerIndex(slotIndex):
    return slotIndex + (1 if slotIndex >= RESERVED_UI_SLOT_INDEX else 0)


def _getSlotIndex(slotList, containerIndex):
    if not isinstance(containerIndex, (int, long)) or containerIndex < 0 or containerIndex == RESERVED_UI_SLOT_INDEX:
        return None
    slotIndex = containerIndex - (1 if containerIndex > RESERVED_UI_SLOT_INDEX else 0)
    return slotIndex if slotIndex < min(len(slotList), BAUBLE_CONTAINER_SLOT_LIMIT) else None


def _getEntitySlotList(entityId):
    """获取实体的槽位列表；非玩家实体使用全局默认槽位。"""
    if entityId and Entity(entityId).IsPlayer:
        return getPlayerSlotList(entityId)
    return SlotRegistry().getBaubleSlotList(defaultFilter=True)


def _getEntityBaubleInfo(entityId):
    if entityId and Entity(entityId).IsPlayer:
        return getPlayerBaubleInfo(entityId)
    return getEntityBaubleInfo(entityId)


@BaseService.Init
class BaubleContainerServerService(BaseService):

    def __init__(self):
        BaseService.__init__(self)
        self.pendingSlotItems = {}
        # 查看者玩家ID -> 被查看实体ID (查看他人饰品栏); 仅在界面打开期间保留
        self.viewerTargets = {}
        self.viewerSlotCounts = {}
        self.viewerSessions = {}
        self.nextSessionId = 0
        # 脚本写入容器时屏蔽物品变化事件。
        self.updatingPlayers = set()

    @staticmethod
    def _isBaubleContainer(data):
        return (
            data.get("collectionType") == "netease_ui_container" and data.get("collectionName") == BAUBLE_CONTAINER_NAME
        )

    def _getTargetId(self, playerId):
        return self.viewerTargets.get(playerId, playerId)

    def _getSlotData(self, playerId, index):
        slotList = _getEntitySlotList(self._getTargetId(playerId))
        slotIndex = _getSlotIndex(slotList, index)
        return slotList[slotIndex] if slotIndex is not None else None

    @staticmethod
    def _isValidBauble(itemStack, slotData):
        return (
            itemStack is not None
            and itemStack.count == 1
            and BaubleRegistry().isValidBauble(itemStack.name, slotData.slotType)
        )

    def _fillContainerItems(self, playerId, entityId):
        slotList = _getEntitySlotList(entityId)[:BAUBLE_CONTAINER_SLOT_LIMIT]
        baubleInfo = _getEntityBaubleInfo(entityId)
        itemComp = compFactory.CreateItem(playerId)
        slotCount = max(len(slotList), self.viewerSlotCounts.get(playerId, 0))
        self.viewerSlotCounts[playerId] = slotCount
        self.updatingPlayers.add(playerId)
        try:
            for slotIndex in range(slotCount):
                itemDict = None
                if slotIndex < len(slotList):
                    itemStack = baubleInfo.getBaubleInfoBySlotId(slotList[slotIndex].identifier)
                    if itemStack is not None and not itemStack.isEmpty():
                        itemDict = itemStack.toDict()
                itemComp.SetPlayerUIItem(playerId, _getContainerIndex(slotIndex), itemDict, False, True)
        finally:
            self.updatingPlayers.discard(playerId)

    def _clearContainerItems(self, playerId, slotCount):
        """清空界面容器槽位, 避免关闭界面后残留物品被引擎结算回背包。"""
        itemComp = compFactory.CreateItem(playerId)
        if not itemComp:
            return
        self.updatingPlayers.add(playerId)
        try:
            for slotIndex in range(min(slotCount, BAUBLE_CONTAINER_SLOT_LIMIT)):
                itemComp.SetPlayerUIItem(playerId, _getContainerIndex(slotIndex), None, False, True)
        finally:
            self.updatingPlayers.discard(playerId)

    def refreshTargetContainers(self, targetId):
        """目标饰品数据变化时, 刷新正查看该目标的容器界面物品(含API移除饰品后同步清除容器内物品)。"""
        for viewerId, viewTargetId in self.viewerTargets.items():
            if viewTargetId == targetId and viewerId not in self.pendingSlotItems:
                self._fillContainerItems(viewerId, targetId)

    @BaseService.REG_API("server/player/closeBaubleContainer")
    def closeBaubleContainer(self, sessionId=None):
        """界面关闭时清空容器槽位并注销 viewer, 防止残留物品被引擎结算回背包。"""
        playerId = getLoaderSystem().rpcPlayerId
        if sessionId is None or sessionId == self.viewerSessions.get(playerId):
            self._closeContainer(playerId)

    def _closeContainer(self, playerId, commit=True):
        targetId = self.viewerTargets.pop(playerId, None)
        if targetId is None:
            return
        self.viewerSessions.pop(playerId, None)
        slotCount = self.viewerSlotCounts.pop(playerId, 0)
        pendingItems = self.pendingSlotItems.pop(playerId, {})
        try:
            # 关闭后引擎可能已清空容器，使用已完成的增删事件记录提交。
            if commit and pendingItems:
                self._applySlotChanges(targetId, pendingItems)
        finally:
            self._clearContainerItems(playerId, slotCount)

    def _openContainer(self, playerId, entityId=None):
        if entityId is None or entityId == playerId:
            entityId = playerId
        if playerId in self.pendingSlotItems:
            self._syncPlayerSlots(playerId)
        self.nextSessionId += 1
        sessionId = self.nextSessionId
        Call(playerId, "SetBaubleContainerSession", sessionId, entityId == playerId)
        # 先同步外部数据快照再打开界面, 避免客户端代理创建时读到旧数据
        if entityId != playerId:
            Call(playerId, "SyncEntityContainerData", self._getTargetSnapshot(entityId), sessionId)
        playerComp = compFactory.CreatePlayer(playerId)
        isOpen = playerComp.OpenNeteaseContainer(BAUBLE_CONTAINER_SCREEN, BAUBLE_CONTAINER_NAME, False)
        if isOpen:
            self.viewerTargets[playerId] = entityId
            self.viewerSessions[playerId] = sessionId
            self._fillContainerItems(playerId, entityId)
        else:
            previousTarget = self.viewerTargets.get(playerId, playerId)
            previousSession = self.viewerSessions.get(playerId)
            Call(playerId, "SetBaubleContainerSession", previousSession, previousTarget == playerId)
            if previousTarget != playerId:
                Call(playerId, "SyncEntityContainerData", self._getTargetSnapshot(previousTarget), previousSession)
        # ponytail: 客户端规则按打开界面时快照同步；运行时新增饰品后重新打开界面刷新。
        return {
            "opened": isOpen,
            "entityId": entityId,
            "slotList": [slot.__dict__ for slot in _getEntitySlotList(entityId)[:BAUBLE_CONTAINER_SLOT_LIMIT]],
            "baubleDict": {
                slotId: itemStack.toDict()
                for slotId, itemStack in _getEntityBaubleInfo(entityId).baubleInfo.items()
                if itemStack is not None and not itemStack.isEmpty()
            },
            "rules": {baubleId: list(info["slot"]) for baubleId, info in BaubleRegistry().baubles.iteritems()},
        }

    @BaseService.REG_API("server/player/openBaubleContainer")
    def openBaubleContainer(self, _=None):
        return self._openContainer(getLoaderSystem().rpcPlayerId)

    @BaseService.Listen("PlayerTryPutCustomContainerItemServerEvent")
    def onTryPutItem(self, data):
        playerId = data.get("playerId")
        if not self._isBaubleContainer(data) or playerId in self.updatingPlayers:
            return
        if playerId not in self.viewerTargets:
            data["cancel"] = True
            return
        slotData = self._getSlotData(playerId, data.get("collectionIndex"))
        itemStack = _toItemStack(data.get("itemDict"))
        if slotData is None or not self._isValidBauble(itemStack, slotData):
            data["cancel"] = True

    @BaseService.Listen("PlayerTryAddCustomContainerItemServerEvent")
    def onTryAddItem(self, data):
        self.onTryPutItem(data)

    @BaseService.Listen("PlayerAddCustomContainerItemServerEvent")
    def onAddItem(self, data):
        playerId = data.get("playerId")
        if not self._isBaubleContainer(data) or playerId in self.updatingPlayers or playerId not in self.viewerTargets:
            return
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
        self._queuePlayerSync(playerId, slotData.identifier, itemStack)

    @BaseService.Listen("PlayerRemoveCustomContainerItemServerEvent")
    def onRemoveItem(self, data):
        playerId = data.get("playerId")
        if not self._isBaubleContainer(data) or playerId in self.updatingPlayers or playerId not in self.viewerTargets:
            return
        index = data.get("collectionIndex")
        slotData = self._getSlotData(playerId, index)
        if slotData is not None:
            self._queuePlayerSync(playerId, slotData.identifier, _toItemStack(data.get("afterItemDict")))

    def _queuePlayerSync(self, playerId, slotId, itemStack):
        isPending = playerId in self.pendingSlotItems
        pendingItems = self.pendingSlotItems.setdefault(playerId, {})
        pendingItems[slotId] = itemStack
        if isPending:
            return
        self.addTimer(self.Timer(self._syncPlayerSlots, (playerId, pendingItems)))

    def _syncPlayerSlots(self, playerId, expectedItems=None):
        pendingItems = self.pendingSlotItems.get(playerId)
        if not pendingItems or (expectedItems is not None and pendingItems is not expectedItems):
            return
        self.pendingSlotItems.pop(playerId)
        targetId = self.viewerTargets.get(playerId)
        if targetId is None:
            return
        if not self._applySlotChanges(targetId, pendingItems):
            self._fillContainerItems(playerId, targetId)
        if targetId != playerId:
            Call(playerId, "SyncEntityContainerData", self._getTargetSnapshot(targetId), self.viewerSessions.get(playerId))

    def _applySlotChanges(self, targetId, pendingItems):
        slotList = _getEntitySlotList(targetId)[:BAUBLE_CONTAINER_SLOT_LIMIT]
        baubleInfo = _getEntityBaubleInfo(targetId)
        changedSlots = []
        for slotData in slotList:
            slotId = slotData.identifier
            if slotId not in pendingItems:
                continue
            itemStack = pendingItems[slotId]
            if itemStack is not None and not self._isValidBauble(itemStack, slotData):
                continue
            oldItemStack = baubleInfo.getBaubleInfoBySlotId(slotId)
            if not _isSameItem(oldItemStack, itemStack):
                changedSlots.append((slotId, oldItemStack, itemStack))

        # 先全部卸下再穿上，避免容器移动事件乱序导致同一饰品短暂重复生效。
        for slotId, oldItemStack, _ in changedSlots:
            if oldItemStack is not None and not oldItemStack.isEmpty():
                baubleInfo.changeBaubleInfoBySlotId(slotId, None, -1, False)
        for slotId, _, itemStack in changedSlots:
            if itemStack is not None:
                baubleInfo.changeBaubleInfoBySlotId(slotId, itemStack, -1, False)
        return bool(changedSlots)

    def _getTargetSnapshot(self, entityId):
        return {
            "entityId": entityId,
            "slotList": [slot.__dict__ for slot in _getEntitySlotList(entityId)[:BAUBLE_CONTAINER_SLOT_LIMIT]],
            "baubleDict": {
                slotId: itemStack.toDict()
                for slotId, itemStack in _getEntityBaubleInfo(entityId).baubleInfo.items()
                if itemStack is not None and not itemStack.isEmpty()
            },
            "rules": {baubleId: list(info["slot"]) for baubleId, info in BaubleRegistry().baubles.iteritems()},
        }

    def _restoreSlot(self, playerId, index, slotId, returnItemDict=None):
        itemStack = (
            _getEntityBaubleInfo(self._getTargetId(playerId)).getBaubleInfoBySlotId(slotId)
            if slotId is not None
            else None
        )
        itemDict = itemStack.toDict() if itemStack is not None and not itemStack.isEmpty() else None
        self.updatingPlayers.add(playerId)
        try:
            restored = compFactory.CreateItem(playerId).SetPlayerUIItem(playerId, index, itemDict, False, True)
        finally:
            self.updatingPlayers.discard(playerId)
        if restored and _toItemStack(returnItemDict) is not None:
            givePlayerItem(returnItemDict, playerId)

    def openEntityBaubleContainer(self, playerId, entityId):
        """对外API: 为玩家打开指定实体的饰品栏容器。"""
        if not playerId or not Entity(playerId).IsPlayer:
            logging.error("铂: 打开实体饰品栏失败, 无效的查看者playerId: {}".format(playerId))
            return False
        if not entityId or not Entity(entityId).isEntityValid():
            logging.error("铂: 打开实体饰品栏失败, 无效的entityId: {}".format(entityId))
            return False
        result = self._openContainer(playerId, entityId)
        isOpen = result.pop("opened")
        return isOpen

    @BaseService.Listen("DelServerPlayerEvent")
    def onDelServerPlayer(self, data):
        playerId = data.get("id")
        self.viewerTargets.pop(playerId, None)
        self.viewerSlotCounts.pop(playerId, None)
        self.viewerSessions.pop(playerId, None)
        self.pendingSlotItems.pop(playerId, None)
        self.updatingPlayers.discard(playerId)

    @BaseService.Listen("PlayerIntendLeaveServerEvent")
    def onPlayerIntendLeave(self, data):
        self._closeContainer(data.get("playerId"))

    @BaseService.Listen("EntityRemoveEvent")
    def onEntityRemoveEvent(self, data):
        """被查看实体移除时通知查看者客户端关闭饰品栏界面。"""
        entityId = data.get("id")
        for viewerId, targetId in self.viewerTargets.items():
            if targetId == entityId:
                sessionId = self.viewerSessions.get(viewerId)
                self._closeContainer(viewerId, commit=False)
                Call(viewerId, "SyncEntityContainerData", None, sessionId)
