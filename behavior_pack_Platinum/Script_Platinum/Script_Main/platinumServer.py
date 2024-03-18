# coding=utf-8
from ..QuModLibs.Server import *
from .. import loggingUtils as logging
from ..commonConfig import BaubleDict


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


@AllowCall
def OnItemChanged(playerId, itemDict, slot):
    if BaubleDict.get(itemDict["newItemName"], None) is not None:
        baubleValue = BaubleDict[itemDict["newItemName"]]
        try:
            baubleSlot = ""
            baubleInfo = ""
            if len(baubleValue) > 1 and isinstance(baubleValue[0], tuple):
                for index, baubleSlotInfo in enumerate(baubleValue[0]):
                    if baubleSlot == "":
                        baubleSlot += baubleSlotInfo
                        baubleSlot = baubleSlot.replace("§r\n", "、")
                    elif index != len(baubleValue[0]) - 1:
                        tmpInfo = baubleSlotInfo.split(" ")[1]
                        tmpInfo.replace("§r\n", "、")
                        baubleSlot += tmpInfo
                    else:
                        tmpInfo = baubleSlotInfo.split(" ")[1].replace("\n", "")
                        baubleSlot += tmpInfo

                baubleInfo = baubleSlot + ("\n" + baubleValue[1]) if len(baubleValue) > 1 else ""
            if baubleSlot == "":
                baubleInfo = baubleValue if isinstance(baubleValue, type("")) else baubleValue[0] if len(
                    baubleValue) == 1 else baubleValue[0] + baubleValue[1]
                baubleSlot = baubleInfo.split("\n")[0]
            item = itemDict["newItemName"]
            if baubleSlot not in itemDict["customTips"]:
                itemI18nName = serverApi.GetEngineCompFactory(). \
                    CreateItem(levelId).GetItemBasicInfo(item)["itemName"]
                baubleInfo = itemI18nName + "\n" + baubleInfo
                itemDict["customTips"] += baubleInfo
                AddItem({"slot": slot, "itemDict": itemDict, "playerId": playerId})
            else:
                return
        except:
            logging.error(
                "铂: 饰品 {} 描述格式错误, 请检查Script_Platinum/commonConfig.py".format(itemDict["newItemName"]))
