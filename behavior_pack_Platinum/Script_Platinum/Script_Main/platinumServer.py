# coding=utf-8
from ..QuModLibs.Server import *
from .. import loggingUtils as logging
from ..commonConfig import BaubleDict


def DelayRun(func, delayTime=0.0, *args, **kwargs):
    comp = serverApi.GetEngineCompFactory().CreateGame(levelId)
    comp.AddTimer(delayTime, func, *args, **kwargs)


@AllowCall
def AddItem(data):
    playerId = data["playerId"]
    slot = data.get("slot", -1)
    itemDict = data["itemDict"]

    if slot == -1:
        comp = serverApi.GetEngineCompFactory().CreateItem(playerId)
        slot = comp.GetSelectSlotId()

    def addItem():
        comp = serverApi.GetEngineCompFactory().CreateItem(playerId)
        comp.SpawnItemToPlayerInv(itemDict, playerId, slot)

    DelayRun(addItem)


@AllowCall
def OnItemChanged(playerId, itemDict, slot):
    if BaubleDict.get(itemDict["newItemName"], None) is not None:
        baubleValue = BaubleDict[itemDict["newItemName"]]
        try:
            baubleSlot = baubleValue.get("baubleSlot", [])
            customTips = baubleValue.get("customTips", None)

            # 转化栏位描述
            baubleSlotStr = ""
            for index, slotStr in enumerate(baubleSlot):
                if len(baubleValue) > 1 and index != len(baubleSlot) - 1:
                    slotStr = slotStr.replace("§r\n", "、")
                if index != 0:
                    slotStr = slotStr.replace("§6栏位: §g", "")
                baubleSlotStr += slotStr

            if baubleSlotStr == "" or baubleSlotStr in itemDict["customTips"]:
                return

                # 获取物品名称
            itemName = itemDict["newItemName"]
            itemI18nName = serverApi.GetEngineCompFactory(). \
                CreateItem(levelId).GetItemBasicInfo(itemName)["itemName"]
            baubleSlotStr = itemI18nName + "\n" + baubleSlotStr
            if customTips is not None:
                baubleSlotStr += customTips
            logging.warn("铂: 饰品 {} 描述: {}".format(itemName, baubleSlotStr))
            itemDict["customTips"] = baubleSlotStr
            AddItem({"slot": slot, "itemDict": itemDict, "playerId": playerId})
        except:
            logging.error(
                "铂: 饰品 {} 描述格式错误, 请检查Script_Platinum/commonConfig.py".format(itemDict["newItemName"]))


@AllowCall
def NeedSendInfo(playerId):
    comp = serverApi.GetEngineCompFactory().CreateMsg(playerId)
    comp.NotifyOneMessage(playerId,
                          "铂: 如遇到饰品无法安装请先尝试铂自带的旅行者腰带, 如可以正常安装反馈问题请到无法安装的饰品模组处反馈, 请勿在铂模组处反馈, 谢谢!",
                          "§6")
