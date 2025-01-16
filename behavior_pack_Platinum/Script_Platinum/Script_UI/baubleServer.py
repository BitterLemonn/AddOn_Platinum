# coding=utf-8
from .baubleInfoRegister import BaubleInfoRegister
from .baubleSlotRegister import BaubleSlotRegister
from ..BroadcastEvent.getPlayerBaubleInfoEvent import GetPlayerBaubleInfoServerEvent
from ..QuModLibs.Modules.Services.Globals import QRequests
from ..QuModLibs.Server import *
from ..QuModLibs.Modules.Services.Server import BaseService
from ..commonConfig import BaubleDict
from .. import serverUtil
import logging


@BaseService.Init
class BaubleServerService(BaseService):
    def __init__(self):
        BaseService.__init__(self)
        self.itemComp = serverApi.GetEngineCompFactory().CreateItem(levelId)
        self.itemComp.GetUserDataInEvent("ServerItemTryUseEvent")

    # 检查饰品是否可用安装至指定槽位
    @staticmethod
    def checkBaubleAvailable(baubleSlotType, baubleName):
        baubleInfoDict = BaubleInfoRegister.getBaubleInfoDict()
        baubleInfo = baubleInfoDict.get(baubleName)
        if baubleInfo and baubleSlotType:
            baubleSlotList = baubleInfo.get("baubleSlot")
            if baubleSlotType in baubleSlotList:
                return True
        return False

    # 改变饰品栏入口位置
    @BaseService.Listen(Events.ServerChatEvent)
    def onServerChatEvent(self, data):
        playerId = data["playerId"]
        msg = data["message"]
        if msg.startswith("#platinum_"):
            msg = msg.replace("#platinum_", "")
            if msg in ["left_top", "right_top", "left_bottom", "right_bottom"]:
                self.syncRequest(playerId, "platinum/changeUiPosition", QRequests.Args(msg))
                data["cancel"] = True
                comp = serverApi.GetEngineCompFactory().CreateMsg(playerId)

                position = "左上角" if msg == "left_top" else "右上角" \
                    if msg == "right_top" else "左下角" if msg == "left_bottom" else "右下角"

                comp.NotifyOneMessage(playerId, "铂: 饰品栏按钮已切换至{}".format(position))

    # 右键穿戴饰品
    @BaseService.Listen(Events.ServerItemTryUseEvent)
    def onServerItemTryUseEvent(self, data):
        itemUsed = data["itemDict"]
        playerId = data["playerId"]
        itemInfo = self.itemComp.GetItemBasicInfo(itemUsed["newItemName"])
        if itemInfo["itemType"] != "armor" and itemInfo["itemType"] != "food":
            baubleRegDict = BaubleInfoRegister.getBaubleInfoDict()
            if itemUsed["newItemName"] in baubleRegDict.keys():
                baubleSlotTypeList = baubleRegDict[itemUsed["newItemName"]]["baubleSlot"]
                itemComp = serverApi.GetEngineCompFactory().CreateItem(playerId)
                selectedSlotId = itemComp.GetSelectSlotId()
                self.syncRequest(playerId, "platinum/tryEquipBauble",
                                 QRequests.Args(itemUsed, selectedSlotId, baubleSlotTypeList))

    # 死亡掉落物品
    @BaseService.Listen(Events.PlayerDieEvent)
    def onPlayerDieEvent(self, data):
        playerId = data["id"]
        pos = Entity(playerId).FootPos
        dimensionId = Entity(playerId).Dm
        comp = serverApi.GetEngineCompFactory().CreateGame(levelId)
        gameRule = comp.GetGameRulesInfoServer()
        keepInv = gameRule["cheat_info"]["keep_inventory"]
        if not keepInv:
            self.syncRequest(playerId, "platinum/onPlayerDie", QRequests.Args(pos, dimensionId))

    # 生成物品
    @BaseService.REG_API("platinum/spawnItem")
    def spawnItem(self, itemDictList, pos, dimensionId):
        for itemDict in itemDictList:
            self.itemComp.SpawnItemToLevel(itemDict, dimensionId, pos)

    # 检测玩家加入游戏
    @BaseService.Listen(Events.PlayerJoinMessageEvent)
    def onPlayerJoinMessageEvent(self, data):
        playerId = data["id"]
        defaultSlot = [info for info in BaubleSlotRegister().getBaubleSlotList() if info["isDefault"]]
        logging.debug("铂: 玩家 {} 加入游戏, 正在同步默认饰品栏信息: {}".format(playerId, defaultSlot))
        self.syncRequest(playerId, "platinum/syncBaubleDefaultSlot",
                         QRequests.Args(defaultSlot))

    # 获取玩家饰品信息
    def getPlayerBaubleInfo(self, playerId):
        self.syncRequest(playerId, "platinum/getPlayerBaubleInfo",
                         QRequests.Args().setCallBack(self.onGetPlayerBaubleInfo))

    def onGetPlayerBaubleInfo(self, data):
        data = data.data
        playerId = data["playerId"]
        baubleDict = data["baubleInfo"]
        self.broadcast(GetPlayerBaubleInfoServerEvent(playerId, baubleDict))

    # 设置饰品栏信息
    def setBaubleSlotInfo(self, playerId, baubleSlotInfo):
        isAllAvailable = True
        for slotId, baubleInfo in baubleSlotInfo.items():
            baubleSlotType = BaubleSlotRegister().getBaubleSlotTypeBySlotIdentifier(slotId)
            success = BaubleServerService.access().checkBaubleAvailable(baubleSlotType, baubleInfo["newItemName"])
            if not success:
                logging.error("铂: 饰品 {} 无法安装至槽位 {} 请检查饰品注册".format(baubleInfo["newItemName"], slotId))
                isAllAvailable = False
        if isAllAvailable:
            self.syncRequest(playerId, "platinum/setBaubleSlotInfo", QRequests.Args(baubleSlotInfo))

    # 设置特定饰品栏信息
    def setBaubleSlotInfoBySlotId(self, playerId, slotId, baubleSlotInfo):
        baubleSlotType = BaubleSlotRegister().getBaubleSlotTypeBySlotIdentifier(slotId)
        success = BaubleServerService.access().checkBaubleAvailable(baubleSlotType, baubleSlotInfo["newItemName"])
        if success:
            self.syncRequest(playerId, "platinum/setBaubleSlotInfoBySlotId", QRequests.Args(slotId, baubleSlotInfo))
        else:
            logging.error("铂: 饰品 {} 无法安装至槽位 {} 请检查饰品注册".format(baubleSlotInfo["newItemName"], slotId))

    # 减少特定饰品耐久值
    def decreaseBaubleDurability(self, playerId, slotId, decrease=1):
        self.syncRequest(playerId, "platinum/decreaseBaubleDurability", QRequests.Args(slotId, decrease))

    # 同步已注册的饰品信息
    def syncBaubleSlotInfo(self, baubleSlotInfoList):
        self.syncRequest("*", "platinum/syncBaubleSlotInfo", QRequests.Args(baubleSlotInfoList))

    # 添加某个玩家的饰品栏槽位
    def addTargetBaubleSlot(self, playerId, slotId, slotType, slotName=None, slotPlaceHolderPath=None):
        self.syncRequest(playerId, "platinum/addBaubleSlot",
                         QRequests.Args(slotId, slotType, slotName, slotPlaceHolderPath))

    # 添加全部玩家的饰品栏槽位
    def addGlobalBaubleSlot(self, slotId, slotType, slotName=None, slotPlaceHolderPath=None, isDefault=False):
        self.syncRequest("*", "platinum/addBaubleSlot",
                         QRequests.Args(slotId, slotType, slotName, slotPlaceHolderPath, isDefault))


@AllowCall
@CallBackKey("CheckBaubleAvailable")
def onCheckBaubleAvailable(baubleSlotType, baubleSlotId, baubleItem, playerId, inventoryIndex):
    baubleName = baubleItem["newItemName"]
    success = BaubleServerService.access().checkBaubleAvailable(baubleSlotType, baubleName)
    if success:
        serverUtil.DecreaseItem(playerId, 1, inventoryIndex, True)
    return {"success": success, "baubleItem": baubleItem, "baubleSlotId": baubleSlotId,
            "inventoryIndex": inventoryIndex}
