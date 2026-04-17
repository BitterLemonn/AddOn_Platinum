# coding=utf-8
from Script_Platinum import commonConfig
from Script_Platinum.QuModLibs.Server import *
from Script_Platinum.data.eventData import BaubleEventData
from Script_Platinum.data.requestData import BaubleCheckRequestData, ChangeBaubleRequestData
from Script_Platinum.data.responseData import BaubleCheckResponseData
from Script_Platinum.data.itemStack import ItemStack
from Script_Platinum.server.player.playerBaubleSlot import checkSlotValid
from Script_Platinum.utils.ItemFactory import ItemFactory
from Script_Platinum.utils import developLogging as logging
from Script_Platinum.utils import serverUtils
from Script_Platinum.QuModLibs.Modules.Services.Server import BaseService, QRequests

minecraftEnum = serverApi.GetMinecraftEnum()

playerBaubleInfoDict = {}  # type: dict[str, PlayerBaubleInfo]


def getPlayerBaubleInfo(playerId):
    global playerBaubleInfoDict
    if playerId not in playerBaubleInfoDict:
        playerBaubleInfoDict[playerId] = PlayerBaubleInfo(playerId)
    return playerBaubleInfoDict[playerId]


class PlayerBaubleInfo(object):
    def __init__(self, playerId):
        self.playerId = playerId
        self.baubleInfo = {}  # type: dict[str, ItemStack]

    def getBaubleInfoBySlotId(self, slotId):  # type: (str) -> ItemStack|None
        """根据槽位ID获取玩家佩戴的饰品信息"""
        return self.baubleInfo.get(slotId, None)

    def changeBaubleInfoBySlotId(
        self, slotId, itemStack, index=-1, isChange=False
    ):  # type: (str, ItemStack, int, bool) -> None
        """设置玩家佩戴的饰品信息"""
        if not checkSlotValid(slotId):
            logging.w("铂: 尝试设置玩家{}槽位{}的饰品信息,但该槽位ID无效".format(self.playerId, slotId))
            return
        oldItemStack = self.baubleInfo.get(slotId, None)
        if isChange and oldItemStack is not None and not oldItemStack.isEmpty():
            oldItemStack = self.baubleInfo[slotId]
            serverUtils.givePlayerItem(oldItemStack.toDict(), self.playerId, index)
        self.baubleInfo[slotId] = itemStack
        self._syncToClient()
        self.boardcastTakeOffEvent(slotId, oldItemStack)
        if itemStack is not None and not itemStack.isEmpty():
            self.boardcastPutOnEvent(slotId, itemStack)

    def setBaubleDict(self, baubleDict, isFirstLoad=False):  # type: (dict[str, dict], bool) -> None
        """直接设置玩家佩戴的饰品信息字典, 用于初始化玩家饰品信息"""
        for slotId, itemDict in baubleDict.items():
            if checkSlotValid(slotId):
                oldItemStack = self.baubleInfo.get(slotId, None)
                self.baubleInfo[slotId] = ItemStack.fromDict(itemDict)
                if oldItemStack is not None and not oldItemStack.isEmpty():
                    self.boardcastTakeOffEvent(slotId, oldItemStack, isFirstLoad)
                self.boardcastPutOnEvent(slotId, self.baubleInfo[slotId], isFirstLoad)
            else:
                logging.w("铂: 尝试设置玩家{}槽位{}的饰品信息,但该槽位ID无效".format(self.playerId, slotId))
        self._syncToClient()

    def setBaubleDurabilityBySlotId(self, slotId, durability):  # type: (str, int) -> None
        """设置玩家佩戴的饰品耐久度"""
        if not checkSlotValid(slotId):
            logging.w("铂: 尝试设置玩家{}槽位{}的饰品耐久度,但该槽位ID无效".format(self.playerId, slotId))
            return
        if slotId in self.baubleInfo:
            if durability <= 0:
                # 耐久度为0或更低时,直接删除饰品
                # 播放饰品破碎音效 TODO
                self.boardcastTakeOffEvent(slotId, self.baubleInfo[slotId])
                self.baubleInfo[slotId] = None
                self._syncToClient()
                return
            itemStack = self.baubleInfo[slotId]
            itemDict = ItemFactory.fromDict(itemStack.toDict()).setDurability(durability).build()
            self.baubleInfo[slotId] = ItemStack.fromDict(itemDict)
            self._syncToClient()
        else:
            logging.w("铂: 尝试设置玩家{}槽位{}的饰品耐久度,但该槽位没有饰品".format(self.playerId, slotId))

    def decreaseBaubleDurabilityBySlotId(self, slotId, decreaseAmount):  # type: (str, int) -> None
        """减少玩家佩戴的饰品耐久度"""
        if not checkSlotValid(slotId):
            logging.w("铂: 尝试减少玩家{}槽位{}的饰品耐久度,但该槽位ID无效".format(self.playerId, slotId))
            return
        if slotId in self.baubleInfo:
            itemStack = self.baubleInfo[slotId]
            item = ItemFactory.fromDict(itemStack.toDict())
            itemDict = item.setDurability(item.getDurability() - decreaseAmount).build()
            itemDict = itemDict if item.getDurability() > 0 else None
            self.baubleInfo[slotId] = ItemStack.fromDict(itemDict) if itemDict is not None else None
            if itemDict is None:
                # 播放饰品破碎音效 TODO
                self.boardcastTakeOffEvent(slotId, itemStack)
                pass
            self._syncToClient()
        else:
            logging.w("铂: 尝试减少玩家{}槽位{}的饰品耐久度,但该槽位没有饰品".format(self.playerId, slotId))

    def _syncToClient(self):
        # 同步饰品信息到客户端
        baubleDict = {
            slotId: itemStack.toDict() if itemStack is not None else None
            for slotId, itemStack in self.baubleInfo.items()
        }
        BaseService().syncRequest(
            self.playerId,
            "client/bauble/syncFromServer",
            QRequests.Args(baubleDict),
        )

    def boardcastTakeOffEvent(self, slotId, itemStack):
        """广播玩家饰品脱落事件"""
        from Script_Platinum.server.registry.slotRegistry import SlotRegistry

        system = serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER)
        slotType = SlotRegistry().getSlotTypeById(slotId)
        slotIndex = SlotRegistry().getSlotIndexById(slotId)
        baubleData = BaubleEventData(self.playerId, slotId, slotType, slotIndex, itemStack, False)
        system.BroadcastEvent(
            commonConfig.BAUBLE_UNEQUIPPED_EVENT,
            baubleData.dumpToDict(),
        )

    def boardcastPutOnEvent(self, slotId, itemStack, isFirstLoad=False):
        """广播玩家饰品佩戴事件"""
        from Script_Platinum.server.registry.slotRegistry import SlotRegistry

        system = serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER)
        slotType = SlotRegistry().getSlotTypeById(slotId)
        slotIndex = SlotRegistry().getSlotIndexById(slotId)
        baubleData = BaubleEventData(self.playerId, slotId, slotType, slotIndex, itemStack, False)
        system.BroadcastEvent(
            commonConfig.BAUBLE_EQUIPPED_EVENT,
            baubleData.dumpToDict(),
        )


@BaseService.Init
class PlayerBaubleInfoServerService(BaseService):
    """玩家饰品信息服务"""

    def __init__(self):
        BaseService.__init__(self)

    @BaseService.REG_API("server/player/baubleCheck")
    def checkBaubleAvailable(self, data):
        """检查饰品是否可以装备"""
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

    @BaseService.REG_API("server/player/changeBauble")
    def changeBauble(self, data):
        """更换饰品"""
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
        playerBaubleInfo = getPlayerBaubleInfo(playerId)
        playerBaubleInfo.changeBaubleInfoBySlotId(data.slotId, baubleItem, data.index, True)
 