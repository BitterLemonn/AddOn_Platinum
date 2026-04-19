# coding=utf-8
from Script_Platinum.QuModLibs.Client import *
from Script_Platinum.QuModLibs.Modules.Services.Client import BaseService
from Script_Platinum.QuModLibs.UI import ScreenNode
from Script_Platinum.client.config.playerConfig import PlayerConfig, QRequests
from Script_Platinum.client.player.playerBaubleInfo import PlayerBaubleInfoClientService
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


@Listen("UiInitFinished")
def onUiInitFinished(data):
    NativeScreenManager = clientApi.GetNativeScreenManagerCls()
    # 注册经典背包界面代理
    NativeScreenManager.instance().RegisterScreenProxy(
        "crafting.inventory_screen", "Script_Platinum.client.ui.baubleUi.BaubleUIClassicProxy"
    )
    PlayerBaubleInfoClientService.access().addBaubleInfoListener(onBaubleInfoChanged)
    # 注册口袋背包界面代理
    NativeScreenManager.instance().RegisterScreenProxy(
        "crafting_pocket.inventory_screen_pocket", "Script_Platinum.client.ui.baubleUi.BaubleUIPocketProxy"
    )


def onBaubleInfoChanged(data):
    # 监听饰品信息变化事件 刷新界面
    if screen:
        screen.screen.UpdateScreen()


class BaubleUIClassicProxy(ProxyCls):

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

        self.baubleSelectedIndex = -1
        self.baubleSelectedPath = ""

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

    def OnCreate(self):
        self.ListenEvent()
        self.setEntryPosition()

    def OnTick(self):
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
        self.inputMode = self.optionComp.GetToggleOption(minecraftEnum.OptionId.INPUT_MODE)

    def OnDestroy(self):
        UnListenForEvent("OnItemSlotButtonClickedEvent", self, self.onItemSlotButtonClickedEvent)

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

    @Binding.binding(Binding.BF_ButtonClickUp, "#bauble_reborn.bauble_button")
    def onBaubleButtonClick(self, args):
        self.isShowBaublePanel = not self.isShowBaublePanel
        playerMode = compFactory.CreateGame(levelId).GetPlayerGameType(playerId)
        if self.isShowBaublePanel and playerMode == minecraftEnum.GameType.Creative:
            self.setToolTips("§c========注意========\n暂不支持直接从创造物品栏装备饰品\n请先获取到背包当中§r")
        self.screen.UpdateScreen()

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
        return index == self.baubleSelectedIndex

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
        elif isSelectedInventory:
            self.baubleSelectedIndex = -1
            self.baubleSelectedPath = ""
            self.setToolTips("§c请先点击饰品栏\n再点击需要装备的饰品§r")

        baubleItem = self.baubleInfoManager.getBaubleInfoBySlot(self.slotManager.getPlayerSlotList()[index].identifier)
        if baubleItem is not None:
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
        inventorySelectedIndex = data.get("slotIndex", -1)
        if 0 <= inventorySelectedIndex < 36:
            itemDict = self.itemComp.GetPlayerItem(minecraftEnum.ItemPosType.INVENTORY, inventorySelectedIndex, True)
            slotList = self.slotManager.getPlayerSlotList()
            slotInfo = slotList[self.baubleSelectedIndex] if self.baubleSelectedIndex != -1 else None
            if self.baubleSelectedIndex != -1 and slotInfo:
                # 装备饰品
                if itemDict:
                    BaseService().syncRequest(
                        "server/player/baubleCheck",
                        QRequests.Args(
                            BaubleCheckRequestData(
                                baubleInfo=ItemStack.fromDict(itemDict),
                                slotType=slotInfo.slotType,
                                slotId=slotInfo.identifier,
                                index=inventorySelectedIndex,
                            ).toDict()
                        ).setCallBack(self.onCheckBaubleAvailable),
                    )
                elif self.baubleInfoManager.getBaubleInfoBySlot(slotInfo.identifier) and not itemDict:
                    # 卸下饰品
                    self.baubleInfoManager.popBaubleInfoBySlot(slotInfo.identifier, inventorySelectedIndex)
                    # 播放飞行物品动画
                    self.flyingItem(
                        self.baubleInfoManager.getBaubleInfoBySlot(slotInfo.identifier).toDict(),
                        self.getBaubleSlotPos(self.baubleSelectedPath),
                        self.getInventorySlotPos(inventorySelectedIndex),
                    )
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
        data = BaubleCheckResponseData.fromDict(data.data)
        if data.suc:
            BaseService().syncRequest(
                "server/player/changeBauble",
                QRequests.Args(ChangeBaubleRequestData(data.baubleInfo, data.slotId, data.index).toDict()),
            )
            oldBaubleItem = self.baubleInfoManager.getBaubleInfoBySlot(data.slotId)
            # 脱下旧物品
            if oldBaubleItem:
                # 播放飞行物品动画
                self.flyingItem(
                    oldBaubleItem.toDict(),
                    self.getBaubleSlotPos(self.baubleSelectedPath),
                    self.getInventorySlotPos(data.index),
                )
            # 播放飞行物品动画
            self.flyingItem(
                data.baubleInfo.toDict(),
                self.getInventorySlotPos(data.index),
                self.getBaubleSlotPos(self.baubleSelectedPath),
            )
        self.baubleSelectedIndex = -1
        self.baubleSelectedPath = ""

    def getBaubleSlotPos(self, path):
        path = path[path.find("/") + 1 :]
        slotPos = self.screen.GetGlobalPosition(path)
        return slotPos

    def getInventorySlotPos(self, index):
        index += 1
        path = (
            self.hotbarSlotPathBase.format(index=index)
            if index < 10
            else self.inventorySlotPathBase.format(index=index - 9)
        )
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

    def flyingItem(self, itemDict, startPos, endPos):
        self.flyingItemController.FlyingItem(itemDict, startPos, endPos)


class BaubleUIPocketProxy(BaubleUIClassicProxy):
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
        self.scrollPanelPath = (
            self.basePath
            + "/base_panel/hotbar_and_panels/gamepad_helper_border/both_panels/left_panel/inventory_tab_content/tab_content_search_bar_panel/scroll_pane"
        )
        self.scrollPanel = None
        self.inventorySlotPathBase = (
            self.basePath
            + "/scroll_pane/scroll_touch/scroll_view/panel/background_and_viewport/scrolling_view_port/scrolling_content/grid/grid_item_for_inventory{index}"
        )
        self.hotbarSlotPathBase = None

        self.armorBasePath = (
            self.basePath
            + "/base_panel/hotbar_and_panels/gamepad_helper_border/both_panels/right_panel/armor_tab_content/content/label_and_renderer"
        )
        self.armorRenderPath = self.armorBasePath + "/label_panel"
        self.armorRenderPath2 = self.armorBasePath + "/renderer_panel"

    def OnDestroy(self):
        super(BaubleUIPocketProxy, self).OnDestroy()

    def OnCreate(self):
        super(BaubleUIPocketProxy, self).OnCreate()
        self.scrollPanel = self.screen.GetBaseUIControl(self.scrollPanelPath).asScrollView()
        self.inventorySlotPathBase = (
            self.scrollPanel.GetScrollViewContentPath() + "/grid/grid_item_for_inventory{index}"
        )

    def OnTick(self):
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
        if not self.isLockControl:
            self.isLockControl = True
            super(BaubleUIPocketProxy, self).onItemSlotButtonClickedEvent(data)

    # 饰品栏点击
    @Binding.binding(Binding.BF_ButtonClickUp, "#bauble_reborn.slot_button")
    def onSlotButtonClick(self, args):
        if not self.isLockControl:
            self.isLockControl = True
            super(BaubleUIPocketProxy, self).onSlotButtonClick(args)

    def getIsTouchInventorySelected(self):
        for i in range(9):
            index = i + 1
            path = self.hotbarSlotPathBase.format(index=index) + "/item_selected_image"
            if self.screen.GetBaseUIControl(path).GetVisible():
                return True
        for i in range(27):
            try:
                index = i + 1
                path = self.inventorySlotPathBase.format(index=index) + "/item_selected_image"
                if self.screen.GetBaseUIControl(path).GetVisible():
                    return True
            except:
                pass
        return False

    def flyingItem(self, itemDict, startPos, endPos):
        self.flyingItemController.FlyingItem(itemDict, startPos, endPos, (24.0, 24.0))
