# coding=utf-8
from ..QuModLibs.Server import *
from ..commonConfig import BaubleDict
from .. import loggingUtils as logging


@AllowCall
def SwapItem(data):
    playerId = data["playerId"]
    fromSlot = data["fromSlot"]
    toSlot = data["toSlot"]

    comp = serverApi.GetEngineCompFactory().CreateItem(playerId)
    comp.SetInvItemExchange(fromSlot, toSlot)


@AllowCall
def AddItem(data):
    playerId = data["playerId"]
    itemDict = data["itemDict"]
    slot = data.get("slot", -1)
    comp = serverApi.GetEngineCompFactory().CreateItem(playerId)
    if slot != -1:
        comp.SpawnItemToPlayerInv(itemDict, playerId, slot)
    else:
        comp.SpawnItemToPlayerCarried(itemDict, playerId)


@AllowCall
def RemoveItem(data):
    playerId = data["playerId"]
    slot = data.get("slot", None)
    itemDict = {"newItemName": "minecraft:air", "newAuxValue": 0, "count": 0}

    comp = serverApi.GetEngineCompFactory().CreateItem(playerId)
    if slot is not None:
        comp.SpawnItemToPlayerInv(itemDict, playerId, slot)
    else:
        comp.SpawnItemToPlayerCarried(itemDict, playerId)


@Listen(Events.ServerItemTryUseEvent)
def OnServerItemTryUseEvent(data):
    itemUsed = data["itemDict"]
    playerId = data["playerId"]
    if itemUsed["newItemName"] in BaubleDict.keys():
        comp = serverApi.GetEngineCompFactory().CreateItem(playerId)
        itemInfo = comp.GetItemBasicInfo(itemUsed["newItemName"])
        # 不为盔甲时判断穿戴饰品
        if itemInfo["itemType"] != "armor" and itemInfo["itemType"] != "food":
            baubleSlot = ItemName2BaubleSlot(itemUsed)
            if CheckBauble(itemUsed, baubleSlot):
                Call(playerId, "EquipBauble", itemUsed, baubleSlot)


def ItemName2BaubleSlot(itemDict):
    itemName = itemDict["newItemName"]
    if itemName in BaubleDict.keys():
        return BaubleDict[itemName]["baubleSlot"][0]


@AllowCall
def CheckBauble(itemDict, baubleSlot):
    comp = serverApi.GetEngineCompFactory().CreateItem(levelId)
    baseInfo = comp.GetItemBasicInfo(itemDict["newItemName"], itemDict["newAuxValue"])
    if baseInfo["maxStackSize"] > 1:
        logging.error("铂: 饰品 {} 最大堆叠数量大于1".format(itemDict["newItemName"]))
        return False

    if itemDict["newItemName"] in BaubleDict.keys():
        baubleValue = BaubleDict[itemDict["newItemName"]]
        targetSlot = baubleValue.get("baubleSlot", [])
        if len(baubleSlot) == 0:
            logging.error("铂: 饰品 {} 配置错误, 请检查饰品注册信息".format(itemDict["newItemName"]))
            return False
        if baubleSlot in targetSlot:
            logging.info("baubleName: {} in baubleSlot: {}".format(itemDict["newItemName"], baubleSlot))
            return True

    return False


@Listen(Events.PlayerDieEvent)
def OnPlayerDieEvent(data):
    playerId = data["id"]
    pos = Entity(playerId).FootPos
    dimensionId = Entity(playerId).Dm
    comp = serverApi.GetEngineCompFactory().CreateGame(levelId)
    gameRule = comp.GetGameRulesInfoServer()
    keepInv = gameRule["cheat_info"]["keep_inventory"]
    Call(playerId, "OnPlayerDie", keepInv, pos, dimensionId)


@AllowCall
def SpawnItem(itemDict, pos, dimensionId):
    comp = serverApi.GetEngineCompFactory().CreateItem(levelId)
    comp.SpawnItemToLevel(itemDict, dimensionId, pos)


@Listen(Events.ServerChatEvent)
def OnServerChatEvent(data):
    playerId = data["playerId"]
    msg = data["message"]
    if msg.startswith("#platinum_"):
        msg = msg.replace("#platinum_", "")
        if msg in ["left_top", "right_top", "left_bottom", "right_bottom"]:
            Call(playerId, "ChangeUiPosition", msg)
            data["cancel"] = True
            comp = serverApi.GetEngineCompFactory().CreateMsg(playerId)

            position = "左上角" if msg == "left_top" else "右上角" \
                if msg == "right_top" else "左下角" if msg == "left_bottom" else "右下角"

            comp.NotifyOneMessage(playerId, "铂: 饰品栏按钮已切换至{}".format(position))


@AllowCall
def SendMsg(playerId, msg):
    comp = serverApi.GetEngineCompFactory().CreateGame(playerId)
    # comp.SetTipMessage(msg, serverApi.GenerateColor('RED'))
