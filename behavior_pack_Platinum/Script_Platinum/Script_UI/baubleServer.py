# coding=utf-8
from ..QuModLibs.Server import *
from ..commonConfig import BaubleDict


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
    slot = data["slot"]
    itemDict = data["itemDict"]

    comp = serverApi.GetEngineCompFactory().CreateItem(playerId)
    comp.SpawnItemToPlayerInv(itemDict, playerId, slot)


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
        if itemInfo["itemType"] != "armor":
            baubleSlot = ItemName2BaubleSlot(itemUsed)
            Call(playerId, "EquipBauble", itemUsed, baubleSlot)


def ItemName2BaubleSlot(itemDict):
    itemName = itemDict["newItemName"]
    if BaubleDict.get(itemName, None):
        return BaubleDict[itemName] if isinstance(BaubleDict[itemName], type("")) else BaubleDict[itemName][0]


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
