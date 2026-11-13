# coding=utf-8
from Script_Platinum.QuModLibs.Server import *
from Script_Platinum.QuModLibs.Modules.Services.Server import BaseService
from Script_Platinum.data.requestData import ItemStack
from Script_Platinum.server.player.playerBaubleSlot import getPlayerSlotList
from Script_Platinum.server.registry.baubleRegistry import BaubleRegistry
from Script_Platinum.server.registry.slotRegistry import SlotRegistry
from Script_Platinum.utils import serverUtils
from Script_Platinum.utils.ItemFactory import ItemFactory
from Script_Platinum.utils.serverUtils import compFactory, minecraftEnum
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

    @BaseService.Listen("ServerItemTryUseEvent")
    def onServerItemTryUseEvent(self, data):
        usedItem = ItemStack.fromDict(data["itemDict"])
        bauble = self.baubleRegistry.getBaubleInfo(usedItem.name)
        if bauble is None or usedItem.count != 1:
            return

        playerId = data["playerId"]
        itemComp = compFactory.CreateItem(playerId)
        if not itemComp:
            return
        itemInfo = itemComp.GetItemBasicInfo(usedItem.name)
        if not itemInfo or itemInfo["itemType"] in ("armor", "food"):
            return
        index = itemComp.GetSelectSlotId()
        if index < 0:
            return

        # 使用事件可能缺少 userData，延迟穿戴时用快捷栏的完整快照做校验。
        heldItem = ItemStack.fromDict(itemComp.GetPlayerItem(minecraftEnum.ItemPosType.INVENTORY, index, True))
        if heldItem.count != 1 or not heldItem.isSameItem(usedItem, isIgnoreUserData=True):
            return

        from Script_Platinum.server.player.playerBaubleInfo import (
            getPlayerBaubleInfo,
            PlayerBaubleInfoServerService,
        )

        slotId = getPlayerBaubleInfo(playerId).getEmptyOrFirstSlotByList(
            bauble.get("slot", []), getPlayerSlotList(playerId)
        )
        if slotId is None:
            return
        compFactory.CreateGame(levelId).AddTimer(
            0.0, lambda: PlayerBaubleInfoServerService.access()._changeBable(playerId, slotId, heldItem, index)
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
