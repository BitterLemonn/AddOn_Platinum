# coding=utf-8
from ..BroadcastEvent.getBaubleSlotInfoEvent import GetGlobalBaubleSlotInfoEvent, GetTargetBaubleSlotInfoEvent
from ..DataManager.baubleInfoManager import BaubleInfoManager
from ..DataManager.baubleSlotManager import BaubleSlotManager
from ..BroadcastEvent.getPlayerBaubleInfoEvent import GetPlayerBaubleInfoServerEvent
from ..DataManager.baubleSlotServerService import BaubleSlotServerService
from ..QuModLibs.Modules.Services.Globals import QRequests
from ..QuModLibs.Server import *
from ..QuModLibs.Modules.Services.Server import BaseService
from .. import serverUtil
from .. import developLogging as logging


@BaseService.Init
class BaubleServerService(BaseService):
    def __init__(self):
        BaseService.__init__(self)
        self.itemComp = serverApi.GetEngineCompFactory().CreateItem(levelId)
        self.itemComp.GetUserDataInEvent("ServerItemTryUseEvent")

    # 检查饰品是否可用安装至指定槽位
    @staticmethod
    def checkBaubleAvailable(baubleSlotType, baubleName):
        baubleInfoDict = BaubleInfoManager.getBaubleInfoDict()
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
            comp = serverApi.GetEngineCompFactory().CreateMsg(playerId)
            data["cancel"] = True
            msg = msg.replace("#platinum_", "")
            if msg in ["left_top", "right_top", "left_bottom", "right_bottom"]:
                self.syncRequest(playerId, "platinum/changeUiPosition", QRequests.Args(msg))

                position = "左上角" if msg == "left_top" else "右上角" \
                    if msg == "right_top" else "左下角" if msg == "left_bottom" else "右下角"

                comp.NotifyOneMessage(playerId, "铂: 饰品栏按钮已切换至{}".format(position))
            elif msg in ["get_gs"]:
                self.getGlobalBaubleSlotInfo()
            elif msg in ["get_ts"]:
                self.getTargetBaubleSlotInfo(playerId)
            else:
                comp.NotifyOneMessage(playerId, "§c铂: 未知指令§r")

    # 右键穿戴饰品
    @BaseService.Listen(Events.ServerItemTryUseEvent)
    def onServerItemTryUseEvent(self, data):
        itemUsed = data["itemDict"]
        playerId = data["playerId"]
        itemInfo = self.itemComp.GetItemBasicInfo(itemUsed["newItemName"])
        if itemInfo["itemType"] != "armor" and itemInfo["itemType"] != "food":
            baubleRegDict = BaubleInfoManager.getBaubleInfoDict()
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

    # 玩家客户端通知指令添加槽位
    @BaseService.REG_API("platinum/addBaubleSlotCommand")
    def addBaubleSlotCommand(self, slotId, slotType, isDefault):
        if slotId not in BaubleSlotServerService.access().getBaubleSlotIdentifierList():
            BaubleSlotServerService.access().addSlot(slotType, slotId, isDefault=isDefault)

    # 检测玩家加入游戏
    @BaseService.Listen(Events.PlayerJoinMessageEvent)
    def onPlayerJoinMessageEvent(self, data):
        playerId = data["id"]
        logging.debug("铂: 玩家 {} 加入游戏 开始同步默认槽位".format(
            serverApi.GetEngineCompFactory().CreateName(playerId).GetName()))
        BaubleSlotServerService.access().syncToClient(playerId)

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
            baubleSlotType = BaubleSlotServerService.access().getBaubleSlotTypeBySlotIdentifier(slotId)
            success = BaubleServerService.access().checkBaubleAvailable(baubleSlotType, baubleInfo["newItemName"])
            if not success:
                logging.error("铂: 饰品 {} 无法安装至槽位 {} 请检查饰品注册".format(baubleInfo["newItemName"], slotId))
                isAllAvailable = False
        if isAllAvailable:
            self.syncRequest(playerId, "platinum/setBaubleSlotInfo", QRequests.Args(baubleSlotInfo))

    # 设置特定饰品栏信息
    def setBaubleSlotInfoBySlotId(self, playerId, slotId, baubleSlotInfo):
        baubleSlotType = BaubleSlotServerService.access().getBaubleSlotTypeBySlotIdentifier(slotId)
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
    def addTargetBaubleSlot(self, playerId, slotId, slotType, slotName=None, slotPlaceHolderPath=None,
                            isCommandModify=False):
        if self.addBaubleSlot(slotId, slotType, slotName, slotPlaceHolderPath):
            self.syncRequest(playerId, "platinum/addBaubleSlot",
                             QRequests.Args(slotId, slotType, slotName, slotPlaceHolderPath, False, isCommandModify))

    # 添加全部玩家的饰品栏槽位
    def addGlobalBaubleSlot(self, slotId, slotType, slotName=None, slotPlaceHolderPath=None, isDefault=False,
                            isCommandModify=False):
        if self.addBaubleSlot(slotId, slotType, slotName, slotPlaceHolderPath, isDefault):
            self.syncRequest("*", "platinum/addBaubleSlot",
                             QRequests.Args(slotId, slotType, slotName, slotPlaceHolderPath, isDefault,
                                            isCommandModify))

    # 添加槽位到服务端注册列表
    @staticmethod
    def addBaubleSlot(slotId, slotType, slotName, placeholderPath, isDefault=False):
        if slotId in BaubleSlotServerService.access().getBaubleSlotIdentifierList():
            return True

        if not slotName or not placeholderPath:
            # 检查是否是继承槽位类型
            if slotType not in BaubleSlotServerService.access().getBaubleSlotTypeList():
                logging.error("铂: 添加槽位失败, 未注册的槽位类型, 请使用registerSlot方法注册槽位")
                return False
            else:
                # 注册槽位
                if BaubleSlotServerService.access().addSlot(slotType, slotId):
                    return True

        else:
            # 注册槽位
            if BaubleSlotServerService.access().registerSlot(
                    {"baubleSlotName": slotName,
                     "placeholderPath": placeholderPath,
                     "baubleSlotIdentifier": slotId,
                     "baubleSlotType": slotType,
                     "isDefault": isDefault}
            ):
                return True
        return False

    # 删除某个玩家的饰品栏槽位
    def removeTargetBaubleSlot(self, playerId, slotId, isCommandModify=False):
        self.syncRequest(playerId, "platinum/removeBaubleSlot", QRequests.Args(slotId, isCommandModify))

    # 删除全部玩家的饰品栏槽位
    def removeGlobalBaubleSlot(self, slotId, isCommandModify=False):
        self.syncRequest("*", "platinum/removeBaubleSlot", QRequests.Args(slotId, isCommandModify))

    # 获取已注册槽位信息
    def getGlobalBaubleSlotInfo(self):
        baubleSlotList = BaubleSlotServerService.access().getBaubleSlotList()
        # 移除placeholderPath key
        for slot in baubleSlotList:
            slot.pop("placeholderPath")
        self.broadcast(GetGlobalBaubleSlotInfoEvent(baubleSlotList))

    # 获取玩家拥有的饰品槽位信息
    def getTargetBaubleSlotInfo(self, playerId):
        self.syncRequest(playerId, "platinum/getBaubleSlotInfo", QRequests.Args().setCallBack(self.onGetBaubleSlotInfo))

    def onGetBaubleSlotInfo(self, data):
        data = data.data
        playerId = data["playerId"]
        baubleSlotList = data["baubleSlotList"]
        # 移除placeholderPath key
        for slot in baubleSlotList:
            slot.pop("placeholderPath")
        self.broadcast(GetTargetBaubleSlotInfoEvent(playerId, baubleSlotList))


@AllowCall
@CallBackKey("CheckBaubleAvailable")
def onCheckBaubleAvailable(baubleSlotType, baubleSlotId, baubleItem, playerId, inventoryIndex):
    baubleName = baubleItem["newItemName"]
    success = BaubleServerService.access().checkBaubleAvailable(baubleSlotType, baubleName)
    if success:
        serverUtil.DecreaseItem(playerId, 1, inventoryIndex, True)
    return {"success": success, "baubleItem": baubleItem, "baubleSlotId": baubleSlotId,
            "inventoryIndex": inventoryIndex}
