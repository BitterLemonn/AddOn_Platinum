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
    return first.count == second.count and first.isSameItem(second)


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
        self.pendingSlotIndices = {}
        # 查看者玩家ID -> 被查看实体ID (查看他人饰品栏)
        self.viewerTargets = {}

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
        slotList = _getEntitySlotList(entityId)
        baubleInfo = _getEntityBaubleInfo(entityId)
        itemComp = compFactory.CreateItem(playerId)

        for slotIndex, slotData in enumerate(slotList[:BAUBLE_CONTAINER_SLOT_LIMIT]):
            itemStack = baubleInfo.getBaubleInfoBySlotId(slotData.identifier)
            itemDict = itemStack.toDict() if itemStack is not None and not itemStack.isEmpty() else None
            itemComp.SetPlayerUIItem(playerId, _getContainerIndex(slotIndex), itemDict, False, True)

    def refreshTargetContainers(self, targetId):
        """目标饰品数据变化时, 刷新正查看该目标的容器界面物品(含API移除饰品后同步清除容器内物品)。"""
        # ponytail: 界面关闭后 viewerTargets 记录保留, 刷新只是对已关闭界面的UI容器槽做无害写入,
        # 下次打开时 _fillContainerItems 会全量覆盖; 需要精确开关追踪时改挂容器关闭事件。
        for viewerId, viewTargetId in self.viewerTargets.items():
            if viewTargetId == targetId:
                self._fillContainerItems(viewerId, targetId)

    def _openContainer(self, playerId, entityId=None):
        if entityId is None or entityId == playerId:
            entityId = playerId
        # 登记 viewer(含查看自己), 供饰品数据变化时刷新打开中的容器界面
        self.viewerTargets[playerId] = entityId
        if playerId in self.pendingSlotIndices:
            self._syncPlayerSlots(playerId)
        self._fillContainerItems(playerId, entityId)
        # 先同步外部数据快照再打开界面, 避免客户端代理创建时读到旧数据
        if entityId != playerId:
            Call(playerId, "SyncEntityContainerData", self._getTargetSnapshot(entityId))
        playerComp = compFactory.CreatePlayer(playerId)
        isOpen = playerComp.OpenNeteaseContainer(BAUBLE_CONTAINER_SCREEN, BAUBLE_CONTAINER_NAME, False)
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
        if not playerId:
            return
        targetId = self._getTargetId(playerId)
        if _getSlotIndex(_getEntitySlotList(targetId), index) is None:
            return
        isPending = playerId in self.pendingSlotIndices
        self.pendingSlotIndices.setdefault(playerId, set()).add(index)
        if isPending:
            return
        # ponytail: 当前按下一服务 tick 合并同次移动事件；跨 tick 事件批次出现时改为带版本的事务队列。
        self.addTimer(self.Timer(self._syncPlayerSlots, (playerId,)))

    def _syncPlayerSlots(self, playerId):
        changedIndices = self.pendingSlotIndices.pop(playerId, set())
        targetId = self._getTargetId(playerId)
        slotList = _getEntitySlotList(targetId)
        baubleInfo = _getEntityBaubleInfo(targetId)
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
        # 查看他人饰品栏时同步最新数据到查看者客户端
        if targetId != playerId:
            Call(playerId, "SyncEntityContainerData", self._getTargetSnapshot(targetId))

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

    @staticmethod
    def _restoreSlot(playerId, index, slotId, returnItemDict=None):
        itemStack = (
            _getEntityBaubleInfo(BaubleContainerServerService.access()._getTargetId(playerId)).getBaubleInfoBySlotId(
                slotId
            )
            if slotId is not None
            else None
        )
        itemDict = itemStack.toDict() if itemStack is not None and not itemStack.isEmpty() else None
        compFactory.CreateItem(playerId).SetPlayerUIItem(playerId, index, itemDict, False, True)
        if _toItemStack(returnItemDict) is not None:
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
        self.viewerTargets.pop(data.get("id"), None)

    @BaseService.Listen("EntityRemoveEvent")
    def onEntityRemoveEvent(self, data):
        """被查看实体移除时通知查看者客户端关闭饰品栏界面。"""
        entityId = data.get("id")
        for viewerId, targetId in self.viewerTargets.items():
            if targetId == entityId:
                self.viewerTargets.pop(viewerId, None)
                Call(viewerId, "SyncEntityContainerData", None)
