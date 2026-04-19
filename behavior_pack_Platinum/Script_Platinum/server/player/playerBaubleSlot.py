# coding=utf-8

from Script_Platinum.QuModLibs.Server import *
from Script_Platinum.QuModLibs.Modules.Services.Server import BaseService, QRequests
from Script_Platinum.commonConfig import PLAYER_SLOT_DATA
from Script_Platinum.data.slotData import BaubleSlotData
from Script_Platinum.server.items.itemService import SlotRegistry
from Script_Platinum.utils.serverUtils import compFactory
from Script_Platinum.utils import developLogging as logging

playerSlotList = {}  # type: dict[int, BaubleSlotData]


def checkSlotValid(slotId):
    from Script_Platinum.server.registry.slotRegistry import SlotRegistry

    return slotId in SlotRegistry().getBaubleSlotIdList()


def getPlayerSlotList(playerId):
    return playerSlotList.get(playerId, [])


def setPlayerSlotList(playerId, slotList):
    global playerSlotList
    playerSlotList[playerId] = slotList
    _syncToClient(playerId)


def addPlayerSlot(playerId, slotData):
    global playerSlotList
    if playerId not in playerSlotList:
        playerSlotList[playerId] = []
    if slotData.identifier not in [slot.identifier for slot in playerSlotList[playerId]]:
        playerSlotList[playerId].append(slotData)
        _syncToClient(playerId)
    else:
        logging.error("铂: 玩家{}的槽位{}已存在, 无法添加".format(playerId, slotData.identifier))


def deletePlayerSlotById(playerId, slotId):
    global playerSlotList
    if playerId in playerSlotList and slotId in [slot.identifier for slot in playerSlotList[playerId]]:
        playerSlotList[playerId] = [slot for slot in playerSlotList[playerId] if slot.identifier != slotId]
        _syncToClient(playerId)
        # 移除饰品信息中的对应槽位数据
        from Script_Platinum.server.player.playerBaubleInfo import getPlayerBaubleInfo, PlayerBaubleInfo

        playerBaubleInfo = getPlayerBaubleInfo(playerId)  # type: PlayerBaubleInfo
        playerBaubleInfo.changeBaubleInfoBySlotId(slotId, None)
    else:
        logging.error("铂: 玩家{}的槽位{}不存在, 无法删除".format(playerId, slotId))


def _syncToClient(playerId):
    # 同步槽位数据到客户端
    playerSlotList = getPlayerSlotList(playerId)
    PlayerBaubleSlotServerService.access().syncRequest(
        playerId, "client/slot/playerSlotSync", QRequests.Args([slot.__dict__ for slot in playerSlotList])
    )
    # 保存到世界信息
    playerSlotInfo = compFactory.CreateExtraData(levelId).GetExtraData(PLAYER_SLOT_DATA) or {}
    playerSlotInfo[playerId] = [slot.__dict__ for slot in playerSlotList]
    compFactory.CreateExtraData(levelId).SetExtraData(PLAYER_SLOT_DATA, playerSlotInfo)


@BaseService.Init
class PlayerBaubleSlotServerService(BaseService):

    def __init__(self):
        BaseService.__init__(self)
        self.slotRegistry = SlotRegistry()  # type: SlotRegistry

    @BaseService.Listen("AddServerPlayerEvent")
    def onAddServerPlayer(self, data):
        playerId = data["id"]
        # 读取世界信息中的槽位数据
        playerSlotInfo = compFactory.CreateExtraData(levelId).GetExtraData(PLAYER_SLOT_DATA) or {}
        slotListData = playerSlotInfo.get(playerId, [])
        if slotListData:
            slotList = [BaubleSlotData(**slotData) for slotData in slotListData]
            # 同步未拥有的默认槽位
            defaultSlots = self.slotRegistry.getBaubleSlotList(defaultFilter=True)
            ownedSlotIds = [slot.identifier for slot in slotList]
            for defaultSlot in defaultSlots:
                if defaultSlot.identifier not in ownedSlotIds:
                    slotList.append(defaultSlot)
            setPlayerSlotList(playerId, slotList)
        else:
            # 请求默认槽位数据
            defaultSlots = self.slotRegistry.getBaubleSlotList(defaultFilter=True)
            setPlayerSlotList(playerId, defaultSlots)

    @BaseService.REG_API("server/slot/requestPlayerSlotList")
    def requestPlayerSlotList(self):
        playerId = getLoaderSystem().rpcPlayerId
        slotList = getPlayerSlotList(playerId)
        return [slot.__dict__ for slot in slotList]

    @BaseService.REG_API("server/player/syncCommandSlot")
    def syncCommandSlot(self, commandSlotList):
        """同步指令添加的槽位数据 (仅用于旧版本数据迁移, 不久后将移除)"""
        if serverApi.IsInServer():
            return

        playerId = getLoaderSystem().rpcPlayerId

        from Script_Platinum.utils.oldVersionFixer import oldSlotTypeToNew

        for slotData in commandSlotList:
            # 注册新槽位
            isDefault = slotData.get("isDefault", False)
            slotId = slotData["slotIdentifier"]
            slotType = oldSlotTypeToNew(slotData["slotType"])
            baubleSlotData = BaubleSlotData(None, None, slotId, slotType, isDefault, True)
            self.slotRegistry.registerSlot(baubleSlotData)
            if not isDefault:
                addPlayerSlot(playerId, baubleSlotData)
