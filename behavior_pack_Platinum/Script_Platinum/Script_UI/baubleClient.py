# coding=utf-8
import logging

from ..QuModLibs.Client import *
from ..QuModLibs.Modules.Services.Client import BaseService, QRequests
from ..QuModLibs.QuClientApi.ui.screenNode import ScreenNode
from ..QuModLibs.UI import EasyScreenNodeCls

from .baubleDatabase import BaubleDataController, BaubleDatabase
from .baubleSlotRegister import BaubleSlotRegister
from .flyingItemRenderer import FlyingItemRenderer
from ..ItemFactory import ItemFactory
from .. import oldVersionFixer

CustomUIScreenProxy = clientApi.GetUIScreenProxyCls()
Binding = clientApi.GetViewBinderCls()
minecraftEnum = clientApi.GetMinecraftEnum()


@BaseService.Init
class BaubleBroadcastService(BaseService):

    def __init__(self):
        BaseService.__init__(self)

    def onBaublePutOn(self, baubleItem, baubleSlotId, isFirstLoad=False):
        slotIndex = BaubleSlotRegister().getSlotIndex(baubleSlotId) + 1
        baubleSlotType = BaubleSlotRegister().getBaubleSlotTypeBySlotIdentifier(baubleSlotId)
        baubleSlotType = oldVersionFixer.oldVersionFixer(baubleSlotType)
        self.localRequest("platinum/onBaublePutOn",
                          {"baubleSlotId": baubleSlotId, "baubleSlot": baubleSlotType, "slotIndex": slotIndex,
                           "itemDict": baubleItem, "isFirstLoad": isFirstLoad, "playerId": playerId})
        self.syncRequest("platinum/onBaublePutOn",
                         QRequests.Args(
                             {"baubleSlotId": baubleSlotId, "baubleSlot": baubleSlotType, "slotIndex": slotIndex,
                              "itemDict": baubleItem, "isFirstLoad": isFirstLoad, "playerId": playerId}))

    def onBaubleTakeOff(self, baubleItem, baubleSlotId, isFirstLoad=False):
        slotIndex = BaubleSlotRegister().getSlotIndex(baubleSlotId) + 1
        baubleSlotType = BaubleSlotRegister().getBaubleSlotTypeBySlotIdentifier(baubleSlotId)
        baubleSlotType = oldVersionFixer.oldVersionFixer(baubleSlotType)
        self.localRequest("platinum/onBaubleTakeOff",
                          {"baubleSlotId": baubleSlotId, "baubleSlot": baubleSlotType, "slotIndex": slotIndex,
                           "itemDict": baubleItem, "isFirstLoad": isFirstLoad, "playerId": playerId})
        self.syncRequest("platinum/onBaubleTakeOff",
                         QRequests.Args(
                             {"baubleSlotId": baubleSlotId, "baubleSlot": baubleSlotType, "slotIndex": slotIndex,
                              "itemDict": baubleItem, "isFirstLoad": isFirstLoad, "playerId": playerId}))

    # 试图装备饰品(右键穿戴)
    @BaseService.REG_API("platinum/tryEquipBauble")
    def tryEquipBauble(self, baubleItem, inventorySlotId, baubleSlotTypeList=None, baubleSlotId=None):
        if baubleSlotTypeList:
            # 查询饰品栏空位
            baubleSlotIdList = BaubleSlotRegister().getBaubleSlotIdByTypeList(baubleSlotTypeList)
            for slotId in baubleSlotIdList:
                if not BaubleDataController.getBaubleInfo(slotId):
                    baubleSlotId = slotId
                    break
            if not baubleSlotId:
                baubleSlotId = baubleSlotIdList[0]
        if baubleSlotId:
            oldBaubleInfo = BaubleDataController.popBaubleInfo(baubleSlotId)
            Call("DecreaseItem", playerId, 1, inventorySlotId, True)
            if oldBaubleInfo:
                Call("GivePlayerItem", oldBaubleInfo, playerId, inventorySlotId)
                self.onBaubleTakeOff(oldBaubleInfo, baubleSlotId)
            BaubleDataController.addBaubleInfo(baubleSlotId, baubleItem)
            self.onBaublePutOn(baubleItem, baubleSlotId)
            CallOTClient(playerId, "PlaySound", {"soundName": "armor.equip_iron", "targetId": playerId})

    @BaseService.REG_API("platinum/onPlayerDie")
    def onPlayerDie(self, pos, dimensionId):
        playerBaubleInfoList = [item for item in BaubleDataController.getAllBaubleInfo().values() if item]
        BaubleDataController.clearBaubleInfo()
        self.syncRequest("platinum/spawnItem", QRequests.Args(playerBaubleInfoList, pos, dimensionId))

    @BaseService.REG_API("platinum/getPlayerBaubleInfo")
    def getPlayerBaubleInfo(self):
        return {"playerId": playerId, "baubleInfo": BaubleDataController.getAllBaubleInfo()}

    @BaseService.REG_API("platinum/setBaubleSlotInfo")
    def setBaubleSlotInfo(self, baubleSlotInfo):
        BaubleDataController.setAllBaubleInfo(baubleSlotInfo)

    @BaseService.REG_API("platinum/setBaubleSlotInfoBySlotId")
    def setBaubleSlotInfoBySlotId(self, slotId, baubleSlotInfo):
        BaubleDataController.setBaubleInfo(slotId, baubleSlotInfo)

    @BaseService.REG_API("platinum/decreaseBaubleDurability")
    def decreaseBaubleDurability(self, slotId, decrease=1):
        baubleInfo = BaubleDataController.getBaubleInfo(slotId)
        if baubleInfo:
            baubleName = baubleInfo["newItemName"]
            baubleAux = baubleInfo["newAuxValue"]
            baseInfo = clientApi.GetEngineCompFactory().CreateItem(levelId).GetItemBasicInfo(baubleName, baubleAux)
            maxDurability = baseInfo["maxDurability"]
            if maxDurability:
                durability = (ItemFactory(baubleInfo).getDurability() or maxDurability) - decrease
                if durability <= 0:
                    BaubleDataController.popBaubleInfo(slotId)
                    # 广播卸下饰品事件
                    self.onBaubleTakeOff(baubleInfo, slotId)
                    # 播放物品破碎音效
                    CallOTClient(playerId, "PlaySound", {"soundName": "random.break", "targetId": playerId})
                else:
                    baubleInfo = ItemFactory(baubleInfo).setDurability(durability).build()
                    BaubleDataController.setBaubleInfo(slotId, baubleInfo)
            else:
                logging.error("铂: 饰品 {} 无耐久度".format(baubleName))

    @BaseService.REG_API("platinum/syncBaubleDefaultSlot")
    def syncBaubleDefaultSlot(self, defaultSlot):
        addSlotList = BaubleSlotRegister().syncDefaultSlot(defaultSlot)
        for slotId in addSlotList:
            BaubleDataController.addBaubleSlot(slotId)

    @BaseService.REG_API("platinum/addBaubleSlot")
    def addBaubleSlot(self, slotId, slotType, slotName, slotPlaceHolderPath, isDefault=False):
        if not slotName or not slotPlaceHolderPath:
            # 检查是否是继承槽位类型
            if slotType not in BaubleSlotRegister().getBaubleSlotTypeList():
                logging.error("铂: 添加槽位失败, 未注册的槽位类型, 请使用registerSlot方法注册槽位")
                return
            else:
                # 注册槽位
                if BaubleSlotRegister().addSlot(slotType, slotId):
                    # 添加玩家槽位信息
                    BaubleDataController.addBaubleSlot(slotId)
                    logging.debug("铂:玩家 {} 添加饰品栏槽位 {}".format(
                        clientApi.GetEngineCompFactory().CreateName(playerId).GetName(), slotId)
                    )

        else:
            # 注册槽位
            if BaubleSlotRegister().registerSlot(
                    {"baubleSlotName": slotName,
                     "placeholderPath": slotPlaceHolderPath,
                     "baubleSlotIdentifier": slotId,
                     "baubleSlotType": slotType,
                     "isDefault": isDefault}
            ):
                # 添加玩家槽位信息
                BaubleDataController.addBaubleSlot(slotId)
                logging.debug("铂:玩家 {} 添加饰品栏槽位 {}".format(
                    clientApi.GetEngineCompFactory().CreateName(playerId).GetName(), slotId)
                )


@BaseService.Init
class BaubleClientService(BaseService):

    def __init__(self):
        BaseService.__init__(self)
        logging.debug("饰品栏客户端服务初始化")

    @BaseService.Listen(Events.UiInitFinished)
    def onUiInitFinished(self, data):
        NativeScreenManager = clientApi.GetNativeScreenManagerCls()
        # 注册经典背包界面代理
        NativeScreenManager.instance().RegisterScreenProxy("crafting.inventory_screen",
                                                           "Script_Platinum.Script_UI.baubleClient.InventoryClassicProxy")

    @BaseService.Listen("AddPlayerCreatedClientEvent")
    def onAddPlayerCreatedClientEvent(self, data):
        targetId = data.get("playerId")
        if targetId == playerId:
            # 添加已注册默认的饰品栏信息
            baubleIdList = BaubleSlotRegister().getBaubleSlotIdentifierList(True)
            for baubleId in baubleIdList:
                BaubleDataController.addBaubleSlot(baubleId)
            # 移除未注册的饰品栏信息
            removeInfoDict = BaubleDataController.checkUnRegisterSlot()
            for baubleId, baubleInfo in (removeInfoDict or {}).items():
                logging.error("铂: 由于玩家饰品信息出现未注册的饰品栏 {}, 已取消穿戴对应栏位的饰品: {}"
                              .format(baubleId, baubleInfo["newItemName"]))
                Call("GivePlayerItem", baubleInfo, playerId)
            # 获取玩家饰品栏信息
            baubleInfoDict = BaubleDataController.getAllBaubleInfo()
            print (
                "[DEBUG]铂: 玩家: {} 饰品栏信息".format(
                    clientApi.GetEngineCompFactory().CreateName(playerId).GetName()))
            for baubleSlotId, baubleItem in baubleInfoDict.items():
                if baubleItem:
                    BaubleBroadcastService.access().onBaublePutOn(baubleItem, baubleSlotId, True)
                    print("[DEBUG]{} : {}".format(baubleSlotId, baubleItem["newItemName"] if baubleItem else None))


class InventoryClassicProxy(CustomUIScreenProxy):
    def __init__(self, screenName, screenNode):
        CustomUIScreenProxy.__init__(self, screenName, screenNode)
        self.basePath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel"
        self.survivalPaddingPath = self.basePath + "/content_stack_panel/survival_padding"
        self.hotbarSlotPathBase = self.basePath + "/content_stack_panel/player_inventory/hotbar_grid/grid_item_for_hotbar{index}"
        self.inventorySlotPathBase = self.basePath + "/content_stack_panel/player_inventory/inventory_panel_bottom_half/inventory_panel/inventory_grid/grid_item_for_inventory{index}"
        self.cursorSlotPath = self.basePath + "/inventory_selected_icon_button/default/selected_item_icon"
        self.flyingPanelPath = self.basePath + "/flying_item_renderer"
        self.toolTipsImgPath = self.basePath + "/bauble_tool_tips"

        self.screen = self.GetScreenNode()  # type: ScreenNode

        self.isShowBaublePanel = False
        self.pureBagPage = False

        self.baubleSelectedIndex = -1
        self.baubleSelectedPath = ""

        self.optionComp = clientApi.GetEngineCompFactory().CreatePlayerView(levelId)
        self.itemComp = clientApi.GetEngineCompFactory().CreateItem(levelId)
        self.inputMode = 0

        self.flyingItemController = FlyingItemRenderer(self.screen, self.flyingPanelPath)
        self.tipsLabel = ""

        self.ListenEvent()
        self.isDestroy = False

    def ListenEvent(self):
        ListenForEvent("OnItemSlotButtonClickedEvent", self, self.onItemSlotButtonClickedEvent)

    def OnTick(self):
        self.pureBagPage = self.screen.GetBaseUIControl(self.survivalPaddingPath).GetVisible()
        self.inputMode = self.optionComp.GetToggleOption(minecraftEnum.OptionId.INPUT_MODE)

    def OnDestroy(self):
        # self.flyingItemController.OnDestroy()
        UnListenForEvent("OnItemSlotButtonClickedEvent", self, self.onItemSlotButtonClickedEvent)

    @Binding.binding(Binding.BF_ButtonClickUp, "#bauble_reborn.bauble_button")
    def onBaubleButtonClick(self, args):
        self.isShowBaublePanel = not self.isShowBaublePanel

    @Binding.binding(Binding.BF_BindBool, "#bauble_reborn.vertical_grid.left_visible")
    def bindingPanelLeftVisible(self):
        return self.isShowBaublePanel

    @Binding.binding(Binding.BF_BindBool, "#bauble_reborn.vertical_grid.right_visible")
    def bindingPanelRightVisible(self):
        return self.isShowBaublePanel and not self.pureBagPage

    # 提示框信息
    @Binding.binding(Binding.BF_BindString, "#bauble_reborn.tip_text")
    def bindingTipText(self):
        return self.tipsLabel

    # 提示框显示
    @Binding.binding(Binding.BF_BindBool, "#bauble_reborn.tip_visible")
    def bindingTipTextVisible(self):
        return len(self.tipsLabel) > 0

    # 饰品栏个数
    @Binding.binding(Binding.BF_BindInt, "#bauble_reborn.vertical_grid.max_items_count")
    def bindingPanelMaxItemsCount(self):
        # logging.error("铂: 饰品栏个数 {}".format(BaubleSlotRegister().getBaubleSlotList()))
        return len(BaubleSlotRegister().getBaubleSlotList())

    # 饰品栏图标
    @Binding.binding_collection(Binding.BF_BindString, "platinum_bauble_collection", "#bauble_reborn.slot.image_holder")
    def bindingSlotImageHolder(self, index):
        return BaubleSlotRegister().getBaubleSlotList()[index]["placeholderPath"]

    # 饰品栏图标显示
    @Binding.binding_collection(Binding.BF_BindBool, "platinum_bauble_collection",
                                "#bauble_reborn.slot.image_holder.visible")
    def bindingSlotImageHolderVisible(self, index):
        baubleIdentifier = BaubleSlotRegister().getBaubleSlotList()[index]["baubleSlotIdentifier"]
        baubleInfo = BaubleDataController.getBaubleInfo(baubleIdentifier)
        if baubleInfo:
            return False
        return True

    # 饰品栏选择框
    @Binding.binding_collection(Binding.BF_BindBool, "platinum_bauble_collection", "#bauble_reborn.is_selected")
    def bindingBaubleSelected(self, index):
        return index == self.baubleSelectedIndex

    # 饰品栏物品渲染
    @Binding.binding_collection(Binding.BF_BindInt, "platinum_bauble_collection",
                                "#bauble_reborn.item_renderer.item_id_aux")
    def bindingSlotItemIdAux(self, index):
        baubleIdentifier = BaubleSlotRegister().getBaubleSlotList()[index]["baubleSlotIdentifier"]
        baubleInfo = BaubleDataController.getBaubleInfo(baubleIdentifier)
        if baubleInfo:
            itemInfo = self.itemComp.GetItemBasicInfo(baubleInfo["newItemName"], baubleInfo["newAuxValue"])
            idAux = itemInfo["id_aux"]
            return idAux if idAux else 0
        return 0

    # 饰品栏物品显示
    @Binding.binding_collection(Binding.BF_BindBool, "platinum_bauble_collection",
                                "#bauble_reborn.item_renderer.visible")
    def bindingSlotItemVisible(self, index):
        baubleIdentifier = BaubleSlotRegister().getBaubleSlotList()[index]["baubleSlotIdentifier"]
        baubleInfo = BaubleDataController.getBaubleInfo(baubleIdentifier)
        if baubleInfo:
            return True
        return False

    # 饰品栏点击
    @Binding.binding(Binding.BF_ButtonClickUp, "#bauble_reborn.slot_button")
    def onSlotButtonClick(self, args):
        index = args["#collection_index"]
        buttonPath = args["ButtonPath"]
        isSelectedInventory = False
        if self.inputMode == minecraftEnum.InputMode.Touch:
            isSelectedInventory = self.getIsTouchInventorySelected()
        else:
            cursorItem = self.screen.GetBaseUIControl(self.cursorSlotPath).asItemRenderer()
            if cursorItem.GetUiItem().get("itemName"):
                isSelectedInventory = True
        if not isSelectedInventory:
            self.baubleSelectedIndex = index if self.baubleSelectedIndex != index else -1
            self.baubleSelectedPath = buttonPath if self.baubleSelectedIndex != -1 else ""

        baubleItem = BaubleDataController.getBaubleInfo(
            BaubleSlotRegister().getBaubleSlotList()[index]["baubleSlotIdentifier"])
        if baubleItem:
            baseInfo = self.itemComp.GetItemBasicInfo(baubleItem["newItemName"], baubleItem["newAuxValue"])
            name = baseInfo["itemName"]
            itemCategory = baseInfo["itemCategory"]
            categoryName = clientApi.GetEngineCompFactory().CreateGame(levelId).GetChinese(
                "craftingScreen.tab." + itemCategory)
            if categoryName == "craftingScreen.tab." + itemCategory:
                categoryName = itemCategory
            customTips = ItemFactory(baubleItem).getCustomTips() or ""
            customTips = customTips.replace("%name%", "").replace("%category%", "").replace("%enchanting%", "").replace(
                "%attack_damage%", "")
            self.setToolTips("{name}§9{category}§r{customTips}".format(name=name, category=categoryName,
                                                                       customTips=customTips))

    # 绑定耐久度数值
    @Binding.binding_collection(Binding.BF_BindFloat, "platinum_bauble_collection",
                                "#bauble_reborn.durability_bar.clip_ratio")
    def bindingSlotClipRatio(self, index):
        baubleIdentifier = BaubleSlotRegister().getBaubleSlotList()[index]["baubleSlotIdentifier"]
        baubleInfo = BaubleDataController.getBaubleInfo(baubleIdentifier)
        if baubleInfo:
            baseInfo = self.itemComp.GetItemBasicInfo(baubleInfo["newItemName"], baubleInfo["newAuxValue"])
            if baseInfo["maxDurability"]:
                return 1 - float(baubleInfo["durability"]) / baseInfo["maxDurability"]
        return 0.0

    # 绑定耐久度显示
    @Binding.binding_collection(Binding.BF_BindBool, "platinum_bauble_collection",
                                "#bauble_reborn.durability_bar.visible")
    def bindingSlotDurabilityVisible(self, index):
        baubleIdentifier = BaubleSlotRegister().getBaubleSlotList()[index]["baubleSlotIdentifier"]
        baubleInfo = BaubleDataController.getBaubleInfo(baubleIdentifier)
        if baubleInfo:
            baseInfo = self.itemComp.GetItemBasicInfo(baubleInfo["newItemName"], baubleInfo["newAuxValue"])
            if baseInfo["maxDurability"] and baubleInfo["durability"] < baseInfo["maxDurability"]:
                return True
        return False

    # 绑定耐久度颜色
    @Binding.binding_collection(Binding.BF_BindColor, "platinum_bauble_collection",
                                "#bauble_reborn.durability_bar.color")
    def bindingSlotClipColor(self, index):
        baubleIdentifier = BaubleSlotRegister().getBaubleSlotList()[index]["baubleSlotIdentifier"]
        baubleInfo = BaubleDataController.getBaubleInfo(baubleIdentifier)
        if baubleInfo:
            baseInfo = self.itemComp.GetItemBasicInfo(baubleInfo["newItemName"], baubleInfo["newAuxValue"])
            if baseInfo["maxDurability"]:
                color = ratioToColor(float(baubleInfo["durability"]) / baseInfo["maxDurability"])
                return color
        return 0.0, 1.0, 0.0, 1.0

    # 背包点击
    def onItemSlotButtonClickedEvent(self, data):
        inventorySelectedIndex = data.get("slotIndex", -1)
        if 0 <= inventorySelectedIndex < 36:
            itemDict = self.itemComp.GetPlayerItem(minecraftEnum.ItemPosType.INVENTORY, inventorySelectedIndex, True)
            baubleSlotList = BaubleSlotRegister().getBaubleSlotList()
            baubleSlotType = baubleSlotList[self.baubleSelectedIndex]["baubleSlotType"]
            baubleSlotId = baubleSlotList[self.baubleSelectedIndex]["baubleSlotIdentifier"]
            if self.baubleSelectedIndex != -1:
                # 装备饰品
                if itemDict:
                    Request("CheckBaubleAvailable",
                            kwargs={"baubleSlotType": baubleSlotType, "baubleSlotId": baubleSlotId,
                                    "baubleItem": itemDict, "playerId": playerId,
                                    "inventoryIndex": inventorySelectedIndex},
                            onResponse=self.onCheckBaubleAvailable)
                elif BaubleDataController.getBaubleInfo(baubleSlotId) and not itemDict:
                    # 卸下饰品
                    baubleDict = BaubleDataController.popBaubleInfo(baubleSlotId)

                    Call("GivePlayerItem", baubleDict, playerId, inventorySelectedIndex)
                    # 播放飞行物品动画
                    self.flyingItemController.FlyingItem(baubleDict, self.getBaubleSlotPos(self.baubleSelectedPath),
                                                         self.getInventorySlotPos(inventorySelectedIndex))
                    # 广播卸下饰品事件
                    BaubleBroadcastService.access().onBaubleTakeOff(baubleDict, baubleSlotId)
                    self.baubleSelectedIndex = -1
                    self.baubleSelectedPath = ""
                else:
                    self.baubleSelectedIndex = -1
                    self.baubleSelectedPath = ""
        elif self.baubleSelectedIndex != -1:
            self.baubleSelectedIndex = -1
            self.baubleSelectedPath = ""

    # 检查饰品是否可用回调
    def onCheckBaubleAvailable(self, data):
        success = data.get("success", False)
        baubleItem = data.get("baubleItem")
        baubleSlotId = data.get("baubleSlotId")
        inventoryIndex = data.get("inventoryIndex")
        if success:
            oldBaubleItem = BaubleDataController.popBaubleInfo(baubleSlotId) \
                if baubleSlotId in BaubleDataController.getAllBaubleInfo().keys() else None
            # 脱下旧物品
            if oldBaubleItem:
                Call("GivePlayerItem", oldBaubleItem, playerId, inventoryIndex)
                # 播放飞行物品动画
                self.flyingItemController.FlyingItem(oldBaubleItem, self.getBaubleSlotPos(self.baubleSelectedPath),
                                                     self.getInventorySlotPos(inventoryIndex))
                BaubleBroadcastService.access().onBaubleTakeOff(oldBaubleItem, baubleSlotId)
            # 装备新物品
            BaubleDataController.addBaubleInfo(baubleSlotId, baubleItem)
            BaubleBroadcastService.access().onBaublePutOn(baubleItem, baubleSlotId)
            # 播放飞行物品动画
            self.flyingItemController.FlyingItem(baubleItem, self.getInventorySlotPos(inventoryIndex),
                                                 self.getBaubleSlotPos(self.baubleSelectedPath))
        self.baubleSelectedIndex = -1
        self.baubleSelectedPath = ""

    def getBaubleSlotPos(self, path):
        path = path[path.find("/") + 1:]
        slotPos = self.screen.GetGlobalPosition(path)
        return slotPos

    def getInventorySlotPos(self, index):
        index += 1
        path = self.hotbarSlotPathBase.format(index=index) if index < 10 else \
            self.inventorySlotPathBase.format(index=index - 9)
        slotPos = self.screen.GetGlobalPosition(path)
        return slotPos

    def getIsTouchInventorySelected(self):
        for i in range(9):
            index = i + 1
            path = self.hotbarSlotPathBase.format(index=index) + "/item_selected_image"
            if self.screen.GetBaseUIControl(path).GetVisible():
                return True
        for i in range(27):
            index = i + 1
            path = self.inventorySlotPathBase.format(index=index) + "/item_selected_image"
            if self.screen.GetBaseUIControl(path).GetVisible():
                return True
        return False

    def setToolTips(self, tips):
        img = self.screen.GetBaseUIControl(self.toolTipsImgPath)
        text = self.screen.GetBaseUIControl(self.toolTipsImgPath + "/item_text_label").asLabel()
        self.tipsLabel = tips
        self.screen.UpdateScreen()
        if len(tips) > 0:
            img.StopAnimation()
            img.PlayAnimation()
            text.StopAnimation()
            text.PlayAnimation()


def ratioToColor(ratio):
    return 1 - ratio, ratio, 0.0, 1.0
