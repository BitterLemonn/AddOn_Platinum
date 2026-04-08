# coding=utf-8
from Script_Platinum.data.itemStack import ItemStack
from Script_Platinum.server.player.playerBaubleSlot import checkSlotValid
from Script_Platinum.utils.ItemFactory import ItemFactory
from Script_Platinum.utils import developLogging as logging
from Script_Platinum.utils import serverUtils
from Script_Platinum.QuModLibs.Modules.Services.Server import BaseService, QRequests

playerBaubleInfoDict = {}  # type: dict[str, PlayerBaubleInfo]


class PlayerBaubleInfo(object):
    def __init__(self, playerId):
        self.playerId = playerId
        self.baubleInfo = {}  # type: dict[str, ItemStack]

    def getBaubleInfoBySlotId(self, slotId):  # type: (str) -> ItemStack|None
        """根据槽位ID获取玩家佩戴的饰品信息"""
        return self.baubleInfo.get(slotId, None)

    def setBaubleInfoBySlotId(self, slotId, itemStack, isChange):  # type: (str, ItemStack, bool) -> None
        """设置玩家佩戴的饰品信息"""
        if not checkSlotValid(slotId):
            logging.w("铂: 尝试设置玩家{}槽位{}的饰品信息,但该槽位ID无效".format(self.playerId, slotId))
            return
        oldItemStack = self.baubleInfo.get(slotId, None)
        if isChange and oldItemStack is not None and not oldItemStack.isEmpty():
            oldItemStack = self.baubleInfo[slotId]
            serverUtils.givePlayerItem(oldItemStack.toDict(), self.playerId)
        self.baubleInfo[slotId] = itemStack
        self._syncToClient()

    def setBaubleDict(self, baubleDicy):  # type: (dict[str, dict]) -> None
        """直接设置玩家佩戴的饰品信息字典"""
        for slotId, itemDict in baubleDicy.items():
            if checkSlotValid(slotId):
                self.baubleInfo[slotId] = ItemStack.fromDict(itemDict)
            else:
                logging.w("铂: 尝试设置玩家{}槽位{}的饰品信息,但该槽位ID无效".format(self.playerId, slotId))
        self._syncToClient()

    def setBaubleDurabilityBySlotId(self, slotId, durability):  # type: (str, int) -> None
        """设置玩家佩戴的饰品耐久度"""
        if not checkSlotValid(slotId):
            logging.w("铂: 尝试设置玩家{}槽位{}的饰品耐久度,但该槽位ID无效".format(self.playerId, slotId))
            return
        if slotId in self.baubleInfo:
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
                pass
            self._syncToClient()
        else:
            logging.w("铂: 尝试减少玩家{}槽位{}的饰品耐久度,但该槽位没有饰品".format(self.playerId, slotId))

    def _syncToClient(self):
        # 同步饰品信息到客户端
        BaseService().syncRequest(
            self.playerId,
            "client/bauble/playerBaubleInfoSync",
            QRequests.Args(
                {
                    slotId: itemStack.toDict() if itemStack is not None else None
                    for slotId, itemStack in self.baubleInfo.items()
                }
            ),
        )

    def boardcastTakeOffEvent(self, slotId):
        """广播玩家饰品脱落事件"""
        

    def boardcastPutOnEvent(self, slotId):
        """广播玩家饰品佩戴事件"""
        BaseService().broadcastRequest(
            "client/bauble/playerBaublePutOn",
            QRequests.Args({"playerId": self.playerId, "slotId": slotId}),
        )
