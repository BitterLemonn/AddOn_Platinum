# coding=utf-8
from Script_Platinum.QuModLibs.Server import *

minecraftEnum = serverApi.GetMinecraftEnum()
cooldownList = {}


@AllowCall
def givePlayerItem(itemDict, playerId, slot=-1):
    comp = compFactory.CreateItem(playerId)
    if slot == -1:
        if not comp.SpawnItemToPlayerInv(itemDict, playerId):
            player = Entity(playerId)
            comp.SpawnItemToLevel(itemDict, player.Dm, player.FootPos)
    else:
        comp.SpawnItemToPlayerInv(itemDict, playerId, slot)


def getPlayerMode(playerId):
    comp = compFactory.CreateGame(levelId)
    return comp.GetPlayerGameType(playerId)


@AllowCall
def decreaseItem(playerId, count, slot=-1, isForce=False):
    if getPlayerMode(playerId) != minecraftEnum.GameType.Creative or isForce:
        comp = compFactory.CreateItem(playerId)
        if slot == -1:
            slot = comp.GetSelectSlotId()

        item = comp.GetPlayerItem(minecraftEnum.ItemPosType.INVENTORY, slot, True)
        restCount = item["count"] - count if item["count"] - count > 0 else 0
        comp.SetInvItemNum(slot, restCount)


def decreaseDurability(playerId, dur, slot=-1):
    if getPlayerMode(playerId) != minecraftEnum.GameType.Creative:
        comp = compFactory.CreateItem(playerId)
        if slot == -1:
            slot = comp.GetSelectSlotId()

        item = comp.GetPlayerItem(minecraftEnum.ItemPosType.INVENTORY, slot, True)
        restDur = item["durability"] - dur if item["durability"] - dur > 0 else 0
        if restDur <= 0:
            comp.SetInvItemNum(slot, item["count"] - 1)
        comp.SetItemDurability(minecraftEnum.ItemPosType.INVENTORY, slot, restDur)


def createParticle(particleName, pos):
    Call("*", "PlayParticle", {"particleName": particleName, "pos": pos})


def setCooldown(playerId, coolDownTime=10):
    if playerId in cooldownList:
        return False
    else:
        cooldownList[playerId] = coolDownTime
        return True


@Listen(Events.OnScriptTickServer)
def onScriptTickUseCoolDown():
    global cooldownList
    for key, cooldownTime in cooldownList.items():
        if cooldownTime == 0:
            del cooldownList[key]
        else:
            cooldownList[key] = cooldownTime - 1


def getDistance(entityId1, entityId2):
    pos1 = Entity(entityId1).FootPos
    pos2 = Entity(entityId2).FootPos
    return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2 + (pos1[2] - pos2[2]) ** 2) ** 0.5
