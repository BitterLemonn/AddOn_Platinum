# coding=utf-8
import logging
from ..QuModLibs.Client import *


def OnInventoryItemChanged(data):
    Call("OnItemChanged", data["playerId"], data["newItemDict"], data["slot"])


ListenForEvent("InventoryItemChangedClientEvent", None, OnInventoryItemChanged)


@Listen(Events.OnLocalPlayerStopLoading)
def OnLocalPlayerStopLoading(data):
    comp = clientApi.GetEngineCompFactory().CreateGame(playerId)

    def NeedSendInfo():
        Call("NeedSendInfo", playerId)

    comp.AddTimer(3.0, NeedSendInfo)
