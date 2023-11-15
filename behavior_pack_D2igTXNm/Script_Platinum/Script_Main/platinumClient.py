# coding=utf-8
from ..commonConfig import BaubleDict
from .. import loggingUtils as logging
from ..QuModLibs.Client import *


def OnInventoryItemChanged(data):
    newItemDict = data["newItemDict"]
    if BaubleDict.get(newItemDict["newItemName"], None) is not None:
        baubleValue = BaubleDict[newItemDict["newItemName"]]
        try:
            baubleInfo = baubleValue if isinstance(baubleValue, type("")) else baubleValue[0] if len(
                baubleValue) == 1 else baubleValue[0] + baubleValue[1]
            baubleSlot = baubleInfo.split("\n")[0]
            item = newItemDict["newItemName"]
            if baubleSlot not in newItemDict["customTips"]:
                itemI18nName = clientApi.GetEngineCompFactory(). \
                    CreateItem(levelId).GetItemBasicInfo(item)["itemName"]
                baubleInfo = itemI18nName + "\n" + baubleInfo
                newItemDict["customTips"] += baubleInfo
                Call("AddItem", {"slot": data["slot"], "itemDict": newItemDict, "playerId": data["playerId"]})
            else:
                return
        except:
            logging.error(
                "铂: 饰品 {} 描述格式错误, 请检查Script_Platinum/commonConfig.py".format(newItemDict["newItemName"]))


ListenForEvent("InventoryItemChangedClientEvent", None, OnInventoryItemChanged)
