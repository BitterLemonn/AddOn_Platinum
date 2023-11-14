# coding=utf-8
from .. import loggingUtils as logging
from ..QuModLibs.Client import *
from ..QuModLibs.UI import *
import re

import mod.client.extraClientApi as clientApi
import mod.client.ui.screenNode as ScreenNode

CustomUIScreenProxy = clientApi.GetUIScreenProxyCls()


class CommonConfig(object):
    UI_DEF = "bauble_base_panel"
    UI_DEF_MAIN = "bauble_base_panel.main"
    UI_DEF_BAUBLE_BTN = "bauble_base_panel.bauble_button"

    FLY_ANIMATION_DURATION = 5


class BaublePath(object):
    swallowInputPanel = "/swallow_input_panel"
    bgImgPath = swallowInputPanel + "/bg_img"
    baseStackPanelPath = bgImgPath + "/base_stack_panel"
    # bauble
    baublePanelPath = baseStackPanelPath + "/bauble_panel"
    baubleContentPCPath = baublePanelPath + "/bauble_scroll/scroll_mouse/scroll_view/stack_panel/background_and_viewport/scrolling_view_port/scrolling_content"
    baubleContentMobilePath = baublePanelPath + "/bauble_scroll/scroll_touch/scroll_view/panel/background_and_viewport/scrolling_view_port/scrolling_content"
    # right
    rightStackPanelPath = baseStackPanelPath + "/right_stack_panel"
    # tool
    toolStackPanelPath = rightStackPanelPath + "/tool_stack_panel"
    playerPaperDollPath = toolStackPanelPath + "/player_panel/paper_doll_bg/player_paper_doll"
    toolPanel = toolStackPanelPath + "/tool_right_stack_panel/tool_panel"
    closeBtnPath = toolPanel + "/close_btn"
    # inventory
    inventoryStackPanelPath = rightStackPanelPath + "/inventory_stack_panel"
    inventoryGridPath = inventoryStackPanelPath + "/inventory_grid"
    hotbarGridPath = inventoryStackPanelPath + "/hotbar_grid"

    # base
    slotBtnBasePath = "/slot_btn"
    itemRenderBasePath = "/item_renderer"
    itemSelectedBasePath = "/item_selected_img"
    durabilityBgBasePath = itemRenderBasePath + "/durability_base_img"
    durabilityBasePath = itemRenderBasePath + "/durability_img"
    itemCountBasePath = itemRenderBasePath + "/item_count"

    # bauble slot panel
    baubleSlotPanelList = {
        "/bauble_helmet_panel": "/bauble_helmet_btn",
        "/bauble_necklace_panel": "/bauble_necklace_btn",
        "/bauble_back_panel": "/bauble_back_btn",
        "/bauble_armor_panel": "/bauble_armor_btn",
        "/bauble_hand_panel_1": "/bauble_hand_btn",
        "/bauble_hand_panel_2": "/bauble_hand_btn",
        "/bauble_belt_panel": "/bauble_belt_btn",
        "/bauble_shoes_panel": "/bauble_shoes_btn",
        "/bauble_other_panel_1": "/bauble_other_btn",
        "/bauble_other_panel_2": "/bauble_other_btn",
        "/bauble_other_panel_3": "/bauble_other_btn",
        "/bauble_other_panel_4": "/bauble_other_btn"
    }


class GlobalData(object):
    try:
        uiNode = ScreenNode.ScreenNode()
    except Exception as e:
        uiNode = None

    bagInfo = {}
    baubleInfo = {}
    slotToPath = {}

    slotSelect = -1
    baubleSlotSelect = -1


# 代理类
class InventoryProxy(CustomUIScreenProxy):
    def __init__(self, screenName, screenNode):
        CustomUIScreenProxy.__init__(self, screenName, screenNode)
        self.config = CommonConfig()

    def OnCreate(self):
        self.CreateCustomButton()

    def CreateCustomButton(self):
        screen = self.GetScreenNode()
        PocketPanelPath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/root_panel/hotbar_and_panels/gamepad_helper_border/both_panels/right_panel/armor_tab_content/content/equipment_and_renderer/armor_panel/armor_and_player/player_preview_border/player_bg"
        panel = screen.GetBaseUIControl(PocketPanelPath)
        if not panel:
            ClassicPanelPath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/content_stack_panel/player_inventory/inventory_panel_top_half/player_armor_panel/player_bg"
            panel = screen.GetBaseUIControl(ClassicPanelPath)
        if not panel:
            logging.error("铂: 无法找到特定界面")
            return
        button = screen.CreateChildControl(self.config.UI_DEF_BAUBLE_BTN, "bauble_button", panel).asButton()
        button.AddTouchEventParams({"isSwallow": True})
        button.SetButtonTouchUpCallback(self.OnBaubleButtonClicked)

    def OnBaubleButtonClicked(self, args):
        clientApi.PopTopUI()
        CallOTClient(clientApi.GetLocalPlayerId(), "OpenBaubleUi")


# 监听UI初始化注册代理类以及饰品栏UI
@Listen(Events.UiInitFinished)
def OnUiInitFinished(args):
    NativeScreenManager = clientApi.GetNativeScreenManagerCls()
    NativeScreenManager.instance().RegisterScreenProxy("crafting.inventory_screen",
                                                       "Script_UI.UIClient.baubleClient.InventoryProxy")
    NativeScreenManager.instance().RegisterScreenProxy("crafting_pocket.inventory_screen_pocket",
                                                       "Script_UI.UIClient.baubleClient.InventoryProxy")

    GlobalData.uiNode = BaubleUiNode()


@CallBackKey("OpenBaubleUi")
def OpenBaubleUi():
    uiNode = GlobalData.uiNode
    if uiNode:
        uiNode.OnOpenBtnClick()
    else:
        logging.error("铂: ui尚未初始化")


# 计算耐久度比例，用于显示耐久度槽
def calculateDurabilityRatio(itemDict):
    itemComp = clientApi.GetEngineCompFactory().CreateItem(clientApi.GetLevelId())
    basicInfo = itemComp.GetItemBasicInfo(itemDict.get("itemName", ""), itemDict.get("auxValue", 0))
    if basicInfo:
        currentDurability = itemDict.get("durability")
        if currentDurability is None:
            return 1
        maxDurability = basicInfo.get("maxDurability", 0)
        if maxDurability != 0:
            return currentDurability * 1.0 / maxDurability
    return 1


# 延迟执行函数
@EasyThread.IsThread
def DelayRun(func, delayTime=0.1):
    comp = clientApi.GetEngineCompFactory().CreateGame(levelId)
    comp.AddTimer(delayTime, func)


@EasyScreenNodeCls.Binding(CommonConfig.UI_DEF_MAIN)
class BaubleUiNode(EasyScreenNodeCls):

    def __init__(self):
        pass

    # 打开按钮点击回调
    def OnOpenBtnClick(self):
        self.SetAllResponse(False)
        self.InitBaubleBtnCallback()

        baublePath = BaublePath
        swallowInputPanel = self.GetBaseUIControl(baublePath.swallowInputPanel).asInputPanel()
        swallowInputPanel.SetVisible(True)
        swallowInputPanel.SetIsModal(True)
        DelayRun(self.GetBagInfoAndRender)

    # 关闭按钮点击回调
    @EasyScreenNodeCls.OnClick(BaublePath.closeBtnPath)
    def OnCloseBtnClick(self):
        self.SetAllResponse(True)
        baublePath = BaublePath
        swallowInputPanel = self.GetBaseUIControl(baublePath.swallowInputPanel).asInputPanel()
        swallowInputPanel.SetVisible(False)
        swallowInputPanel.SetIsModal(False)

    # 设置是否响应玩家输入
    def SetAllResponse(self, canResponse):
        clientApi.HideHudGUI(not canResponse)
        clientApi.SetResponse(canResponse)

        if clientApi.GetPlatform() == 0:
            comp = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLevelId())
            comp.SimulateTouchWithMouse(not canResponse)

        comp = clientApi.GetEngineCompFactory().CreateOperation(clientApi.GetLevelId())
        comp.SetCanAll(canResponse)

    # 获取背包信息并渲染物品栏
    def GetBagInfoAndRender(self):
        def RenderBagUi(path, item):
            try:
                itemRenderer = self.GetBaseUIControl(path + BaublePath.itemRenderBasePath).asItemRenderer()
                itemCount = self.GetBaseUIControl(path + BaublePath.itemCountBasePath).asLabel()
                durability = self.GetBaseUIControl(path + BaublePath.durabilityBasePath).asImage()
                durabilityBg = self.GetBaseUIControl(path + BaublePath.durabilityBgBasePath).asImage()
            except Exception as e:
                logging.error("铂: {}".format(e))
                return

            if item:
                # 物品渲染
                isEnchanted = item.get("enchantData") and len(item.get("enchantData")) > 0
                itemRenderer.SetUiItem(item["newItemName"], item["newAuxValue"], isEnchanted,
                                       item.get("userData"))
                itemRenderer.SetVisible(True)

                # 数量渲染
                if item["count"] > 1:
                    itemCount.SetText(str(item["count"]))
                    itemCount.SetVisible(True)
                else:
                    itemCount.SetVisible(False)

                # 耐久渲染
                if item["durability"] > 0:
                    durabilityRatio = calculateDurabilityRatio(item)
                    durability.SetSpriteClipRatio(1)  # 重置耐久度偏移
                    if durabilityRatio != 1:
                        durabilityBg.SetVisible(True)
                        durability.SetVisible(True)
                        durability.SetSpriteColor((1 - durabilityRatio, durabilityRatio, 0))
                        durability.SetSpriteClipRatio(1 - durabilityRatio)
                else:
                    durabilityBg.SetVisible(False)
                    durability.SetVisible(False)
            else:
                itemRenderer.SetVisible(False)
                itemCount.SetVisible(False)
                durabilityBg.SetVisible(False)
                durability.SetVisible(False)

        bagComp = clientApi.GetEngineCompFactory().CreateItem(clientApi.GetLocalPlayerId())
        itemList = bagComp.GetPlayerAllItems(clientApi.GetMinecraftEnum().ItemPosType.INVENTORY, True)

        for slotIndex in range(0, 9):
            bagGridChild = BaublePath.hotbarGridPath + BaublePath.slotBtnBasePath + str(slotIndex + 1)
            itemDict = itemList[slotIndex]
            GlobalData.bagInfo[slotIndex] = itemDict
            GlobalData.slotToPath[slotIndex] = bagGridChild

            itemSelected = self.GetBaseUIControl(bagGridChild + BaublePath.itemSelectedBasePath).asImage()
            itemSelected.SetVisible(False)

            itemBtn = self.GetBaseUIControl(bagGridChild).asButton()
            itemBtn.AddTouchEventParams({"isSwallow": True})
            itemBtn.SetButtonTouchUpCallback(self.ItemBtnCallback)
            RenderBagUi(bagGridChild, itemDict)

        for slotIndex in range(9, 36):
            bagGridChild = BaublePath.inventoryGridPath + BaublePath.slotBtnBasePath + str(slotIndex + 1 - 9)
            itemDict = itemList[slotIndex]
            GlobalData.bagInfo[slotIndex] = itemDict
            GlobalData.slotToPath[slotIndex] = bagGridChild

            itemSelected = self.GetBaseUIControl(bagGridChild + BaublePath.itemSelectedBasePath).asImage()
            itemSelected.SetVisible(False)

            itemBtn = self.GetBaseUIControl(bagGridChild).asButton()
            itemBtn.AddTouchEventParams({"isSwallow": True})
            itemBtn.SetButtonTouchUpCallback(self.ItemBtnCallback)
            RenderBagUi(bagGridChild, itemDict)

    # 物品栏点击回调
    def ItemBtnCallback(self, data):
        path = data["ButtonPath"]
        if path.split("/")[-2] == "hotbar_grid":
            slot = int(re.findall(r"\d+", path)[-1]) - 1
        else:
            slot = int(re.findall(r"\d+", path)[-1]) - 1 + 9

        # 已选择饰品栏
        if GlobalData.baubleSlotSelect != -1:
            self.SwitchBauble(GlobalData.baubleSlotSelect, slot)
            GlobalData.baubleSlotSelect = -1
            return

        # 选择
        if GlobalData.bagInfo[slot] and GlobalData.slotSelect == -1:
            GlobalData.slotSelect = slot
            itemSelected = self.GetBaseUIControl(path + BaublePath.itemSelectedBasePath).asImage()
            itemSelected.SetVisible(True)

        # 移动和交换
        elif GlobalData.slotSelect != -1:
            self.SwapItem(GlobalData.slotSelect, slot)
            GlobalData.slotSelect = -1

    # 物品栏移动逻辑
    def SwapItem(self, fromSlot, toSlot):
        if fromSlot == toSlot:
            path = GlobalData.slotToPath[fromSlot]
            itemSelected = self.GetBaseUIControl(path + BaublePath.itemSelectedBasePath).asImage()
            itemSelected.SetVisible(False)
        else:
            Call("SwapItem", {"playerId": clientApi.GetLocalPlayerId(), "fromSlot": fromSlot, "toSlot": toSlot})
            DelayRun(self.GetBagInfoAndRender)

    # 注册饰品栏按钮回调
    def InitBaubleBtnCallback(self):
        targetBaublePath = BaublePath.baubleContentMobilePath
        # 测试栏位是否存在
        if self.GetBaseUIControl(targetBaublePath):
            pass
        elif self.GetBaseUIControl(BaublePath.baubleContentPCPath):
            targetBaublePath = BaublePath.baubleContentPCPath
        else:
            logging.error("铂: 未找到饰品栏")
            return

        for panelPath, btnPath in BaublePath.baubleSlotPanelList.items():
            baubleBtn = self.GetBaseUIControl(targetBaublePath + panelPath + btnPath).asButton()
            baubleBtn.AddTouchEventParams({"isSwallow": True})
            baubleBtn.SetButtonTouchUpCallback(self.OnBaubleSlotClick)

    # 饰品栏槽位点击回调
    def OnBaubleSlotClick(self, data):
        path = data["ButtonPath"]
        itemSelected = self.GetBaseUIControl(path + "/item_selected_img").asImage()

        # 选择
        if len(GlobalData.baubleInfo.get(path, {})) > 0 and GlobalData.baubleSlotSelect == -1:
            GlobalData.baubleSlotSelect = path
            itemSelected.SetVisible(True)
        elif GlobalData.baubleSlotSelect == path:
            GlobalData.baubleSlotSelect = -1
            itemSelected.SetVisible(False)
        elif GlobalData.baubleSlotSelect != -1:
            self.SwitchBauble(GlobalData.baubleSlotSelect, path)
            GlobalData.baubleSlotSelect = -1

        # 装备
        if GlobalData.slotSelect != -1:
            # TODO(判断物品是否可以装备)
            self.SwitchBauble(GlobalData.slotSelect, path)
            GlobalData.slotSelect = -1
            GlobalData.baubleSlotSelect = -1
            return

    # 饰品栏切换逻辑
    def SwitchBauble(self, fromSlot, toSlot):
        # 物品栏到饰品栏
        if isinstance(fromSlot, type(1)) and isinstance(toSlot, type("")):
            baubleItem = GlobalData.bagInfo[fromSlot]
            oldBaubleItem = GlobalData.baubleInfo.get(toSlot, {})
            if oldBaubleItem and len(oldBaubleItem) > 0:
                # 添加玩家物品
                Call("AddItem", {"playerId": clientApi.GetLocalPlayerId(), "slot": fromSlot, "itemDict": oldBaubleItem})
            else:
                # 移除玩家物品
                Call("RemoveItem", {"playerId": clientApi.GetLocalPlayerId(), "slot": fromSlot})
            DelayRun(self.GetBagInfoAndRender)
            # 饰品栏渲染
            GlobalData.baubleInfo[toSlot] = baubleItem
            self.renderBaubleUi(toSlot, baubleItem)

        # 饰品栏到物品栏
        elif isinstance(fromSlot, type("")) and isinstance(toSlot, type(1)):
            baubleItem = GlobalData.baubleInfo[fromSlot]
            bagItem = GlobalData.bagInfo[toSlot]
            needRenderItem = {}
            if bagItem and len(bagItem) > 0:
                # 移除玩家物品
                Call("RemoveItem", {"playerId": clientApi.GetLocalPlayerId(), "slot": toSlot})
                needRenderItem = bagItem
            # 添加玩家物品
            Call("AddItem", {"playerId": clientApi.GetLocalPlayerId(), "slot": toSlot, "itemDict": baubleItem})
            DelayRun(self.GetBagInfoAndRender)
            # 饰品栏渲染
            GlobalData.baubleInfo[fromSlot] = needRenderItem
            self.renderBaubleUi(fromSlot, needRenderItem)

        # 饰品栏到饰品栏
        elif isinstance(fromSlot, type("")) and isinstance(toSlot, type("")):
            fromItem = GlobalData.baubleInfo[fromSlot]
            toItem = GlobalData.baubleInfo.get(toSlot, {})
            # 饰品栏渲染
            GlobalData.baubleInfo[fromSlot] = toItem
            GlobalData.baubleInfo[toSlot] = fromItem
            self.renderBaubleUi(fromSlot, toItem)
            self.renderBaubleUi(toSlot, fromItem)

        return False

    # 饰品栏渲染
    def renderBaubleUi(self, slotPath, itemDict):
        imgPath = slotPath.split("/")[-1].replace("btn", "img")
        imgPath = "/".join(slotPath.split("/")[:-1]) + "/" + imgPath
        baubleImg = self.GetBaseUIControl(imgPath).asImage()
        itemRenderer = self.GetBaseUIControl(slotPath + "/item_renderer").asItemRenderer()
        itemSelected = self.GetBaseUIControl(slotPath + "/item_selected_img").asImage()

        durability = self.GetBaseUIControl(slotPath + BaublePath.durabilityBasePath).asImage()
        durabilityBg = self.GetBaseUIControl(slotPath + BaublePath.durabilityBgBasePath).asImage()

        if itemDict:
            baubleImg.SetVisible(False)
            # 物品渲染
            isEnchanted = itemDict.get("enchantData") and len(itemDict.get("enchantData")) > 0
            itemRenderer.SetUiItem(itemDict["newItemName"], itemDict["newAuxValue"], isEnchanted,
                                   itemDict.get("userData"))
            itemRenderer.SetVisible(True)
            # 耐久渲染
            if itemDict["durability"] > 0:
                durabilityRatio = calculateDurabilityRatio(itemDict)
                durability.SetSpriteClipRatio(1)
                if durabilityRatio != 1:
                    durabilityBg.SetVisible(True)
                    durability.SetVisible(True)
                    durability.SetSpriteColor((1 - durabilityRatio, durabilityRatio, 0))
                    durability.SetSpriteClipRatio(1 - durabilityRatio)
            else:
                durabilityBg.SetVisible(False)
                durability.SetVisible(False)
        else:
            baubleImg.SetVisible(True)
            itemRenderer.SetVisible(False)
            durabilityBg.SetVisible(False)
            durability.SetVisible(False)

        itemSelected.SetVisible(False)
