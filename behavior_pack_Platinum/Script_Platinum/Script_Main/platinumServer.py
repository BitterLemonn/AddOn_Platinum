# coding=utf-8
from ..QuModLibs.Server import *
from .. import loggingUtils as logging


def DelayRun(func, delayTime=0.1, *args, **kwargs):
    comp = serverApi.GetEngineCompFactory().CreateGame(levelId)
    comp.AddTimer(delayTime, func, *args, **kwargs)


@AllowCall
def AddItem(data):
    playerId = data["playerId"]
    slot = data["slot"]
    itemDict = data["itemDict"]

    def addItem():
        comp = serverApi.GetEngineCompFactory().CreateItem(playerId)
        comp.SpawnItemToPlayerInv(itemDict, playerId, slot)

    DelayRun(addItem)
