# coding=utf-8
import pickle
import traceback
from copy import copy, deepcopy

from Script_Platinum import commonConfig
from Script_Platinum.QuModLibs.Server import *
from Script_Platinum.data.eventData import BaubleEventData
from Script_Platinum.data.requestData import BaubleCheckRequestData, ChangeBaubleRequestData
from Script_Platinum.data.responseData import BaubleCheckResponseData
from Script_Platinum.data.itemStack import ItemStack
from Script_Platinum.server.data.baubleInfo import BaubleInfo
from Script_Platinum.server.player.playerBaubleSlot import getPlayerSlotList
from Script_Platinum.server.registry.baubleRegistry import BaubleRegistry
from Script_Platinum.server.registry.slotRegistry import SlotRegistry, checkSlotValid
from Script_Platinum.utils import developLogging as logging
from Script_Platinum.utils import serverUtils
from Script_Platinum.QuModLibs.Modules.Services.Server import BaseService, QRequests


minecraftEnum = serverApi.GetMinecraftEnum()

isInit = False
playerBaubleInfoDict = {}  # type: dict[str, PlayerBaubleInfo]


def _loadSavedBaubleInfo():
    global isInit
    if isInit:
        return
    isInit = True
    data = compFactory.CreateExtraData(levelId).GetExtraData(commonConfig.PLAYER_BAUBLE_INFO)
    if not data:
        return
    try:
        savedInfo = pickle.loads(data)
    except (pickle.UnpicklingError, EOFError, AttributeError, ImportError, IndexError, TypeError, ValueError):
        logging.error("铂: 玩家饰品信息加载失败\n{}".format(traceback.format_exc()))
        return
    if not isinstance(savedInfo, dict):
        logging.error("铂: 玩家饰品存档格式无效")
        return
    playerBaubleInfoDict.update(savedInfo)


def getPlayerBaubleInfo(playerId):  # type: (str) -> PlayerBaubleInfo
    _loadSavedBaubleInfo()
    if playerId not in playerBaubleInfoDict:
        playerBaubleInfoDict[playerId] = PlayerBaubleInfo(playerId)
    return playerBaubleInfoDict[playerId]


def getEntityBaubleInfo(entityId):
    """兼容旧导入路径，实体饰品数据由实体模块管理。"""
    from Script_Platinum.server.entity.entityBaubleInfo import getEntityBaubleInfo as getInfo

    return getInfo(entityId)


class PlayerBaubleInfo(BaubleInfo):
    def __init__(self, playerId, isPlayer=True):
        BaubleInfo.__init__(self, playerId)
        self.playerId = playerId
        # 保留旧 pickle 字段和构造参数。
        self.isPlayer = isPlayer

    def _getTargetId(self):
        return self.playerId

    def _returnReplacedBauble(self, itemStack, index):
        serverUtils.givePlayerItem(itemStack.toDict(), self.playerId, index)

    def _syncToClient(self):
        baubleDict = {
            slotId: itemStack.toDict() if itemStack is not None else None
            for slotId, itemStack in self.baubleInfo.items()
        }
        BaseService().syncRequest(
            self.playerId,
            "client/bauble/syncFromServer",
            QRequests.Args(baubleDict),
        )
        self._refreshOpenContainer()

    def _save(self):
        PlayerBaubleInfoServerService.access().savePlayerBaubleInfo()

    def _playBreakSound(self):
        Call(self.playerId, "PlaySound", {"soundName": "random.break", "targetId": self.playerId})

    def _syncBaubleEvent(self, requestName, eventDict):
        PlayerBaubleInfoServerService.access().syncRequest(
            self.playerId, requestName, QRequests.Args(eventDict)
        )

    def _createTakeOffEventData(self, slotId, slotType, slotIndex, itemStack):
        return (
            BaubleEventData(self.playerId, slotId, slotType, slotIndex, itemStack, False),
            commonConfig.BAUBLE_UNEQUIPPED_EVENT,
        )

    def _createPutOnEventData(self, slotId, slotType, slotIndex, itemStack, isFirstLoad):
        return (
            BaubleEventData(self.playerId, slotId, slotType, slotIndex, itemStack, isFirstLoad),
            commonConfig.BAUBLE_EQUIPPED_EVENT,
        )


@BaseService.Init
class PlayerBaubleInfoServerService(BaseService):
    """玩家饰品信息服务。"""

    def __init__(self):
        BaseService.__init__(self)
        self.restoredPlayers = set()

    @BaseService.Listen("PlayerDieEvent")
    def onPlayerDieEvent(self, data):
        rule = compFactory.CreateGame(levelId).GetGameRulesInfoServer()
        isKeep = rule.get("cheat_info", {}).get("keep_inventory")
        if not isKeep:
            playerId = data["id"]
            playerBaubleInfo = getPlayerBaubleInfo(playerId)
            for slotId, itemStack in playerBaubleInfo.baubleInfo.items():
                if itemStack is None or itemStack.isEmpty():
                    continue
                playerBaubleInfo.changeBaubleInfoBySlotId(slotId, None, -1, False)
                pos = Entity(playerId).Pos
                dimension = Entity(playerId).Dm
                System.CreateEngineItemEntity(itemStack.toDict(), dimension, pos)

    @BaseService.Listen("ClientLoadAddonsFinishServerEvent")
    def onClientLoadAddonsFinishServerEvent(self, data):
        playerId = data.get("playerId")
        if not playerId or playerId in self.restoredPlayers:
            return
        getPlayerBaubleInfo(playerId).loadFromDataInit()
        self.restoredPlayers.add(playerId)

    @BaseService.Listen("DelServerPlayerEvent")
    def onDelServerPlayer(self, data):
        self.restoredPlayers.discard(data.get("id"))

    @BaseService.REG_API("server/player/requestBaubleInfo")
    def requestBaubleInfo(self, _=None):
        """客户端请求玩家饰品信息。"""
        playerId = getLoaderSystem().rpcPlayerId
        playerBaubleInfo = getPlayerBaubleInfo(playerId)
        return {
            slotId: itemStack.toDict() if itemStack is not None else None
            for slotId, itemStack in playerBaubleInfo.baubleInfo.items()
        }

    @BaseService.REG_API("server/player/baubleCheck")
    def checkBaubleAvailable(self, data):
        """检查饰品是否可以装备。"""
        if not isinstance(data, dict):
            return BaubleCheckResponseData(False, None, None, -1).toDict()
        playerId = getLoaderSystem().rpcPlayerId
        data = BaubleCheckRequestData.fromDict(data)
        slotData = self._getInventorySlotData(playerId, data.slotId, data.index)
        if slotData is None:
            return BaubleCheckResponseData(False, None, data.slotId, data.index).toDict()
        comp = compFactory.CreateItem(playerId)
        if not comp:
            return BaubleCheckResponseData(False, None, data.slotId, data.index).toDict()
        invItem = ItemStack.fromDict(comp.GetPlayerItem(minecraftEnum.ItemPosType.INVENTORY, data.index, True))
        valid = self._matchesBaubleItem(invItem, data.baubleInfo, slotData.slotType)
        return BaubleCheckResponseData(valid, invItem if valid else None, data.slotId, data.index).toDict()

    def _getInventorySlotData(self, playerId, slotId, index):
        if isinstance(index, bool) or not isinstance(index, (int, long)) or not 0 <= index < 36:
            return None
        return self._getPlayerSlotData(playerId, slotId)

    @staticmethod
    def _getPlayerSlotData(playerId, slotId):
        if not playerId or not isinstance(slotId, basestring):
            return None
        if not any(slot.identifier == slotId for slot in getPlayerSlotList(playerId)):
            return None
        return SlotRegistry().getSlotDataById(slotId)

    @staticmethod
    def _matchesBaubleItem(item, expectedItem, slotType, isIgnoreUserData=False):
        return (
            isinstance(expectedItem, ItemStack)
            and expectedItem.count == item.count == 1
            and not item.isEmpty()
            and item.isSameItem(expectedItem, isIgnoreUserData)
            and BaubleRegistry().isValidBauble(item.name, slotType)
        )

    @BaseService.REG_API("server/player/swapCursorBauble")
    def swapCursorBauble(self, slotId, itemName=None, itemAux=0):
        """把原版背包光标上的物品与玩家饰品槽交换。"""
        playerId = getLoaderSystem().rpcPlayerId
        slotData = self._getPlayerSlotData(playerId, slotId)
        if slotData is None or not isinstance(itemAux, (int, long)):
            return False
        comp = compFactory.CreateItem(playerId)
        if not comp:
            return False

        cursorSlot = minecraftEnum.PlayerUISlot.CursorSelected
        cursorItem = ItemStack.fromDict(comp.GetPlayerUIItem(playerId, cursorSlot, True))
        if itemName is None:
            if not cursorItem.isEmpty() and cursorItem.name != "minecraft:air":
                return False
            cursorItem = None
        elif not isinstance(itemName, basestring) or not self._matchesBaubleItem(
            cursorItem, ItemStack(itemName, 1, itemAux), slotData.slotType, isIgnoreUserData=True
        ):
            return False

        baubleInfo = getPlayerBaubleInfo(playerId)
        oldItem = baubleInfo.getBaubleInfoBySlotId(slotId)
        oldItemDict = oldItem.toDict() if oldItem is not None and not oldItem.isEmpty() else None
        if cursorItem is None and oldItemDict is None:
            return False
        # 光标直接换成旧饰品，避免引擎把原光标物品额外返还背包。
        if not comp.SetPlayerUIItem(playerId, cursorSlot, oldItemDict, False):
            return False
        baubleInfo.changeBaubleInfoBySlotId(slotId, cursorItem, isChanged=False)
        return True

    @BaseService.REG_API("server/player/equipCreativeBauble")
    def equipCreativeBauble(self, slotId, itemName, itemAux=0):
        """从创造物品目录直接装备一件饰品。"""
        playerId = getLoaderSystem().rpcPlayerId
        slotData = self._getPlayerSlotData(playerId, slotId)
        if slotData is None or serverUtils.getPlayerMode(playerId) != minecraftEnum.GameType.Creative:
            return False
        if not isinstance(itemName, basestring) or not BaubleRegistry().isValidBauble(itemName, slotData.slotType):
            return False
        if isinstance(itemAux, bool) or not isinstance(itemAux, (int, long)) or not 0 <= itemAux <= 32767:
            return False

        itemAux = 0 if itemAux == 32767 else itemAux
        comp = compFactory.CreateItem(playerId)
        itemInfo = comp.GetItemBasicInfo(itemName, itemAux) if comp else None
        if not itemInfo or itemInfo.get("maxStackSize") != 1:
            return False
        item = ItemStack(itemName, 1, itemAux, durability=itemInfo.get("maxDurability", 0))
        getPlayerBaubleInfo(playerId).changeBaubleInfoBySlotId(slotId, item)
        return item.toDict()

    def _changeBable(self, playerId, slotId, baubleItem, index=-1, playSound=True):
        """从服务端背包格穿脱饰品，成功转移物品后再更新饰品数据。"""
        slotData = self._getInventorySlotData(playerId, slotId, index)
        if slotData is None:
            return False
        comp = compFactory.CreateItem(playerId)
        if not comp:
            return False
        invItemDict = comp.GetPlayerItem(minecraftEnum.ItemPosType.INVENTORY, index, True)
        invItem = ItemStack.fromDict(invItemDict)
        baubleInfo = getPlayerBaubleInfo(playerId)
        oldItem = baubleInfo.getBaubleInfoBySlotId(slotId)
        hasOldItem = oldItem is not None and not oldItem.isEmpty()
        if baubleItem is None:
            if not invItem.isEmpty() or not hasOldItem:
                return False
        elif not self._matchesBaubleItem(invItem, baubleItem, slotData.slotType) or not comp.SetInvItemNum(index, 0):
            return False

        if hasOldItem and not comp.SpawnItemToPlayerInv(oldItem.toDict(), playerId, index):
            if baubleItem is not None and not comp.SpawnItemToPlayerInv(invItemDict, playerId, index):
                serverUtils.givePlayerItem(invItemDict, playerId)
            return False

        baubleInfo.changeBaubleInfoBySlotId(slotId, invItem if baubleItem is not None else None, isChanged=False)
        if playSound:
            Call(playerId, "PlaySound", {"soundName": "armor.equip_iron", "targetId": playerId})
        return True

    @BaseService.REG_API("server/player/changeBauble")
    def changeBauble(self, data):
        """更换饰品。"""
        if not isinstance(data, dict):
            return False
        playerId = getLoaderSystem().rpcPlayerId
        data = ChangeBaubleRequestData.fromDict(data)
        return self._changeBable(playerId, data.slotId, data.baubleInfo, data.index, playSound=False)

    @BaseService.REG_API("server/player/syncOldData")
    def syncOldData(self, data):
        """同步旧版本数据。"""
        if serverApi.IsInServer() or not isinstance(data, dict):
            return False
        playerId = getLoaderSystem().rpcPlayerId
        if not playerId:
            return False
        playerBaubleInfo = getPlayerBaubleInfo(playerId)
        data = {slotId: itemDict for slotId, itemDict in data.items() if itemDict is not None}
        receipt = getattr(playerBaubleInfo, "legacyMigrationReceipt", None)
        if receipt is not None:
            return receipt == data

        ownedSlots = {slot.identifier for slot in getPlayerSlotList(playerId)}
        updates = {}
        for slotId, itemDict in data.items():
            if slotId not in ownedSlots or not checkSlotValid(slotId) or not isinstance(itemDict, dict):
                return False
            item = ItemStack.fromDict(itemDict)
            if not isinstance(item.name, basestring) or not isinstance(item.count, (int, long)) or item.isEmpty():
                return False
            currentItem = playerBaubleInfo.getBaubleInfoBySlotId(slotId)
            if currentItem is None or currentItem.isEmpty():
                updates[slotId] = item
            elif currentItem.toDict() != item.toDict():
                return False
        # 与回执一并存盘，成功后再向游戏发布穿戴事件。
        migratedInfo = copy(playerBaubleInfo)
        migratedInfo.baubleInfo = dict(playerBaubleInfo.baubleInfo)
        migratedInfo.baubleInfo.update(updates)
        migratedInfo.legacyMigrationReceipt = deepcopy(data)
        savedInfo = dict(playerBaubleInfoDict)
        savedInfo[playerId] = migratedInfo
        if not self.savePlayerBaubleInfo(savedInfo):
            return False
        playerBaubleInfo.baubleInfo.update(updates)
        playerBaubleInfo.legacyMigrationReceipt = migratedInfo.legacyMigrationReceipt
        if updates:
            for slotId, item in updates.iteritems():
                playerBaubleInfo.boardcastPutOnEvent(slotId, item, True)
            playerBaubleInfo._syncToClient()
        return True

    def savePlayerBaubleInfo(self, savedInfo=None):
        """将玩家饰品信息保存到世界信息中。"""
        baubleInfo = pickle.dumps(playerBaubleInfoDict if savedInfo is None else savedInfo)
        return compFactory.CreateExtraData(levelId).SetExtraData(commonConfig.PLAYER_BAUBLE_INFO, baubleInfo)
