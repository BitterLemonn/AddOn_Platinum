# coding=utf-8
import random
from Script_Platinum import commonConfig
from Script_Platinum.QuModLibs.Server import *
from Script_Platinum.data.eventData import (
    BaubleEventData,
    EntityBaubleEventData,
    EntityBaubleDropEventData,
)
from Script_Platinum.data.requestData import BaubleCheckRequestData, ChangeBaubleRequestData
from Script_Platinum.data.responseData import BaubleCheckResponseData
from Script_Platinum.data.itemStack import ItemStack
from Script_Platinum.server.player.playerBaubleSlot import checkSlotValid
from Script_Platinum.utils.ItemFactory import ItemFactory
from Script_Platinum.utils import developLogging as logging
from Script_Platinum.utils import serverUtils
from Script_Platinum.QuModLibs.Modules.Services.Server import BaseService, QRequests

minecraftEnum = serverApi.GetMinecraftEnum()

isInit = False
playerBaubleInfoDict = {}  # type: dict[str, PlayerBaubleInfo]
entityBaubleInfoDict = {}  # type: dict[str, PlayerBaubleInfo]


def getPlayerBaubleInfo(playerId):  # type: (str) -> PlayerBaubleInfo
    global playerBaubleInfoDict
    if playerId not in playerBaubleInfoDict:
        playerBaubleInfoDict[playerId] = PlayerBaubleInfo(playerId)
    return playerBaubleInfoDict[playerId]


def getEntityBaubleInfo(entityId):  # type: (str) -> PlayerBaubleInfo
    """获取实体饰品信息；目标沿用世界数据，非目标使用实体ModAttr持久化。"""
    if entityId and Entity(entityId).IsPlayer:
        return getPlayerBaubleInfo(entityId)
    if entityId not in entityBaubleInfoDict:
        baubleInfo = PlayerBaubleInfo(entityId, False)
        entityBaubleInfoDict[entityId] = baubleInfo
        baubleInfo.loadEntityDataInit()
    return entityBaubleInfoDict[entityId]


class PlayerBaubleInfo(object):
    def __init__(self, playerId, isPlayer=True):
        self.playerId = playerId
        self.isPlayer = isPlayer
        self.baubleInfo = {}  # type: dict[str, ItemStack]
        self.dropProbability = {}  # type: dict[str, float]

    def _isPlayerTarget(self):
        # 旧存档对象没有 isPlayer 字段，默认按目标处理。
        return getattr(self, "isPlayer", True)

    def loadFromDataInit(self):
        """当从存档数据中加载目标饰品信息时调用, 用于触发饰品的穿戴事件"""
        for slotId, itemStack in self.baubleInfo.items():
            if itemStack is not None and not itemStack.isEmpty():
                self.boardcastPutOnEvent(slotId, itemStack, True)

    def loadEntityDataInit(self):
        """从实体ModAttr加载生物饰品，并恢复穿戴事件。"""
        if self._isPlayerTarget():
            return
        comp = compFactory.CreateModAttr(self.playerId)
        baubleDict = comp.GetAttr(commonConfig.ENTITY_BAUBLE_INFO, {})
        dropProbDict = comp.GetAttr(commonConfig.ENTITY_BAUBLE_DROP_PROBABILITY, {})
        if isinstance(dropProbDict, dict):
            self.dropProbability = {k: float(v) for k, v in dropProbDict.items() if isinstance(v, (int, float))}
        if not isinstance(baubleDict, dict):
            logging.warning("铂: 生物{}饰品ModAttr数据无效".format(self.playerId))
            return
        self.setBaubleDict(baubleDict, True, False)

    def getEmptyOrFirstSlotByList(self, slotTypeList):
        """根据槽位类型列表获取一个空的槽位ID, 没有空槽位则返回该类型的第一个槽位ID"""
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
        """根据槽位ID获取目标佩戴的饰品信息"""
        return self.baubleInfo.get(slotId, None)

    def changeBaubleInfoBySlotId(
        self, slotId, itemStack, index=-1, isChanged=True, dropProbability=1.0
    ):  # type: (str, int, ItemStack, bool, float) -> None
        """设置目标佩戴的饰品信息"""
        if not checkSlotValid(slotId):
            logging.w("铂: 尝试设置目标{}槽位{}的饰品信息,但该槽位ID无效".format(self.playerId, slotId))
            return
        oldItemStack = self.baubleInfo.get(slotId, None)
        if oldItemStack is not None and not oldItemStack.isEmpty() and isChanged and self._isPlayerTarget():
            oldItemStack = self.baubleInfo[slotId]
            serverUtils.givePlayerItem(oldItemStack.toDict(), self.playerId, index)
        self.baubleInfo[slotId] = itemStack
        if not self._isPlayerTarget():
            if itemStack is None or itemStack.isEmpty():
                self.dropProbability.pop(slotId, None)
            else:
                self.dropProbability[slotId] = float(dropProbability)
        self._syncToClient()
        if oldItemStack is not None and not oldItemStack.isEmpty():
            self.boardcastTakeOffEvent(slotId, oldItemStack)
        if itemStack is not None and not itemStack.isEmpty():
            self.boardcastPutOnEvent(slotId, itemStack)

        # 保存到世界信息中
        self._save()

    def setBaubleDict(
        self, baubleDict, isFirstLoad=False, needSave=True, dropProbability=None
    ):  # type: (dict[str, dict], bool, bool, float|dict[str, float]|None) -> None
        """直接设置目标佩戴的饰品信息字典, 用于初始化目标饰品信息"""
        if not isinstance(baubleDict, dict):
            return
        for slotId, itemDict in baubleDict.items():
            if itemDict is None:
                continue
            if not isinstance(itemDict, dict):
                logging.warning("铂: 目标{}槽位{}的饰品数据无效".format(self.playerId, slotId))
                continue
            if checkSlotValid(slotId):
                oldItemStack = self.baubleInfo.get(slotId, None)
                self.baubleInfo[slotId] = ItemStack.fromDict(itemDict)
                if not self._isPlayerTarget():
                    if isinstance(dropProbability, dict):
                        prob = dropProbability.get(slotId, 1.0)
                    elif isinstance(dropProbability, (int, float)):
                        prob = float(dropProbability)
                    else:
                        prob = self.dropProbability.get(slotId, 1.0)
                    self.dropProbability[slotId] = float(prob)
                if oldItemStack is not None and not oldItemStack.isEmpty():
                    self.boardcastTakeOffEvent(slotId, oldItemStack)
                self.boardcastPutOnEvent(slotId, self.baubleInfo[slotId], isFirstLoad)
            else:
                logging.warning("铂: 尝试设置目标{}槽位{}的饰品信息,但该槽位ID无效".format(self.playerId, slotId))
        self._syncToClient()
        # 保存到世界信息中
        if needSave:
            self._save()

    def setBaubleDurabilityBySlotId(self, slotId, durability):  # type: (str, int) -> None
        """设置目标佩戴的饰品耐久度"""
        if not checkSlotValid(slotId):
            logging.warning("铂: 尝试设置目标{}槽位{}的饰品耐久度,但该槽位ID无效".format(self.playerId, slotId))
            return
        if slotId in self.baubleInfo:
            if durability <= 0:
                # 耐久度为0或更低时,直接删除饰品
                # 播放物品破碎音效
                if self._isPlayerTarget():
                    Call(self.playerId, "PlaySound", {"soundName": "random.break", "targetId": self.playerId})
                self.boardcastTakeOffEvent(slotId, self.baubleInfo[slotId])
                self.baubleInfo[slotId] = None
                self._syncToClient()
                self._save()
                return
            itemStack = self.baubleInfo[slotId]
            itemDict = ItemFactory.fromDict(itemStack.toDict()).setDurability(durability).build()
            self.baubleInfo[slotId] = ItemStack.fromDict(itemDict)
            self._syncToClient()
        else:
            logging.warning("铂: 尝试设置目标{}槽位{}的饰品耐久度,但该槽位没有饰品".format(self.playerId, slotId))
        # 保存到世界信息中
        self._save()

    def decreaseBaubleDurabilityBySlotId(self, slotId, decreaseAmount):  # type: (str, int) -> None
        """减少目标佩戴的饰品耐久度"""
        if not checkSlotValid(slotId):
            logging.warning("铂: 尝试减少目标{}槽位{}的饰品耐久度,但该槽位ID无效".format(self.playerId, slotId))
            return
        if slotId in self.baubleInfo:
            itemStack = self.baubleInfo[slotId]
            item = ItemFactory.fromDict(itemStack.toDict())
            itemDict = item.setDurability(item.getDurability() - decreaseAmount).build()
            itemDict = itemDict if item.getDurability() > 0 else None
            self.baubleInfo[slotId] = ItemStack.fromDict(itemDict) if itemDict is not None else None
            if itemDict is None:
                # 播放饰品破碎音效
                if self._isPlayerTarget():
                    Call(self.playerId, "PlaySound", {"soundName": "random.break", "targetId": self.playerId})
                self.boardcastTakeOffEvent(slotId, itemStack)
                pass
            self._syncToClient()
        else:
            logging.warning("铂: 尝试减少目标{}槽位{}的饰品耐久度,但该槽位没有饰品".format(self.playerId, slotId))

        # 保存到世界信息中
        self._save()

    def _save(self):
        if self._isPlayerTarget():
            PlayerBaubleInfoServerService.access().savePlayerBaubleInfo()
            return
        baubleDict = {
            slotId: itemStack.toDict() if itemStack is not None else None
            for slotId, itemStack in self.baubleInfo.items()
        }
        modAttrComp = compFactory.CreateModAttr(self.playerId)
        modAttrComp.SetAttr(commonConfig.ENTITY_BAUBLE_INFO, baubleDict, True)
        modAttrComp.SetAttr(commonConfig.ENTITY_BAUBLE_DROP_PROBABILITY, self.dropProbability, True)

    def _syncToClient(self):
        if not self._isPlayerTarget():
            return
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
        """广播目标饰品脱落事件"""
        from Script_Platinum.server.registry.slotRegistry import SlotRegistry
        from Script_Platinum.utils.oldVersionFixer import newSlotTypeToOld

        system = serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER)
        slotType = SlotRegistry().getSlotTypeById(slotId)
        oldSlotType = newSlotTypeToOld(slotType)
        slotIndex = SlotRegistry().getSlotIndexById(slotId)
        if self._isPlayerTarget():
            baubleData = BaubleEventData(self.playerId, slotId, oldSlotType, slotIndex, itemStack, False)
            eventName = commonConfig.BAUBLE_UNEQUIPPED_EVENT
        else:
            baubleData = EntityBaubleEventData(self.playerId, slotId, oldSlotType, slotIndex, itemStack, False)
            eventName = commonConfig.ENTITY_BAUBLE_UNEQUIPPED_EVENT
        system.BroadcastEvent(
            eventName,
            baubleData.dumpToDict(),
        )
        if self._isPlayerTarget():
            PlayerBaubleInfoServerService.access().syncRequest(
                self.playerId, "client/bauble/unequipBaubleBoardcast", QRequests.Args(baubleData.dumpToDict())
            )

    def boardcastPutOnEvent(self, slotId, itemStack, isFirstLoad=False):
        """广播目标饰品佩戴事件"""
        from Script_Platinum.server.registry.slotRegistry import SlotRegistry
        from Script_Platinum.utils.oldVersionFixer import newSlotTypeToOld

        system = serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER)
        slotType = SlotRegistry().getSlotTypeById(slotId)
        oldSlotType = newSlotTypeToOld(slotType)
        slotIndex = SlotRegistry().getSlotIndexById(slotId)
        if self._isPlayerTarget():
            baubleData = BaubleEventData(self.playerId, slotId, oldSlotType, slotIndex, itemStack, isFirstLoad)
            eventName = commonConfig.BAUBLE_EQUIPPED_EVENT
        else:
            baubleData = EntityBaubleEventData(self.playerId, slotId, oldSlotType, slotIndex, itemStack, isFirstLoad)
            eventName = commonConfig.ENTITY_BAUBLE_EQUIPPED_EVENT
        system.BroadcastEvent(
            eventName,
            baubleData.dumpToDict(),
        )
        if self._isPlayerTarget():
            PlayerBaubleInfoServerService.access().syncRequest(
                self.playerId, "client/bauble/equipBaubleBoardcast", QRequests.Args(baubleData.dumpToDict())
            )


@BaseService.Init
class PlayerBaubleInfoServerService(BaseService):
    """目标饰品信息服务"""

    def __init__(self):
        BaseService.__init__(self)
        self.deathEntityIds = set()

    @BaseService.Listen("PlayerDieEvent")
    def onPlayerDieEvent(self, data):
        # 检查游戏规则
        rule = compFactory.CreateGame(levelId).GetGameRulesInfoServer()
        isKeep = rule.get("cheat_info", {}).get("keep_inventory")
        if not isKeep:
            # 移除目标穿戴饰品
            playerId = data["id"]
            playerBaubleInfo = getPlayerBaubleInfo(playerId)
            for slotId, itemStack in playerBaubleInfo.baubleInfo.items():
                if itemStack is None or itemStack.isEmpty():
                    continue
                # 设置槽位信息为None
                playerBaubleInfo.changeBaubleInfoBySlotId(slotId, None, -1, False)
                # 掉落饰品
                pos = Entity(playerId).Pos
                dimension = Entity(playerId).Dm
                System.CreateEngineItemEntity(itemStack.toDict(), dimension, pos)

    @BaseService.Listen("MobDieEvent")
    def onMobDieEvent(self, data):
        """生物死亡事件：根据概率计算掉落饰品，广播事件并在下一帧掉落。"""
        entityId = data.get("id")
        if not entityId or Entity(entityId).IsPlayer:
            return
        entityBaubleInfo = entityBaubleInfoDict.get(entityId)
        if entityBaubleInfo is None:
            return
        itemList = []
        for slotId, itemStack in entityBaubleInfo.baubleInfo.items():
            if itemStack is None or itemStack.isEmpty():
                continue
            prob = entityBaubleInfo.dropProbability.get(slotId, 1.0)
            if prob >= 1.0 or random.random() < prob:
                itemList.append(itemStack.toDict())
        if not itemList:
            return
        dropData = EntityBaubleDropEventData(entityId, itemList, False)
        dropDict = dropData.dumpToDict()
        system = serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER)
        system.BroadcastEvent(commonConfig.ENTITY_BAUBLE_DROP_BEFORE_EVENT, dropDict)
        # 记录死亡实体ID
        self.deathEntityIds.add(entityId)
        # 广播脱下事件
        for slotId, itemStack in entityBaubleInfo.baubleInfo.items():
            if itemStack is not None and not itemStack.isEmpty():
                entityBaubleInfo.boardcastTakeOffEvent(slotId, itemStack)

        pos = Entity(entityId).Pos
        dimension = Entity(entityId).Dm
        if pos is None:
            return

        def actualDrop():
            if dropDict.get("cancel", False):
                return
            currentItems = dropDict.get("itemList", [])
            for item in currentItems:
                if item and isinstance(item, dict):
                    System.CreateEngineItemEntity(item, dimension, pos)

        compFactory.CreateGame(levelId).AddTimer(0.0, actualDrop)

    @BaseService.Listen("AddEntityServerEvent")
    def onAddEntityServerEvent(self, data):
        """实体从存档加载时恢复ModAttr中的饰品。"""
        entityId = data["id"]
        comp = compFactory.CreateModAttr(entityId)
        baubleDict = comp.GetAttr(commonConfig.ENTITY_BAUBLE_INFO, {})
        if isinstance(baubleDict, dict) and baubleDict:
            getEntityBaubleInfo(entityId)

    @BaseService.Listen("EntityRemoveEvent")
    def onEntityRemoveEvent(self, data):
        """清理非玩家实体的运行时饰品及属性修饰符。"""
        entityId = data["id"]
        entityBaubleInfo = entityBaubleInfoDict.pop(entityId, None)
        # 检查实体是否已死亡
        if entityId in self.deathEntityIds:
            self.deathEntityIds.discard(entityId)
            return
        if entityBaubleInfo is None:
            return
        for slotId, itemStack in entityBaubleInfo.baubleInfo.items():
            if itemStack is not None and not itemStack.isEmpty():
                entityBaubleInfo.boardcastTakeOffEvent(slotId, itemStack)
        from Script_Platinum.server.attribute.attributeModifier import PlatinumAttributeModifierService

        PlatinumAttributeModifierService.access().clearEntity(entityId, False)

    @BaseService.Listen("ChunkAcquireDiscardedServerEvent")
    def onChunkAcquireDiscardedServerEvent(self, data):
        """区块卸载移除实体时，复用实体移除清理流程。"""
        for entityId in data.get("entities", []):
            self.onEntityRemoveEvent({"id": entityId})

    @BaseService.Listen("ClientLoadAddonsFinishServerEvent")
    def onClientLoadAddonsFinishServerEvent(self, data):
        global isInit
        if isInit:
            return
        isInit = True
        # 从世界信息中加载目标饰品信息
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
                logging.error("铂: 目标饰品信息加载失败, 数据可能已损坏. 错误信息: {}".format(e))
        else:
            logging.info("铂: 目标饰品信息加载完成, 无数据可加载")

    @BaseService.REG_API("server/player/requestBaubleInfo")
    def requestBaubleInfo(self, _=None):
        """客户端请求目标饰品信息"""
        playerId = getLoaderSystem().rpcPlayerId
        playerBaubleInfo = getPlayerBaubleInfo(playerId)
        baubleDict = {
            slotId: itemStack.toDict() if itemStack is not None else None
            for slotId, itemStack in playerBaubleInfo.baubleInfo.items()
        }
        return baubleDict

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

    def _changeBable(self, playerId, slotId, baubleItem, index=-1):  # type: (str, str, ItemStack, int) -> None
        """更换饰品的内部方法"""
        if baubleItem and not checkSlotValid(slotId):
            return
        comp = compFactory.CreateItem(playerId)
        comp.SetInvItemNum(index, 0)
        playerBaubleInfo = getPlayerBaubleInfo(playerId)
        playerBaubleInfo.changeBaubleInfoBySlotId(slotId, baubleItem, index)
        Call(playerId, "PlaySound", {"soundName": "armor.equip_iron", "targetId": playerId})

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
        playerBaubleInfo.changeBaubleInfoBySlotId(data.slotId, baubleItem, data.index)

    @BaseService.REG_API("server/player/syncOldData")
    def syncOldData(self, data):
        """同步旧版本数据, 危险操作, 仅在旧版本更新后的一段时间内使用(不允许山头环境使用)"""
        if serverApi.IsInServer():
            return

        playerId = getLoaderSystem().rpcPlayerId
        playerBaubleInfo = getPlayerBaubleInfo(playerId)
        # 删除旧数据中value为null的数据
        data = {slotId: itemDict for slotId, itemDict in data.items() if itemDict is not None}
        playerBaubleInfo.setBaubleDict(data, isFirstLoad=True)

    def savePlayerBaubleInfo(self):
        """将目标饰品信息保存到世界信息中"""
        import pickle

        baubleInfo = pickle.dumps(playerBaubleInfoDict)
        compFactory.CreateExtraData(levelId).SetExtraData(commonConfig.PLAYER_BAUBLE_INFO, baubleInfo)
