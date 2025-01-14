# coding=utf-8
import logging

from ..ItemFactory import ItemFactory
from ..QuModLibs.Modules.Services.Globals import BaseTimer
from ..QuModLibs.Server import *
from ..QuModLibs.Modules.Services.Server import BaseService
from ..Script_UI.baubleInfoRegister import BaubleInfoRegister
from ..Script_UI.baubleSlotRegister import BaubleSlotRegister
from ..commonConfig import BaubleDict
from .. import serverUtil


@AllowCall
def NeedSendInfo(playerId):
    comp = serverApi.GetEngineCompFactory().CreateMsg(playerId)
    comp.NotifyOneMessage(playerId,
                          "铂: 如遇到饰品无法安装请先尝试铂自带的旅行者腰带, 如可以正常安装反馈问题请到无法安装的饰品模组处反馈, 请勿在铂模组处反馈, 谢谢!",
                          "§6")


@BaseService.Init
class PlatinumServerService(BaseService):
    def __init__(self):
        BaseService.__init__(self)
        comp = serverApi.GetEngineCompFactory().CreateItem(levelId)
        comp.GetUserDataInEvent("InventoryItemChangedServerEvent")

    @BaseService.Listen("InventoryItemChangedServerEvent")
    def OnInventoryItemChangedServerEvent(self, data):
        playerId = data.get("playerId")
        itemDict = data.get("newItemDict")
        slot = data.get("slot")
        itemName = itemDict.get("newItemName")
        if itemName and itemName in BaubleInfoRegister.getBaubleInfoDict().keys():
            baubleInfo = BaubleInfoRegister.getBaubleInfoDict().get(itemName)
            try:
                customTips = ItemFactory(itemDict).getCustomTips()
                baubleTips = baubleInfo.get("customTips")
                if "§6栏位: §g" in (customTips or ""):
                    return
                else:
                    baubleSlotTypeList = baubleInfo.get("baubleSlot")
                    tips = "§6栏位: §g"
                    for slotType in baubleSlotTypeList:
                        isLast = baubleSlotTypeList.index(slotType) == len(baubleSlotTypeList) - 1
                        slotName = BaubleSlotRegister().getSlotTypeNameDict().get(slotType)
                        tips += slotName + ("、" if not isLast else "") + ("§r\n" if isLast else "")
                    customTips = "%name%%category%%enchanting%\n" + tips + \
                                 (baubleTips if baubleTips else "") + "%attack_damage%"
                    itemDict = ItemFactory(itemDict).setCustomTips(customTips).build()
                    self.addTimer(BaseTimer(
                        callObject=serverUtil.GivePlayerItem,
                        kwargsDict={
                            "playerId": playerId,
                            "itemDict": itemDict,
                            "slot": slot
                        },
                        time=0.0
                    ))

            except Exception as e:
                logging.error("铂: 饰品 {} 描述格式错误, 请检查Script_Platinum/commonConfig.py {}".format(
                    itemDict.get("newItemName"), e)
                )
