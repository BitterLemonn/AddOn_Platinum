# coding=utf-8
from .. import loggingUtils as logging
from ..QuModLibs.Client import *


def OnInventoryItemChanged(data):
    Call("OnItemChanged", data["playerId"], data["newItemDict"], data["slot"])


ListenForEvent("InventoryItemChangedClientEvent", None, OnInventoryItemChanged)
