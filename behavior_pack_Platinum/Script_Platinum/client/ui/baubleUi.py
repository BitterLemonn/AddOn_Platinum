# coding=utf-8
from Script_Platinum.QuModLibs.UI import ScreenNode
from Script_Platinum.QuModLibs.Client import *
from Script_Platinum.QuModLibs.Modules.Services.Client import BaseService
from Script_Platinum.client.config.playerConfig import PlayerConfig, PlayerConfigService, QRequests
from Script_Platinum.client.player.playerBaubleInfo import PlayerBaubleInfoClientService
from Script_Platinum.client.ui.baubleContainerUi import openBaubleContainer
from Script_Platinum.client.ui.flyingItemRenderer import FlyingItemRenderer
from Script_Platinum.client.player.playerBaubleSlot import PlayerBaubleSlotClientService
from Script_Platinum.data.requestData import BaubleCheckRequestData, ChangeBaubleRequestData
from Script_Platinum.data.responseData import BaubleCheckResponseData, ItemStack
from Script_Platinum.utils.ItemFactory import ItemFactory
from Script_Platinum.utils.commonUtils import ratioToColor
from Script_Platinum.utils.clientUtils import compFactory

ProxyCls = clientApi.GetUIScreenProxyCls()
Binding = clientApi.GetViewBinderCls()
minecraftEnum = clientApi.GetMinecraftEnum()
screen = None  # type: BaubleUIClassicProxy|None


@AllowCall
def ChangeUiPosition(position):
    PlayerConfigService.access().setUiPosition(position)


@Listen("UiInitFinished")
def onUiInitFinished(data):
    NativeScreenManager = clientApi.GetNativeScreenManagerCls()
    # 注册经典背包界面代理
    NativeScreenManager.instance().RegisterScreenProxy(
        "crafting.inventory_screen", "Script_Platinum.client.ui.baubleUi.BaubleUIClassicProxy"
    )
    # 注册口袋背包界面代理
    NativeScreenManager.instance().RegisterScreenProxy(
        "crafting_pocket.inventory_screen_pocket", "Script_Platinum.client.ui.baubleUi.BaubleUIPocketProxy"
    )
    PlayerBaubleInfoClientService.access().addBaubleInfoListener(onBaubleInfoChanged)


def onBaubleInfoChanged(data):
    # 监听饰品信息变化事件 刷新界面
    if screen:
        screen.screen.UpdateScreen()


class BaubleUIClassicProxy(ProxyCls):

    inventoryScreenName = "inventory_screen"
    flyingItemScale = 1.0

    def __init__(self, screenName, screenNode):
        ProxyCls.__init__(self, screenName, screenNode)
        self.basePath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel"
        self.playerInvPath = self.basePath + "/content_stack_panel/player_inventory"
        self.entryBtnPath = self.playerInvPath + "/inventory_panel_top_half/player_armor_panel/player_bg/bauble_button"
        self.recipeBtnTogglePath = (
            self.basePath
            + "/content_stack_panel/toolbar_anchor/toolbar_panel/toolbar_background/toolbar_stack_panel/recipe_book_layout_toggle_panel_creative/recipe_book_layout_toggle"
        )
        self.hotbarSlotPathBase = self.playerInvPath + "/hotbar_grid/grid_item_for_hotbar{index}"
        self.inventorySlotPathBase = (
            self.playerInvPath
            + "/inventory_panel_bottom_half/inventory_panel/inventory_grid/grid_item_for_inventory{index}"
        )
        self.creativeBagScrollPath = (
            self.basePath
            + "/content_stack_panel/recipe_book/tab_content_panel/tab_content_search_bar_panel/scroll_pane"
        )
        self.cursorSlotPath = self.basePath + "/inventory_selected_icon_button/default/selected_item_icon"
        self.flyingPanelPath = self.basePath + "/flying_item_renderer"
        self.toolTipsImgPath = self.basePath + "/bauble_tool_tips"

        self.screen = self.GetScreenNode()  # type: ScreenNode

        self.isShowBaublePanel = False
        self.recipeBagPage = False
        self.entryPosition = PlayerConfig.uiPosition
        self.showBaubleSidebarButton = PlayerConfig.showBaubleSidebarButton
        self.showBaubleContainerButton = PlayerConfig.showBaubleContainerButton
        self.useNewBaubleOperation = PlayerConfig.useNewBaubleOperation

        self.baubleSelection = None
        self.touchItemPress = None
        self.pendingTouchSlotClicks = []
        self.cursorSlotPress = None
        self.pendingCursorSwap = None

        self.optionComp = compFactory.CreatePlayerView(levelId)
        self.itemComp = compFactory.CreateItem(levelId)
        self.gameComp = compFactory.CreateGame(levelId)
        self.inputMode = 0
        self.gameMode = ""

        self.flyingItemController = FlyingItemRenderer(self.screen, self.flyingPanelPath)
        self.slotManager = PlayerBaubleSlotClientService.access()
        self.baubleInfoManager = PlayerBaubleInfoClientService.access()
        self.tipsLabel = ""

    def ListenEvent(self):
        ListenForEvent("OnItemSlotButtonClickedEvent", self, self.onItemSlotButtonClickedEvent)
        ListenForEvent("PlayerTryDropItemClientEvent", self, self.onTryDropItem)

    def OnCreate(self):
        self._syncInputMode()
        self.ListenEvent()
        self.setEntryPosition()

    def OnTick(self):
        self.syncPlayerConfig()
        gameMode = self.gameComp.GetPlayerGameType(playerId)
        if gameMode != self.gameMode:
            self.gameMode = gameMode
            self.recipeBtnTogglePath = (
                self.basePath
                + "/content_stack_panel/toolbar_anchor/toolbar_panel/toolbar_background/toolbar_stack_panel/recipe_book_layout_toggle_panel_{}/recipe_book_layout_toggle".format(
                    "creative" if gameMode == minecraftEnum.GameType.Creative else "survival"
                )
            )
        recipeBagPage = self.screen.GetBaseUIControl(self.recipeBtnTogglePath).asSwitchToggle().GetToggleState()
        if recipeBagPage != self.recipeBagPage:
            self.recipeBagPage = recipeBagPage
            self.screen.UpdateScreen()
        self._updateSlotInput()

    def _updateSlotInput(self):
        self._syncInputMode()
        self._flushTouchSlotClicks()

        if self.pendingCursorSwap is not None:
            request = self.pendingCursorSwap
            self.pendingCursorSwap = None
            self.cursorSlotPress = None
            if self._isMouseSidebar():
                BaseService().syncRequest("server/player/swapCursorBauble", QRequests.Args(*request))
        elif self.cursorSlotPress is not None and not self._isMouseSidebar():
            self.cursorSlotPress = None

    def OnDestroy(self):
        UnListenForEvent("OnItemSlotButtonClickedEvent", self, self.onItemSlotButtonClickedEvent)
        UnListenForEvent("PlayerTryDropItemClientEvent", self, self.onTryDropItem)
        self.isShowBaublePanel = False
        self._clearSlotInteraction()

    def _clearSlotInteraction(self):
        self.baubleSelection = None
        self.touchItemPress = None
        del self.pendingTouchSlotClicks[:]
        self.cursorSlotPress = None
        self.pendingCursorSwap = None

    def _syncInputMode(self):
        inputMode = self.optionComp.GetToggleOption(minecraftEnum.OptionId.INPUT_MODE)
        if self.inputMode != inputMode:
            self._setBaubleSelection(None)
            self.inputMode = inputMode
        if self.inputMode != minecraftEnum.InputMode.Touch:
            self.touchItemPress = None
            del self.pendingTouchSlotClicks[:]

    def _flushTouchSlotClicks(self):
        if not self.pendingTouchSlotClicks:
            return
        clicks = self.pendingTouchSlotClicks
        self.pendingTouchSlotClicks = []
        if not self._isTouchSidebar():
            return
        for slotInfo, selection, buttonPath in clicks:
            if selection is None:
                continue
            inventoryIndex, item, creativePos = selection
            if inventoryIndex is None:
                self._requestEquipFromCreative(slotInfo.identifier, item, creativePos, buttonPath)
            else:
                self._requestEquipFromInventory(slotInfo, inventoryIndex, item, buttonPath)

    def setEntryPosition(self):
        btn = self.screen.GetBaseUIControl(self.entryBtnPath)
        if self.entryPosition == "left_top":
            btn.SetFullPosition(axis="x", paramDict={"followType": "parent", "relativeValue": -0.35})
            btn.SetFullPosition(axis="y", paramDict={"followType": "parent", "relativeValue": -0.4})
        elif self.entryPosition == "right_top":
            btn.SetFullPosition(axis="x", paramDict={"followType": "parent", "relativeValue": 0.35})
            btn.SetFullPosition(axis="y", paramDict={"followType": "parent", "relativeValue": -0.4})
        elif self.entryPosition == "left_bottom":
            btn.SetFullPosition(axis="x", paramDict={"followType": "parent", "relativeValue": -0.35})
            btn.SetFullPosition(axis="y", paramDict={"followType": "parent", "relativeValue": 0.4})
        elif self.entryPosition == "right_bottom":
            btn.SetFullPosition(axis="x", paramDict={"followType": "parent", "relativeValue": 0.35})
            btn.SetFullPosition(axis="y", paramDict={"followType": "parent", "relativeValue": 0.4})

    def syncPlayerConfig(self):
        needUpdate = False
        if self.entryPosition != PlayerConfig.uiPosition:
            self.entryPosition = PlayerConfig.uiPosition
            self.setEntryPosition()
            needUpdate = True
        if self.showBaubleSidebarButton != PlayerConfig.showBaubleSidebarButton:
            self.showBaubleSidebarButton = PlayerConfig.showBaubleSidebarButton
            needUpdate = True
        if self.showBaubleContainerButton != PlayerConfig.showBaubleContainerButton:
            self.showBaubleContainerButton = PlayerConfig.showBaubleContainerButton
            needUpdate = True
        if self.useNewBaubleOperation != PlayerConfig.useNewBaubleOperation:
            self.useNewBaubleOperation = PlayerConfig.useNewBaubleOperation
            self._clearSlotInteraction()
            self.tipsLabel = ""
            needUpdate = True
        if needUpdate:
            self.screen.UpdateScreen()

    @Binding.binding(Binding.BF_ButtonClickUp, "#bauble_reborn.bauble_button")
    def onBaubleButtonClick(self, args):
        self.isShowBaublePanel = not self.isShowBaublePanel
        if not self.isShowBaublePanel:
            self._clearSlotInteraction()
        self.screen.UpdateScreen()

    @Binding.binding(Binding.BF_ButtonClickUp, "#bauble_reborn.bauble_layout_toggle")
    def onBaubleLayoutToggleClick(self, args):
        openBaubleContainer(minecraftEnum.InventoryType.EQUIPMENT)

    @Binding.binding(Binding.BF_BindBool, "#bauble_reborn.bauble_button.visible")
    def bindingBaubleButtonVisible(self):
        return PlayerConfig.showBaubleSidebarButton

    @Binding.binding(Binding.BF_BindBool, "#bauble_reborn.new_operation.visible")
    def bindingNewOperationVisible(self):
        return self.useNewBaubleOperation

    @Binding.binding(Binding.BF_BindBool, "#bauble_reborn.legacy_operation.visible")
    def bindingLegacyOperationVisible(self):
        return not self.useNewBaubleOperation

    @Binding.binding(Binding.BF_BindBool, "#bauble_reborn.container_button.visible")
    def bindingBaubleContainerButtonVisible(self):
        return PlayerConfig.showBaubleContainerButton

    @Binding.binding(Binding.BF_BindBool, "#bauble_reborn.vertical_grid.left_visible")
    def bindingPanelLeftVisible(self):
        return self.isShowBaublePanel and not self.recipeBagPage

    @Binding.binding(Binding.BF_BindBool, "#bauble_reborn.vertical_grid.right_visible")
    def bindingPanelRightVisible(self):
        return self.isShowBaublePanel and self.recipeBagPage

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
        return len(self.slotManager.getPlayerSlotList())

    # 饰品栏图标
    @Binding.binding_collection(Binding.BF_BindString, "platinum_bauble_collection", "#bauble_reborn.slot.image_holder")
    def bindingSlotImageHolder(self, index):
        slotList = self.slotManager.getPlayerSlotList()
        if index < len(slotList):
            return slotList[index].placeholderPath
        return ""

    # 饰品栏图标显示
    @Binding.binding_collection(
        Binding.BF_BindBool, "platinum_bauble_collection", "#bauble_reborn.slot.image_holder.visible"
    )
    def bindingSlotImageHolderVisible(self, index):
        slotList = self.slotManager.getPlayerSlotList()
        if index < len(slotList):
            slot = slotList[index]
            baubleInfo = self.baubleInfoManager.getBaubleInfoBySlot(slot.identifier)
            if baubleInfo is not None:
                return False
        return True

    # 饰品栏选择框
    @Binding.binding_collection(Binding.BF_BindBool, "platinum_bauble_collection", "#bauble_reborn.is_selected")
    def bindingBaubleSelected(self, index):
        if self.baubleSelection is None:
            return False
        slotList = self.slotManager.getPlayerSlotList()
        slotId = self.baubleSelection[0]
        if not 0 <= index < len(slotList) or slotList[index].identifier != slotId:
            return False
        if self.useNewBaubleOperation and self.inputMode == minecraftEnum.InputMode.Touch:
            item = self.baubleInfoManager.getBaubleInfoBySlot(slotId)
            return item is not None and not item.isEmpty()
        return True

    def _setBaubleSelection(self, selection):
        if self.baubleSelection != selection:
            self.baubleSelection = selection
            if self.inputMode == minecraftEnum.InputMode.Touch:
                self.screen.UpdateScreen(False)

    # 饰品栏物品渲染
    @Binding.binding_collection(
        Binding.BF_BindInt, "platinum_bauble_collection", "#bauble_reborn.item_renderer.item_id_aux"
    )
    def bindingSlotItemIdAux(self, index):
        slotList = self.slotManager.getPlayerSlotList()
        if index < len(slotList):
            slot = slotList[index]
            baubleInfo = self.baubleInfoManager.getBaubleInfoBySlot(slot.identifier)
            if baubleInfo is not None:
                itemInfo = self.itemComp.GetItemBasicInfo(baubleInfo.name, baubleInfo.aux)
                idAux = itemInfo["id_aux"]
                return idAux if idAux else 0
        return 0

    # 饰品栏物品显示
    @Binding.binding_collection(
        Binding.BF_BindBool, "platinum_bauble_collection", "#bauble_reborn.item_renderer.visible"
    )
    def bindingSlotItemVisible(self, index):
        slotList = self.slotManager.getPlayerSlotList()
        if index < len(slotList):
            slot = slotList[index]
            baubleInfo = self.baubleInfoManager.getBaubleInfoBySlot(slot.identifier)
            if baubleInfo is not None:
                return True
        return False

    def _isMouseSidebar(self):
        return (
            self.useNewBaubleOperation
            and self.isShowBaublePanel
            and self.optionComp.GetToggleOption(minecraftEnum.OptionId.INPUT_MODE) == minecraftEnum.InputMode.Mouse
            and clientApi.GetTopUI() == self.inventoryScreenName
        )

    def _isTouchSidebar(self):
        return (
            self.useNewBaubleOperation
            and self.isShowBaublePanel
            and self.inputMode == minecraftEnum.InputMode.Touch
            and clientApi.GetTopUI() == self.inventoryScreenName
        )

    def _getRenderedItem(self, path):
        control = self.screen.GetBaseUIControl(path)
        renderer = control.asItemRenderer() if control else None
        if not renderer:
            return None
        item = renderer.GetUiItem() or {}
        itemName = item.get("itemName")
        if itemName and itemName != "minecraft:air":
            return ItemStack(itemName, 1, item.get("auxValue", 0))
        return None

    @Binding.binding(Binding.BF_ButtonClickDown, "#bauble_reborn.slot_button")
    def onSlotButtonDown(self, args):
        self._syncInputMode()
        self.touchItemPress = None
        if self._isTouchSidebar():
            # 原版丢弃动作会清除选中态，先记录装备来源。
            self.touchItemPress = (args["ButtonPath"], self._getTouchItemSelection())
        cursorItem = self._getRenderedItem(self.cursorSlotPath) if self._isMouseSidebar() else None
        self.cursorSlotPress = (args["ButtonPath"], cursorItem) if cursorItem is not None else None

    @Binding.binding(Binding.BF_ButtonClickCancel, "#bauble_reborn.slot_button")
    def onSlotButtonCancel(self, _):
        self.touchItemPress = None
        self.cursorSlotPress = None

    def onTryDropItem(self, data):
        if data.get("playerId") != playerId:
            return
        if self._isTouchSidebar():
            if self.touchItemPress is not None or self.pendingTouchSlotClicks:
                data["cancel"] = True
            return
        if self.cursorSlotPress is None or not self._isMouseSidebar():
            return
        _, cursorItem = self.cursorSlotPress
        itemDict = data.get("itemDict") or {}
        dropItem = ItemStack(
            itemDict.get("newItemName") or itemDict.get("itemName", ""),
            aux=itemDict.get("newAuxValue", itemDict.get("auxValue", 0)),
        )
        if cursorItem.isSameItem(dropItem, isIgnoreUserData=True):
            data["cancel"] = True

    # 饰品栏点击
    @Binding.binding(Binding.BF_ButtonClickUp, "#bauble_reborn.slot_button")
    def onSlotButtonClick(self, args):
        cursorPress = self.cursorSlotPress
        self.cursorSlotPress = None
        touchPress = self.touchItemPress
        self.touchItemPress = None
        slotList = self.slotManager.getPlayerSlotList()
        index = args.get("#collection_index", -1)
        if not self.isShowBaublePanel or not 0 <= index < len(slotList):
            return
        slotInfo = slotList[index]
        slotId = slotInfo.identifier
        baubleItem = self.baubleInfoManager.getBaubleInfoBySlot(slotId)
        hasBauble = baubleItem is not None and not baubleItem.isEmpty()
        buttonPath = args["ButtonPath"]
        isMouseSidebar = self._isMouseSidebar()
        cursorItem = None
        if isMouseSidebar or self.inputMode != minecraftEnum.InputMode.Touch:
            cursorItem = self._getRenderedItem(self.cursorSlotPath)
        if isMouseSidebar:
            self._setBaubleSelection(None)
            if cursorItem is None and cursorPress is not None and cursorPress[0] == buttonPath:
                cursorItem = cursorPress[1]
            if cursorItem is not None:
                self.cursorSlotPress = (buttonPath, cursorItem)
                # 等这次点击的原版丢弃回调处理完，再提交交换请求。
                self.pendingCursorSwap = (slotId, cursorItem.name, cursorItem.aux)
            elif hasBauble:
                self.pendingCursorSwap = (slotId,)
            return

        hasSelectedItem = cursorItem is not None
        if self.useNewBaubleOperation and self.inputMode == minecraftEnum.InputMode.Touch:
            selection = touchPress[1] if touchPress and touchPress[0] == buttonPath else self._getTouchItemSelection()
            # 保留这次点按的丢弃拦截，下一帧再提交装备请求。
            self.pendingTouchSlotClicks.append((slotInfo, selection, buttonPath))
            if selection is not None:
                self._setBaubleSelection(None)
                return
            if not hasBauble:
                self._setBaubleSelection(None)
                return
        elif self.inputMode == minecraftEnum.InputMode.Touch:
            hasSelectedItem = self._getTouchItemSelection() is not None

        if not hasSelectedItem:
            if self.baubleSelection is not None and self.baubleSelection[0] == slotId:
                self._setBaubleSelection(None)
            else:
                self._setBaubleSelection((slotId, buttonPath))
        else:
            self._setBaubleSelection(None)
            self.setToolTips("§c请先点击饰品栏\n再点击需要装备的饰品§r")

        if baubleItem is not None:
            self._showBaubleToolTips(baubleItem)

    def _showBaubleToolTips(self, baubleItem):
        baseInfo = self.itemComp.GetItemBasicInfo(baubleItem.name, baubleItem.aux)
        name = baseInfo["itemName"]
        itemCategory = baseInfo["itemCategory"]
        categoryName = compFactory.CreateGame(levelId).GetChinese("craftingScreen.tab." + itemCategory)
        if categoryName == "craftingScreen.tab." + itemCategory:
            categoryName = itemCategory
        customTips = ItemFactory(baubleItem.toDict()).getCustomTips() or ""
        customTips = (
            customTips.replace("%name%", "")
            .replace("%category%", "")
            .replace("%enchanting%", "")
            .replace("%attack_damage%", "")
        )
        self.setToolTips(
            "{name}\n§9{category}§r{customTips}".format(name=name, category=categoryName, customTips=customTips)
        )

    # 绑定耐久度数值
    @Binding.binding_collection(
        Binding.BF_BindFloat, "platinum_bauble_collection", "#bauble_reborn.durability_bar.clip_ratio"
    )
    def bindingSlotClipRatio(self, index):
        slotList = self.slotManager.getPlayerSlotList()
        if index < len(slotList):
            slot = slotList[index]
            baubleInfo = self.baubleInfoManager.getBaubleInfoBySlot(slot.identifier)
            if baubleInfo is not None:
                baseInfo = self.itemComp.GetItemBasicInfo(baubleInfo.name, baubleInfo.aux)
                if baseInfo and baseInfo["maxDurability"]:
                    return 1 - float(baubleInfo.durability) / baseInfo["maxDurability"]
        return 0.0

    # 绑定耐久度显示
    @Binding.binding_collection(
        Binding.BF_BindBool, "platinum_bauble_collection", "#bauble_reborn.durability_bar.visible"
    )
    def bindingSlotDurabilityVisible(self, index):
        slotList = self.slotManager.getPlayerSlotList()
        if index < len(slotList):
            slot = slotList[index]
            baubleInfo = self.baubleInfoManager.getBaubleInfoBySlot(slot.identifier)
            if baubleInfo is not None:
                baseInfo = self.itemComp.GetItemBasicInfo(baubleInfo.name, baubleInfo.aux)
                if baseInfo and baseInfo["maxDurability"] and baubleInfo.durability < baseInfo["maxDurability"]:
                    return True
        return False

    # 绑定耐久度颜色
    @Binding.binding_collection(
        Binding.BF_BindColor, "platinum_bauble_collection", "#bauble_reborn.durability_bar.color"
    )
    def bindingSlotClipColor(self, index):
        slotList = self.slotManager.getPlayerSlotList()
        if index < len(slotList):
            slot = slotList[index]
            baubleInfo = self.baubleInfoManager.getBaubleInfoBySlot(slot.identifier)
            if baubleInfo is not None:
                baseInfo = self.itemComp.GetItemBasicInfo(baubleInfo.name, baubleInfo.aux)
                if baseInfo and baseInfo["maxDurability"]:
                    color = ratioToColor(float(baubleInfo.durability) / baseInfo["maxDurability"])
                    return color
        return 0.0, 1.0, 0.0, 1.0

    # 背包点击
    def onItemSlotButtonClickedEvent(self, data):
        if not self.isShowBaublePanel or self.baubleSelection is None:
            return
        slotId, buttonPath = self.baubleSelection
        self._setBaubleSelection(None)
        if self._isMouseSidebar():
            return
        inventoryIndex = data.get("slotIndex", -1)
        if not 0 <= inventoryIndex < 36:
            return
        slotInfo = next((slot for slot in self.slotManager.getPlayerSlotList() if slot.identifier == slotId), None)
        if slotInfo is None:
            return

        baubleItem = self.baubleInfoManager.getBaubleInfoBySlot(slotId)
        hasBauble = baubleItem is not None and not baubleItem.isEmpty()
        if self.useNewBaubleOperation and self.inputMode == minecraftEnum.InputMode.Touch and not hasBauble:
            return

        item = self._getInventoryItem(inventoryIndex)
        if item is not None:
            self._requestEquipFromInventory(slotInfo, inventoryIndex, item, buttonPath)
            return

        if not hasBauble:
            return
        self.baubleInfoManager.popBaubleInfoBySlot(slotId, inventoryIndex)
        fromPos = self.getBaubleSlotPos(buttonPath)
        toPos = self.getInventorySlotPos(inventoryIndex)
        if fromPos is not None and toPos is not None:
            self.flyingItemParam(
                [FlyingItemRenderer.FlyingItemParam(baubleItem.toDict(), fromPos, toPos, self.flyingItemScale)]
            )

    def _requestEquipFromInventory(self, slotInfo, inventoryIndex, item, buttonPath):
        request = BaubleCheckRequestData(item, slotInfo.identifier, slotInfo.slotType, inventoryIndex)
        BaseService().syncRequest(
            "server/player/baubleCheck",
            QRequests.Args(request.toDict()).setCallBack(lambda data: self.onCheckBaubleAvailable(data, buttonPath)),
        )

    def onCheckBaubleAvailable(self, result, buttonPath):
        if not result.data:
            return
        data = BaubleCheckResponseData.fromDict(result.data)
        if not data.suc:
            return
        BaseService().syncRequest(
            "server/player/changeBauble",
            QRequests.Args(ChangeBaubleRequestData(data.baubleInfo, data.slotId, data.index).toDict()),
        )
        if not self.isShowBaublePanel:
            return
        baublePos = self.getBaubleSlotPos(buttonPath)
        inventoryPos = self.getInventorySlotPos(data.index)
        if baublePos is None or inventoryPos is None:
            return
        scale = self.flyingItemScale
        itemParamList = []
        oldBaubleItem = self.baubleInfoManager.getBaubleInfoBySlot(data.slotId)
        if oldBaubleItem is not None and not oldBaubleItem.isEmpty():
            itemParamList.append(FlyingItemRenderer.FlyingItemParam(oldBaubleItem.toDict(), baublePos, inventoryPos, scale))
        itemParamList.append(FlyingItemRenderer.FlyingItemParam(data.baubleInfo.toDict(), inventoryPos, baublePos, scale))
        self.flyingItemParam(itemParamList)

    def _requestEquipFromCreative(self, slotId, item, fromPos, buttonPath):
        BaseService().syncRequest(
            "server/player/equipCreativeBauble",
            QRequests.Args(slotId, item.name, item.aux).setCallBack(
                lambda result: self._onCreativeBaubleEquipped(result, fromPos, buttonPath)
            ),
        )

    def _onCreativeBaubleEquipped(self, result, fromPos, buttonPath):
        if not result.data or not self.isShowBaublePanel or fromPos is None:
            return
        toPos = self.getBaubleSlotPos(buttonPath)
        if toPos is not None:
            self.flyingItemParam([FlyingItemRenderer.FlyingItemParam(result.data, fromPos, toPos, self.flyingItemScale)])

    def getBaubleSlotPos(self, path):
        path = path[path.find("/") + 1 :]
        return self._getFlyingItemPosition(path)

    def _getInventorySlotPathBase(self):
        return self.inventorySlotPathBase

    def getInventorySlotPos(self, index):
        if index < 9:
            path = self.hotbarSlotPathBase.format(index=index + 1)
        else:
            pathBase = self._getInventorySlotPathBase()
            if not pathBase:
                return None
            path = pathBase.format(index=index - 8)
        return self._getFlyingItemPosition(path)

    def _getFlyingItemPosition(self, path):
        control = self.screen.GetBaseUIControl(path)
        if not control:
            return None
        width, height = control.GetSize()
        if width <= 0 or height <= 0:
            return None
        x, y = control.GetGlobalPosition()
        # 原版飞行渲染器接收 16px 物品图标缩放后的左上角。
        iconSize = 16.0 * self.flyingItemScale
        return x + (width - iconSize) * 0.5, y + (height - iconSize) * 0.5

    def _getInventoryItem(self, index):
        item = ItemStack.fromDict(self.itemComp.GetPlayerItem(minecraftEnum.ItemPosType.INVENTORY, index, True))
        return None if item.isEmpty() or item.name == "minecraft:air" else item

    def _getTouchItemSelection(self):
        slotGroups = ((0, 9, self.hotbarSlotPathBase), (9, 36, self._getInventorySlotPathBase()))
        for start, stop, pathBase in slotGroups:
            if not pathBase:
                continue
            for index in range(start, stop):
                path = pathBase.format(index=index - start + 1) + "/item_selected_image"
                control = self.screen.GetBaseUIControl(path)
                if not control or not control.GetVisible():
                    continue
                item = self._getInventoryItem(index)
                if item is not None:
                    return index, item, None
        if self.gameComp.GetPlayerGameType(playerId) == minecraftEnum.GameType.Creative:
            return self._getTouchCreativeSelection()
        return None

    def _getTouchCreativeSelection(self):
        control = self.screen.GetBaseUIControl(self.creativeBagScrollPath)
        if not control or not control.GetVisible() or control.GetSize()[1] <= 0:
            return None
        scrollPanel = control.asScrollView()
        contentPath = scrollPanel.GetScrollViewContentPath() if scrollPanel else None
        if not contentPath:
            return None
        gridPath = contentPath + "/grid"
        for slotName in self.screen.GetChildrenName(gridPath) or ():
            slotPath = gridPath + "/" + slotName
            selected = self.screen.GetBaseUIControl(slotPath + "/item_selected_image")
            if not selected or not selected.GetVisible():
                continue
            item = self._getRenderedItem(slotPath + "/item_cell/item/common.item_renderer")
            if item is not None:
                return None, item, self._getFlyingItemPosition(slotPath)
        return None

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

    def flyingItemParam(self, itemParamList):  # type: (list[FlyingItemRenderer.FlyingItemParam]) -> None
        self.flyingItemController.flyingItem(itemParamList)


class BaubleUIPocketProxy(BaubleUIClassicProxy):
    inventoryScreenName = "inventory_screen_pocket"
    flyingItemScale = 1.5
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(BaubleUIPocketProxy, cls).__new__(cls)
        return cls.__instance

    def __init__(self, screenName, screenNode):
        BaubleUIClassicProxy.__init__(self, screenName, screenNode)
        self.isLockControl = False
        self.lockTime = 0

        self.basePath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel"
        self.cursorSlotPath = self.basePath + "/base_panel/inventory_selected_icon_button/default/selected_item_icon"
        self.entryBtnPath = (
            self.basePath
            + "/base_panel/hotbar_and_panels/gamepad_helper_border/both_panels/right_panel/armor_tab_content/content/equipment_and_renderer/armor_panel/armor_and_player/player_preview_border/player_bg/bauble_button"
        )
        leftPanelPath = (
            self.basePath
            + "/base_panel/hotbar_and_panels/gamepad_helper_border/both_panels/left_panel"
        )
        self.scrollPanelPath = leftPanelPath + "/inventory_tab_content/tab_content_search_bar_panel/scroll_pane"
        self.creativeBagScrollPath = leftPanelPath + "/recipe_book_tab_content/tab_content_search_bar_panel/scroll_pane"
        self.hotbarSlotPathBase = (
            self.basePath
            + "/base_panel/hotbar_and_panels/hotbar_section_panel/hotbar/hotbar_grid/hotbar_grid_item{index}"
        )

        self.armorBasePath = (
            self.basePath
            + "/base_panel/hotbar_and_panels/gamepad_helper_border/both_panels/right_panel/armor_tab_content/content/label_and_renderer"
        )
        self.armorRenderPath = self.armorBasePath + "/label_panel"
        self.armorRenderPath2 = self.armorBasePath + "/renderer_panel"

    def OnDestroy(self):
        super(BaubleUIPocketProxy, self).OnDestroy()

    def _getInventorySlotPathBase(self):
        control = self.screen.GetBaseUIControl(self.scrollPanelPath)
        scrollPanel = control.asScrollView() if control else None
        contentPath = scrollPanel.GetScrollViewContentPath() if scrollPanel else None
        return contentPath + "/grid/grid_item_for_inventory{index}" if contentPath else None

    def OnTick(self):
        self.syncPlayerConfig()
        self._updateSlotInput()
        # 锁定控制
        if self.isLockControl:
            self.lockTime += 1
            if self.lockTime > 3 * 2:
                self.isLockControl = False
                self.lockTime = 0

    @Binding.binding(Binding.BF_ButtonClickUp, "#bauble_reborn.bauble_button")
    def onBaubleButtonClick(self, args):
        if not self.isLockControl:
            self.isLockControl = True
            super(BaubleUIPocketProxy, self).onBaubleButtonClick(args)
        if self.isShowBaublePanel:
            basePanel = self.screen.GetBaseUIControl(self.armorBasePath)
            x, y = basePanel.GetSize()
            if y < 40:
                self.setToolTips("§c检测到背包界面过小，请到\n§6设置-视频-GUI标度§r\n§c中缩小GUI标度§r")

    @Binding.binding(Binding.BF_BindBool, "#bauble_reborn.pocket_grid.visible")
    def bindingPocketGridVisible(self):
        self.screen.GetBaseUIControl(self.armorRenderPath).SetVisible(not self.isShowBaublePanel)
        self.screen.GetBaseUIControl(self.armorRenderPath2).SetVisible(not self.isShowBaublePanel)
        return self.isShowBaublePanel

    # 背包点击
    def onItemSlotButtonClickedEvent(self, data):
        if self.inputMode not in (minecraftEnum.InputMode.Mouse, minecraftEnum.InputMode.Touch):
            if self.isLockControl:
                return
            self.isLockControl = True
        super(BaubleUIPocketProxy, self).onItemSlotButtonClickedEvent(data)

    # 饰品栏点击
    @Binding.binding(Binding.BF_ButtonClickUp, "#bauble_reborn.slot_button")
    def onSlotButtonClick(self, args):
        if self.inputMode not in (minecraftEnum.InputMode.Mouse, minecraftEnum.InputMode.Touch):
            if self.isLockControl:
                return
            self.isLockControl = True
        super(BaubleUIPocketProxy, self).onSlotButtonClick(args)
