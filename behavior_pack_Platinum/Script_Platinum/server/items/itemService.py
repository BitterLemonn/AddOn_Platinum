# coding=utf-8
from Script_Platinum.QuModLibs.Server import *
from Script_Platinum.QuModLibs.Modules.Services.Server import BaseService
from Script_Platinum.server.registry.baubleRegistry import BaubleRegistry
from Script_Platinum.server.registry.slotRegistry import SlotRegistry
from Script_Platinum.utils import serverUtils
from Script_Platinum.utils.ItemFactory import ItemFactory
from Script_Platinum.utils.serverUtils import compFactory
from Script_Platinum.utils import developLogging as logging


@BaseService.Init
class ItemService(BaseService):

    def __init__(self):
        BaseService.__init__(self)
        self.baubleRegistry = BaubleRegistry()
        self.slotRegistry = SlotRegistry()

    @BaseService.Listen("InventoryItemChangedServerEvent")
    def onInventoryItemChangedServer(self, data):
        playerId = data.get("playerId")
        itemDict = data.get("newItemDict")
        slot = data.get("slot")
        itemName = itemDict.get("newItemName")

        if self.baubleRegistry.getBaubleInfo(itemName):
            baubleInfo = self.baubleRegistry.getBaubleInfo(itemName)
            try:
                customTips = ItemFactory(itemDict).getCustomTips()
                baubleTips = baubleInfo.get("customTips")
                if "§6栏位: §g" in (customTips or ""):
                    return
                else:
                    baubleSlotTypeList = baubleInfo.get("slot")
                    slotNames = [self.slotRegistry.getSlotTypeNameByType(st) for st in baubleSlotTypeList]
                    tips = "§6栏位: §g" + "、".join(slotNames) + "§r\n"
                    customTips = (
                        "%name%%category%%enchanting%\n" + tips + (baubleTips if baubleTips else "") + "%attack_damage%"
                    )
                    itemDict = ItemFactory(itemDict).setCustomTips(customTips).build()
                    compFactory.CreateGame(levelId).AddTimer(
                        0.0, lambda: serverUtils.givePlayerItem(itemDict, playerId, slot)
                    )

            except Exception as e:
                logging.error(
                    "铂: 饰品 {} 描述格式错误, 请检查Script_Platinum/commonConfig.py {}".format(
                        itemDict.get("newItemName"), e
                    )
                )