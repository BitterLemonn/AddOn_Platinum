# coding=utf-8
from Script_Platinum.QuModLibs.Server import *
from Script_Platinum.QuModLibs.Modules.Services.Server import BaseService
from Script_Platinum.data.requestData import ItemStack
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
                    baubleSlotTypeList = [st for st in baubleInfo["slot"]]
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
                import traceback

                traceback.print_exc()
                logging.error(
                    "铂: 饰品 {} 描述格式错误, 请检查Script_Platinum/commonConfig.py {}".format(
                        itemDict.get("newItemName"), e
                    )
                )

        # 右键穿戴饰品

    @BaseService.Listen("ServerItemTryUseEvent")
    def onServerItemTryUseEvent(self, data):
        itemStack = ItemStack.fromDict(data["itemDict"]) 
        playerId = data["playerId"]
        itemComp = compFactory.CreateItem(playerId)
        itemInfo = itemComp.GetItemBasicInfo(itemStack.name)
        if itemInfo["itemType"] != "armor" and itemInfo["itemType"] != "food":
            if self.baubleRegistry.getBaubleInfo(itemStack.name) is not None:
                baubleSlotTypeList = self.baubleRegistry.getBaubleInfo(itemStack.name).get("slot", [])
                index = itemComp.GetSelectSlotId()

                from Script_Platinum.server.player.playerBaubleInfo import (
                    getPlayerBaubleInfo,
                    PlayerBaubleInfoServerService,
                )

                emptySlotId = getPlayerBaubleInfo(playerId).getEmptyOrFirstSlotByList(baubleSlotTypeList)
                if emptySlotId is None:
                    return
                compFactory.CreateGame(levelId).AddTimer(
                    0.0,
                    lambda: PlayerBaubleInfoServerService.access()._changeBable(
                        playerId, emptySlotId, itemStack, index
                    ),
                )

    # 死亡掉落物品
    @BaseService.Listen("PlayerDieEvent")
    def onPlayerDieEvent(self, data):
        playerId = data["id"]
        pos = Entity(playerId).FootPos
        dimensionId = Entity(playerId).Dm
        comp = serverApi.GetEngineCompFactory().CreateGame(levelId)
        gameRule = comp.GetGameRulesInfoServer()
        keepInv = gameRule["cheat_info"]["keep_inventory"]
        if not keepInv:
            logging.info("铂: 玩家 {} 死亡掉落物品".format(compFactory.CreateName(playerId).GetName()))
            # self.syncRequest(playerId, "platinum/onPlayerDie", QRequests.Args(pos, dimensionId))
