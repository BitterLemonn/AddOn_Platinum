from .. import loggingUtils as logging
from ..QuModLibs.Server import *


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
    slot = data["slot"]
    itemDict = {"newItemName": "minecraft:air", "newAuxValue": 0, "count": 0}

    comp = serverApi.GetEngineCompFactory().CreateItem(playerId)
    comp.SpawnItemToPlayerInv(itemDict, playerId, slot)
