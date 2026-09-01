# coding=utf-8
import random
from Script_Platinum import commonConfig
from Script_Platinum.QuModLibs.Server import *
from Script_Platinum.data.eventData import EntityBaubleEventData, EntityBaubleDropEventData
from Script_Platinum.server.data.baubleInfo import BaubleInfo
from Script_Platinum.utils import developLogging as logging
from Script_Platinum.utils.serverUtils import compFactory
from Script_Platinum.QuModLibs.Modules.Services.Server import BaseService


entityBaubleInfoDict = {}  # type: dict[str, EntityBaubleInfo]


def getEntityBaubleInfo(entityId):  # type: (str) -> BaubleInfo
    """获取实体饰品信息；玩家目标复用玩家数据，其他实体使用实体ModAttr持久化。"""
    if entityId and Entity(entityId).IsPlayer:
        from Script_Platinum.server.player.playerBaubleInfo import getPlayerBaubleInfo

        return getPlayerBaubleInfo(entityId)
    if entityId not in entityBaubleInfoDict:
        baubleInfo = EntityBaubleInfo(entityId)
        entityBaubleInfoDict[entityId] = baubleInfo
        baubleInfo.loadEntityDataInit()
    return entityBaubleInfoDict[entityId]


class EntityBaubleInfo(BaubleInfo):
    def loadEntityDataInit(self):
        """从实体ModAttr加载饰品，并恢复穿戴事件。"""
        comp = compFactory.CreateModAttr(self.targetId)
        baubleDict = comp.GetAttr(commonConfig.ENTITY_BAUBLE_INFO, {})
        dropProbDict = comp.GetAttr(commonConfig.ENTITY_BAUBLE_DROP_PROBABILITY, {})
        if isinstance(dropProbDict, dict):
            self.dropProbability = {
                k: float(v) for k, v in dropProbDict.items() if isinstance(v, (int, float))
            }
        if not isinstance(baubleDict, dict):
            logging.warning("铂: 生物{}饰品ModAttr数据无效".format(self.targetId))
            return
        self.setBaubleDict(baubleDict, True, False)

    def _updateDropProbability(self, slotId, itemStack, dropProbability):
        if itemStack is None or itemStack.isEmpty():
            self.dropProbability.pop(slotId, None)
        else:
            self.dropProbability[slotId] = float(dropProbability)

    def _updateLoadedDropProbability(self, slotId, dropProbability):
        if isinstance(dropProbability, dict):
            prob = dropProbability.get(slotId, 1.0)
        elif isinstance(dropProbability, (int, float)):
            prob = float(dropProbability)
        else:
            prob = self.dropProbability.get(slotId, 1.0)
        self.dropProbability[slotId] = float(prob)

    def _save(self):
        baubleDict = {
            slotId: itemStack.toDict() if itemStack is not None else None
            for slotId, itemStack in self.baubleInfo.items()
        }
        modAttrComp = compFactory.CreateModAttr(self.targetId)
        modAttrComp.SetAttr(commonConfig.ENTITY_BAUBLE_INFO, baubleDict, True)
        modAttrComp.SetAttr(commonConfig.ENTITY_BAUBLE_DROP_PROBABILITY, self.dropProbability, True)

    def _createTakeOffEventData(self, slotId, slotType, slotIndex, itemStack):
        return (
            EntityBaubleEventData(self.targetId, slotId, slotType, slotIndex, itemStack, False),
            commonConfig.ENTITY_BAUBLE_UNEQUIPPED_EVENT,
        )

    def _createPutOnEventData(self, slotId, slotType, slotIndex, itemStack, isFirstLoad):
        return (
            EntityBaubleEventData(self.targetId, slotId, slotType, slotIndex, itemStack, isFirstLoad),
            commonConfig.ENTITY_BAUBLE_EQUIPPED_EVENT,
        )


@BaseService.Init
class EntityBaubleInfoServerService(BaseService):
    """非玩家实体饰品信息服务。"""

    def __init__(self):
        BaseService.__init__(self)
        self.deathEntityIds = set()

    @BaseService.Listen("MobDieEvent")
    def onMobDieEvent(self, data):
        """实体死亡时按槽位概率掉落饰品。"""
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
        self.deathEntityIds.add(entityId)
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
        """清理非玩家实体运行时饰品及属性修饰符。"""
        entityId = data["id"]
        entityBaubleInfo = entityBaubleInfoDict.pop(entityId, None)
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
        """区块卸载移除实体时复用实体移除清理流程。"""
        for entityId in data.get("entities", []):
            self.onEntityRemoveEvent({"id": entityId})
