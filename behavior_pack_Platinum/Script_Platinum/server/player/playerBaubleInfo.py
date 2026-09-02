# coding=utf-8
from Script_Platinum import commonConfig
from Script_Platinum.QuModLibs.Server import *
from Script_Platinum.data.eventData import BaubleEventData
from Script_Platinum.data.requestData import BaubleCheckRequestData, ChangeBaubleRequestData
from Script_Platinum.data.responseData import BaubleCheckResponseData
from Script_Platinum.data.itemStack import ItemStack
from Script_Platinum.server.data.baubleInfo import BaubleInfo
from Script_Platinum.server.player.playerBaubleSlot import checkSlotValid
from Script_Platinum.utils import developLogging as logging
from Script_Platinum.utils import serverUtils
from Script_Platinum.QuModLibs.Modules.Services.Server import BaseService, QRequests


minecraftEnum = serverApi.GetMinecraftEnum()

isInit = False
playerBaubleInfoDict = {}  # type: dict[str, PlayerBaubleInfo]


def getPlayerBaubleInfo(playerId):  # type: (str) -> PlayerBaubleInfo
    global playerBaubleInfoDict
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
        global isInit
        if isInit:
            return
        isInit = True
        import pickle

        playerBaubleInfoData = compFactory.CreateExtraData(levelId).GetExtraData(commonConfig.PLAYER_BAUBLE_INFO)
        if playerBaubleInfoData:
            try:
                playerBaubleInfo = pickle.loads(playerBaubleInfoData)
                global playerBaubleInfoDict
                playerBaubleInfoDict = playerBaubleInfo
                for _, baubleInfo in playerBaubleInfoDict.items():
                    baubleInfo.loadFromDataInit()
            except Exception as e:
                logging.error("铂: 玩家饰品信息加载失败, 数据可能已损坏. 错误信息: {}".format(e))
        else:
            logging.info("铂: 玩家饰品信息加载完成, 无数据可加载")

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
        from Script_Platinum.server.registry.baubleRegistry import BaubleRegistry

        playerId = getLoaderSystem().rpcPlayerId
        itemComp = compFactory.CreateItem(playerId)
        data = BaubleCheckRequestData.fromDict(data)
        baubleItem = data.baubleInfo
        invItem = itemComp.GetPlayerItem(minecraftEnum.ItemPosType.INVENTORY, data.index, True)
        invItem = ItemStack.fromDict(invItem) if invItem is not None else None
        if not baubleItem or not invItem or not checkSlotValid(data.slotId):
            return BaubleCheckResponseData(False, baubleItem, data.slotId, data.index).toDict()
        if not invItem.isSameItem(baubleItem):
            return BaubleCheckResponseData(False, baubleItem, data.slotId, data.index).toDict()
        if not BaubleRegistry().isValidBauble(baubleItem.name, data.slotType):
            return BaubleCheckResponseData(False, baubleItem, data.slotId, data.index).toDict()
        return BaubleCheckResponseData(True, baubleItem, data.slotId, data.index).toDict()

    def _changeBable(self, playerId, slotId, baubleItem, index=-1):  # type: (str, str, ItemStack, int) -> None
        """更换饰品的内部方法。"""
        if baubleItem and not checkSlotValid(slotId):
            return
        comp = compFactory.CreateItem(playerId)
        comp.SetInvItemNum(index, 0)
        getPlayerBaubleInfo(playerId).changeBaubleInfoBySlotId(slotId, baubleItem, index)
        Call(playerId, "PlaySound", {"soundName": "armor.equip_iron", "targetId": playerId})

    @BaseService.REG_API("server/player/changeBauble")
    def changeBauble(self, data):
        """更换饰品。"""
        playerId = getLoaderSystem().rpcPlayerId
        data = ChangeBaubleRequestData.fromDict(data)
        comp = compFactory.CreateItem(playerId)
        cursorItem = comp.GetPlayerUIItem(playerId, minecraftEnum.PlayerUISlot.CursorSelected)
        baubleItem = data.baubleInfo
        if baubleItem and not checkSlotValid(data.slotId):
            return
        if cursorItem is not None and not ItemStack.fromDict(cursorItem).isEmpty():
            comp.SetPlayerUIItem(playerId, minecraftEnum.PlayerUISlot.CursorSelected, None, False)
        comp.SetInvItemNum(data.index, 0)
        getPlayerBaubleInfo(playerId).changeBaubleInfoBySlotId(data.slotId, baubleItem, data.index)

    @BaseService.REG_API("server/player/syncOldData")
    def syncOldData(self, data):
        """同步旧版本数据。"""
        if serverApi.IsInServer():
            return

        playerId = getLoaderSystem().rpcPlayerId
        playerBaubleInfo = getPlayerBaubleInfo(playerId)
        data = {slotId: itemDict for slotId, itemDict in data.items() if itemDict is not None}
        playerBaubleInfo.setBaubleDict(data, isFirstLoad=True)

    def savePlayerBaubleInfo(self):
        """将玩家饰品信息保存到世界信息中。"""
        import pickle

        baubleInfo = pickle.dumps(playerBaubleInfoDict)
        compFactory.CreateExtraData(levelId).SetExtraData(commonConfig.PLAYER_BAUBLE_INFO, baubleInfo)
