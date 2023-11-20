# coding=utf-8
from ..QuModLibs.Client import *
from ..QuModLibs.UI import *
from .. import loggingUtils as logging
from ..commonConfig import BaubleDict
from ..commonConfig import BaubleEnum
import re
import time

import mod.client.ui.screenNode as ScreenNode

CustomUIScreenProxy = clientApi.GetUIScreenProxyCls()


# 饰品装备广播
def BaubleEquippedBroadcaster(baubleSlot, itemDict):
    Call("BaubleEquipped", {"playerId": playerId, "baubleSlot": baubleSlot, "itemDict": itemDict})
    CallOTClient(playerId, "BaubleEquipped", {"playerId": playerId, "baubleSlot": baubleSlot, "itemDict": itemDict})


# 饰品卸下广播
def BaubleUnequippedBroadcaster(baubleSlot, itemDict):
    Call("BaubleUnequipped", {"playerId": playerId, "baubleSlot": baubleSlot, "itemDict": itemDict})
    CallOTClient(playerId, "BaubleUnequipped", {"playerId": playerId, "baubleSlot": baubleSlot, "itemDict": itemDict})


# 基础常量
class BaubleConfig(object):
    UI_DEF = "bauble_base_panel"
    UI_DEF_MAIN = "bauble_base_panel.main"
    UI_DEF_BAUBLE_BTN = "bauble_base_panel.bauble_button"

    PLATINUM_LOCAL_DATA = "platinum_local_data"
    BAUBLE_SLOT_INFO = "bauble_slot_info"

    # 通过函数注册
    SLOT_PATH_TO_NAME = {}
    NAME_TO_SLOT_PATH = {}

    SLOT_TO_DEF = {
        "helmet": BaubleEnum.HELMET,
        "necklace": BaubleEnum.NECKLACE,
        "back": BaubleEnum.BACK,
        "armor": BaubleEnum.ARMOR,
        "hand_1": BaubleEnum.HAND,
        "hand_2": BaubleEnum.HAND,
        "belt": BaubleEnum.BELT,
        "shoes": BaubleEnum.SHOES,
        "other_1": BaubleEnum.OTHER,
        "other_2": BaubleEnum.OTHER,
        "other_3": BaubleEnum.OTHER,
        "other_4": BaubleEnum.OTHER
    }
    DEF_TO_SLOT = {
        BaubleEnum.HELMET: "helmet",
        BaubleEnum.NECKLACE: "necklace",
        BaubleEnum.BACK: "back",
        BaubleEnum.ARMOR: "armor",
        BaubleEnum.BELT: "belt",
        BaubleEnum.SHOES: "shoes",
    }


# 全局变量
class GlobalData(object):
    uiNode = None  # type: ScreenNode

    uiProfile = clientApi.GetEngineCompFactory().CreatePlayerView(levelId).GetUIProfile()

    bagInfo = {}
    baubleInfo = {}
    slotToPath = {}

    slotSelect = -1
    baubleSlotSelect = -1

    itemInfoAlpha = 0.0


# ui路径
class BaublePath(object):
    # classical
    swallowInputPanel = "/swallow_input_panel"
    bgImgPath = swallowInputPanel + "/bg_img"
    baseStackPanelPath = bgImgPath + "/base_stack_panel"
    itemInfoBgPath = swallowInputPanel + "/item_info_bg"
    itemInfoTextPath = itemInfoBgPath + "/item_info_text"
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

    # pocket
    pocketInputPanel = "/mobile_input_panel"
    pocketBgImgPath = pocketInputPanel + "/bg_img"
    pocketItemInfoBgPath = pocketInputPanel + "/item_info_bg"
    pocketItemInfoTextPath = pocketItemInfoBgPath + "/item_info_text"
    pocketBaseStackPanelPath = pocketBgImgPath + "/base_stack_panel"
    # info
    pocketCloseBtnPath = pocketBaseStackPanelPath + "/info_stack_panel/info_upper_panel/close_btn"
    pocketPaperDollPath = pocketBaseStackPanelPath + "/info_stack_panel/info_upper_panel/netease_paper_doll"
    # bauble
    pocketBaubleStackPanelPath = pocketBaseStackPanelPath + "/info_stack_panel/bauble_panel/bauble_stack_panel"
    # inventory
    pocketInvMouseContentPath = pocketBaseStackPanelPath + "/inventory_scroll_view/scroll_mouse/scroll_view/stack_panel/background_and_viewport/scrolling_view_port/scrolling_content"
    pocketInvMobileContentPath = pocketBaseStackPanelPath + "/inventory_scroll_view/scroll_touch/scroll_view/panel/background_and_viewport/scrolling_view_port/scrolling_content"

    # base
    slotBtnBasePath = "/slot_btn"
    slotBtnBigBasePath = "/slot_btn_big"
    itemRenderBasePath = "/item_renderer"
    itemSelectedBasePath = "/item_selected_img"
    durabilityBgBasePath = itemRenderBasePath + "/durability_base_img"
    durabilityBasePath = itemRenderBasePath + "/durability_img"
    itemCountBasePath = itemRenderBasePath + "/item_count"

    # dict
    # pocket bauble stack
    pocketBaubleStackList = {
        "/bauble_one_stack_panel": [
            "/bauble_helmet_panel", "/bauble_necklace_panel", "/bauble_back_panel", "/bauble_armor_panel"
        ],
        "/bauble_two_stack_panel": [
            "/bauble_hand_panel_1", "/bauble_hand_panel_2", "/bauble_belt_panel", "/bauble_shoes_panel"
        ],
        "/bauble_three_stack_panel": [
            "/bauble_other_panel_1", "/bauble_other_panel_2", "/bauble_other_panel_3", "/bauble_other_panel_4"
        ]
    }
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

    # btn to slot
    btnToSlot = {
        "bauble_helmet_btn": "helmet",
        "bauble_necklace_btn": "necklace",
        "bauble_back_btn": "back",
        "bauble_armor_btn": "armor",
        "bauble_hand_btn": "hand",
        "bauble_belt_btn": "belt",
        "bauble_shoes_btn": "shoes",
        "bauble_other_btn": "other"
    }


# 背包界面代理类
class InventoryProxy(CustomUIScreenProxy):
    def __init__(self, screenName, screenNode):
        CustomUIScreenProxy.__init__(self, screenName, screenNode)
        self.config = BaubleConfig()

    def OnCreate(self):
        self.CreateCustomButton()

    def CreateCustomButton(self):
        screen = self.GetScreenNode()
        panelPath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/root_panel/hotbar_and_panels/gamepad_helper_border/both_panels/right_panel/armor_tab_content/content/equipment_and_renderer/armor_panel/armor_and_player/player_preview_border/player_bg"
        panel = screen.GetBaseUIControl(panelPath)
        if not panel:
            panelPath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/content_stack_panel/player_inventory/inventory_panel_top_half/player_armor_panel/player_bg"
            panel = screen.GetBaseUIControl(panelPath)
        if not panel:
            logging.error("铂: 无法找到特定界面")
            return
        try:
            baubleBtn = screen.GetBaseUIControl(panelPath + "/bauble_button").asButton()
        except:
            baubleBtn = screen.CreateChildControl(self.config.UI_DEF_BAUBLE_BTN, "bauble_button", panel).asButton()
        baubleBtn.AddTouchEventParams({"isSwallow": True})
        baubleBtn.SetButtonTouchUpCallback(self.OnBaubleButtonClicked)

    def OnBaubleButtonClicked(self, args):
        clientApi.PopTopUI()
        CallOTClient(clientApi.GetLocalPlayerId(), "OpenBaubleUi")


# 获取玩家饰品栏物品信息
def DisplayPlayerBaubleInfo():
    comp = clientApi.GetEngineCompFactory().CreateName(playerId)
    playerName = comp.GetName()
    baubleInfo = GlobalData.baubleInfo
    displayDict = {}
    for slotName, itemDict in baubleInfo.items():
        comp = clientApi.GetEngineCompFactory().CreateItem(clientApi.GetLevelId())
        basicInfo = comp.GetItemBasicInfo(itemDict.get("itemName", ""), itemDict.get("auxValue", 0))
        if basicInfo:
            displayDict[slotName] = basicInfo["itemName"]
        else:
            displayDict[slotName] = "空"
    displayText = ["玩家 {} 的饰品栏信息:".format(playerName)]
    for slotName, item in displayDict.items():
        displayText.append("{}: {}\n".format(slotName, item))
    logging.infoLines(displayText)


# 监听客户端mod加载完成读取饰品文件
@Listen(Events.OnLocalPlayerStopLoading)
def OnLoadClientAddonScriptsAfter(data):
    comp = clientApi.GetEngineCompFactory().CreateConfigClient(levelId)
    configData = comp.GetConfigData(BaubleConfig.PLATINUM_LOCAL_DATA)
    GlobalData.baubleInfo = configData.get(BaubleConfig.BAUBLE_SLOT_INFO, {})
    if len(GlobalData.baubleInfo) == 0:
        logging.error("铂: 未找到玩家饰品数据, 或读取失败!!!")
    else:
        logging.info("铂: 读取饰品数据成功")
        DisplayPlayerBaubleInfo()
        for slotName, bauble in GlobalData.baubleInfo.items():
            if len(bauble) > 0:
                BaubleEquippedBroadcaster(BaubleConfig.SLOT_TO_DEF[slotName], bauble)


# 监听客户端关闭保存饰品文件
def QuDestroy():
    comp = clientApi.GetEngineCompFactory().CreateConfigClient(levelId)
    configData = comp.GetConfigData(BaubleConfig.PLATINUM_LOCAL_DATA)
    configData[BaubleConfig.BAUBLE_SLOT_INFO] = GlobalData.baubleInfo
    isSave = comp.SetConfigData(BaubleConfig.PLATINUM_LOCAL_DATA, configData)
    if isSave:
        logging.info("铂: 保存饰品数据成功")
    else:
        logging.error("铂: 保存饰品数据失败!!! 丢失玩家饰品数据")


# 监听UI初始化注册代理类以及饰品栏UI
@Listen(Events.UiInitFinished)
def OnUiInitFinished(args):
    NativeScreenManager = clientApi.GetNativeScreenManagerCls()
    NativeScreenManager.instance().RegisterScreenProxy("crafting.inventory_screen",
                                                       "Script_Platinum.Script_UI.baubleClient.InventoryProxy")
    NativeScreenManager.instance().RegisterScreenProxy("crafting_pocket.inventory_screen_pocket",
                                                       "Script_Platinum.Script_UI.baubleClient.InventoryProxy")

    GlobalData.uiNode = BaubleUiNode()


# 打开饰品栏界面
@CallBackKey("OpenBaubleUi")
def OpenBaubleUi():
    uiNode = GlobalData.uiNode
    if uiNode:
        uiNode.OnOpenBtnClick()
    else:
        logging.error("铂: ui尚未初始化")


# 计算耐久度比例，用于显示耐久度槽
def CalculateDurabilityRatio(itemDict):
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
def DelayRun(func, delayTime=0.05, *args):
    time.sleep(delayTime)
    EasyThread.NextTick(func, args)


# 玩家右键装备饰品
@AllowCall
def EquipBauble(itemDict, baubleSlot):
    isEquip = False
    if baubleSlot != BaubleEnum.OTHER and baubleSlot != BaubleEnum.HAND:
        slotName = BaubleConfig.DEF_TO_SLOT[baubleSlot]
        if len(GlobalData.baubleInfo.get(slotName, {})) == 0:
            GlobalData.baubleInfo[slotName] = itemDict
            isEquip = True

    elif baubleSlot == BaubleEnum.OTHER:
        for slot in range(1, 4):
            slotName = "other_{}".format(slot), {}
            if len(GlobalData.baubleInfo.get(slotName)) == 0:
                GlobalData.baubleInfo[slotName] = itemDict
                isEquip = True
                break
    elif baubleSlot == BaubleEnum.HAND:
        for slot in range(1, 2):
            slotName = "hand_{}".format(slot), {}
            if len(GlobalData.baubleInfo.get(slotName, {})) == 0:
                GlobalData.baubleInfo[slotName] = itemDict
                isEquip = True
                break
    if isEquip:
        # 播放声音
        comp = clientApi.GetEngineCompFactory().CreateCustomAudio(levelId)
        comp.PlayCustomMusic("armor.equip_iron", (0, 0, 0), 1, 1, False, playerId)
        # 广播装备饰品
        BaubleEquippedBroadcaster(baubleSlot, itemDict)
        # 移除玩家手上物品
        Call("RemoveItem", {"playerId": clientApi.GetLocalPlayerId()})


# 设置是否响应玩家输入
def SetAllResponse(canResponse):
    clientApi.HideHudGUI(not canResponse)
    clientApi.SetResponse(canResponse)

    if clientApi.GetPlatform() == 0:
        comp = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLevelId())
        comp.SimulateTouchWithMouse(not canResponse)

    comp = clientApi.GetEngineCompFactory().CreateOperation(clientApi.GetLevelId())
    comp.SetCanAll(canResponse)


@EasyScreenNodeCls.Binding(BaubleConfig.UI_DEF_MAIN)
class BaubleUiNode(EasyScreenNodeCls):

    def __init__(self):
        self.InitBaubleBtnCallback()

    @staticmethod
    @Listen(Events.OnScriptTickClient)
    def Update():
        if GlobalData.itemInfoAlpha > 0:
            GlobalData.itemInfoAlpha -= 0.05
        else:
            GlobalData.itemInfoAlpha = 0

        try:
            # 显示物品信息
            if GlobalData.uiProfile == 0:
                itemInfoBg = GlobalData.uiNode.GetBaseUIControl(BaublePath.itemInfoBgPath).asImage()
            else:
                itemInfoBg = GlobalData.uiNode.GetBaseUIControl(BaublePath.pocketItemInfoBgPath).asImage()
            itemInfoBg.SetAlpha(GlobalData.itemInfoAlpha)
        except:
            pass

    # 打开按钮点击回调
    def OnOpenBtnClick(self):
        SetAllResponse(False)

        def OpenLogic():
            if GlobalData.uiProfile == 0:
                swallowInputPanel = self.GetBaseUIControl(BaublePath.swallowInputPanel).asInputPanel()
                swallowInputPanel.SetVisible(True)
                swallowInputPanel.SetIsModal(True)
            else:
                pocketInputPanel = self.GetBaseUIControl(BaublePath.pocketInputPanel).asInputPanel()
                pocketInputPanel.SetVisible(True)
                pocketInputPanel.SetIsModal(True)

            DelayRun(self.GetBagInfoAndRender)
            for slotName, itemDict in GlobalData.baubleInfo.items():
                slotPath = BaubleConfig.NAME_TO_SLOT_PATH[slotName]
                DelayRun(self.RenderBaubleUi, 0.1, slotPath, itemDict)
            # 渲染玩家纸娃娃
            DelayRun(self.RenderPlayerPaperDoll)

        # ui档案变化时重新初始化
        if GlobalData.uiProfile != clientApi.GetEngineCompFactory().CreatePlayerView(levelId).GetUIProfile():
            logging.info("铂: ui档案变化, 重新初始化")
            GlobalData.uiProfile = clientApi.GetEngineCompFactory().CreatePlayerView(levelId).GetUIProfile()
            # 重置临时变量
            BaubleConfig.NAME_TO_SLOT_PATH = {}
            BaubleConfig.SLOT_PATH_TO_NAME = {}
            self.InitBaubleBtnCallback()
            DelayRun(OpenLogic)
        else:
            OpenLogic()

    # 渲染玩家纸娃娃
    def RenderPlayerPaperDoll(self):
        try:
            if GlobalData.uiProfile == 0:
                playerPaperDoll = self.GetBaseUIControl(BaublePath.playerPaperDollPath).asNeteasePaperDoll()
                playerPaperDoll.RenderEntity({"entity_id": playerId, "scale": 0.4})
            else:
                pocketPaperDoll = self.GetBaseUIControl(BaublePath.pocketPaperDollPath).asNeteasePaperDoll()
                pocketPaperDoll.RenderEntity({"entity_id": playerId, "scale": 0.4})
        except:
            pass

    # 关闭按钮点击回调
    @EasyScreenNodeCls.OnClick(BaublePath.closeBtnPath)
    def OnClassicCloseBtnClick(self):
        SetAllResponse(True)
        swallowInputPanel = self.GetBaseUIControl(BaublePath.swallowInputPanel).asInputPanel()
        swallowInputPanel.SetVisible(False)
        swallowInputPanel.SetIsModal(False)

        # 重置临时变量
        GlobalData.slotSelect = -1
        GlobalData.baubleSlotSelect = -1
        GlobalData.itemInfoAlpha = 0.0

    @EasyScreenNodeCls.OnClick(BaublePath.pocketCloseBtnPath)
    def OnPocketCloseBtnClick(self):
        SetAllResponse(True)
        pocketInputPanel = self.GetBaseUIControl(BaublePath.pocketInputPanel).asInputPanel()
        pocketInputPanel.SetVisible(False)
        pocketInputPanel.SetIsModal(False)

        # 重置临时变量
        GlobalData.slotSelect = -1
        GlobalData.baubleSlotSelect = -1
        GlobalData.itemInfoAlpha = 0.0

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
                    durabilityRatio = CalculateDurabilityRatio(item)
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
        if GlobalData.uiProfile == 0:
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
        else:
            invContent = GlobalData.uiNode.GetBaseUIControl(BaublePath.pocketInvMobileContentPath)
            invContentPath = BaublePath.pocketInvMobileContentPath if invContent is not None \
                else BaublePath.pocketInvMouseContentPath

            for slotIndex in range(0, 36):
                bagGridChild = invContentPath + BaublePath.slotBtnBigBasePath + str(slotIndex + 1)
                itemDict = itemList[slotIndex]
                GlobalData.bagInfo[slotIndex] = itemDict
                GlobalData.slotToPath[slotIndex] = bagGridChild

                itemSelected = self.GetBaseUIControl(bagGridChild + BaublePath.itemSelectedBasePath).asImage()
                itemSelected.SetVisible(False)

                itemBtn = self.GetBaseUIControl(bagGridChild).asButton()
                itemBtn.AddTouchEventParams({"isSwallow": True})
                itemBtn.SetButtonTouchUpCallback(self.ItemBtnCallback)

                DelayRun(RenderBagUi, 0.1, bagGridChild, itemDict)

    # 物品栏点击回调
    def ItemBtnCallback(self, data):
        path = data["ButtonPath"]
        if GlobalData.uiProfile == 0:
            if path.split("/")[-2] == "hotbar_grid":
                slot = int(re.findall(r"\d+", path)[-1]) - 1
            else:
                slot = int(re.findall(r"\d+", path)[-1]) - 1 + 9
        else:
            slot = int(re.findall(r"\d+", path)[-1]) - 1

        itemInfo = GlobalData.bagInfo[slot]
        # 显示物品信息
        if itemInfo and len(itemInfo) > 0:
            itemName = GlobalData.bagInfo[slot]["newItemName"]
            customTips = GlobalData.bagInfo[slot]["customTips"]
            comp = clientApi.GetEngineCompFactory().CreateItem(levelId)
            itemName = comp.GetItemBasicInfo(itemName)["itemName"]

            showText = itemName if len(customTips) == 0 else customTips
            self.ShowInfo(showText)

        # 已选择饰品栏
        if GlobalData.baubleSlotSelect != -1:
            # 判断是否能够装备
            if itemInfo is None or CheckSlot(itemInfo, GlobalData.baubleSlotSelect):
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
        if GlobalData.uiProfile == 0:
            targetBaublePath = BaublePath.baubleContentMobilePath \
                if self.GetBaseUIControl(BaublePath.baubleContentMobilePath) else BaublePath.baubleContentPCPath

            if self.GetBaseUIControl(targetBaublePath) is None:
                logging.error("铂: 未找到饰品栏")
                return

            for panelPath, btnPath in BaublePath.baubleSlotPanelList.items():
                btnPath = targetBaublePath + panelPath + btnPath
                baubleBtn = self.GetBaseUIControl(btnPath).asButton()

                self.unifiedRegTrans(btnPath)

                baubleBtn.AddTouchEventParams({"isSwallow": True})
                baubleBtn.SetButtonTouchUpCallback(self.OnBaubleSlotClick)

        else:
            for basePanelPath, targetPanelPathList in BaublePath.pocketBaubleStackList.items():
                for targetPanelPath in targetPanelPathList:
                    baseBtnPath = BaublePath.baubleSlotPanelList[targetPanelPath]
                    btnPath = BaublePath.pocketBaubleStackPanelPath + basePanelPath + targetPanelPath + baseBtnPath
                    baubleBtn = self.GetBaseUIControl(btnPath).asButton()

                    self.unifiedRegTrans(btnPath)

                    baubleBtn.AddTouchEventParams({"isSwallow": True})
                    baubleBtn.SetButtonTouchUpCallback(self.OnBaubleSlotClick)

    # 饰品栏槽位点击回调
    def OnBaubleSlotClick(self, data):
        path = data["ButtonPath"]
        itemSelected = self.GetBaseUIControl(path + "/item_selected_img").asImage()

        slotName = BaubleConfig.SLOT_PATH_TO_NAME[path]
        itemInfo = GlobalData.baubleInfo.get(slotName, None)
        # 显示物品信息
        if itemInfo and len(itemInfo) > 0:
            itemName = GlobalData.baubleInfo[slotName]["newItemName"]
            customTips = GlobalData.baubleInfo[slotName]["customTips"]
            comp = clientApi.GetEngineCompFactory().CreateItem(levelId)
            itemName = comp.GetItemBasicInfo(itemName)["itemName"]

            showText = itemName if len(customTips) == 0 else customTips
            self.ShowInfo(showText)

        # 选择
        if len(GlobalData.baubleInfo.get(slotName, {})) > 0 and GlobalData.baubleSlotSelect == -1:
            GlobalData.baubleSlotSelect = path
            itemSelected.SetVisible(True)
        # 取消选择
        elif GlobalData.baubleSlotSelect == path:
            GlobalData.baubleSlotSelect = -1
            itemSelected.SetVisible(False)
        # 交换饰品栏位
        elif GlobalData.baubleSlotSelect != -1:
            canSwitch = CheckSlot(GlobalData.baubleInfo.get(slotName, {}), GlobalData.baubleSlotSelect) and \
                        CheckSlot(GlobalData.bagInfo[BaubleConfig.SLOT_PATH_TO_NAME[GlobalData.slotSelect]], path)
            if canSwitch:
                self.SwitchBauble(GlobalData.baubleSlotSelect, path)
                GlobalData.baubleSlotSelect = -1

        # 装备
        if GlobalData.slotSelect != -1:
            # 判断是否能够装备
            if CheckSlot(GlobalData.bagInfo[GlobalData.slotSelect], path):
                self.SwitchBauble(GlobalData.slotSelect, path)
                GlobalData.slotSelect = -1
                GlobalData.baubleSlotSelect = -1

    # 饰品栏切换逻辑
    def SwitchBauble(self, fromSlotPath, toSlotPath):
        # 物品栏到饰品栏
        if isinstance(fromSlotPath, type(1)) and isinstance(toSlotPath, type("")):
            toSlotName = BaubleConfig.SLOT_PATH_TO_NAME[toSlotPath]

            baubleItem = GlobalData.bagInfo[fromSlotPath]
            oldBaubleItem = GlobalData.baubleInfo.get(toSlotName, {})
            if oldBaubleItem and len(oldBaubleItem) > 0:
                # 添加玩家物品
                Call("AddItem",
                     {"playerId": clientApi.GetLocalPlayerId(), "slot": fromSlotPath, "itemDict": oldBaubleItem})
                # 广播卸下饰品
                BaubleUnequippedBroadcaster(BaubleConfig.SLOT_TO_DEF[toSlotName], oldBaubleItem)
            else:
                # 移除玩家物品
                Call("RemoveItem", {"playerId": clientApi.GetLocalPlayerId(), "slot": fromSlotPath})
            DelayRun(self.GetBagInfoAndRender)
            # 饰品栏信息
            GlobalData.baubleInfo[toSlotName] = baubleItem
            # 广播装备饰品
            BaubleEquippedBroadcaster(BaubleConfig.SLOT_TO_DEF[toSlotName], baubleItem)
            # 饰品栏渲染
            self.RenderBaubleUi(toSlotPath, baubleItem)

        # 饰品栏到物品栏
        elif isinstance(fromSlotPath, type("")) and isinstance(toSlotPath, type(1)):
            fromSlotName = BaubleConfig.SLOT_PATH_TO_NAME[fromSlotPath]

            baubleItem = GlobalData.baubleInfo[fromSlotName]
            bagItem = GlobalData.bagInfo[toSlotPath]
            needRenderItem = {}
            if bagItem and len(bagItem) > 0:
                # 移除玩家物品
                Call("RemoveItem", {"playerId": clientApi.GetLocalPlayerId(), "slot": toSlotPath})
                needRenderItem = bagItem
                # 广播装备饰品
                BaubleEquippedBroadcaster(BaubleConfig.SLOT_TO_DEF[fromSlotName], bagItem)
            # 添加玩家物品
            Call("AddItem", {"playerId": clientApi.GetLocalPlayerId(), "slot": toSlotPath, "itemDict": baubleItem})
            DelayRun(self.GetBagInfoAndRender)
            # 饰品栏信息
            GlobalData.baubleInfo[fromSlotName] = needRenderItem
            # 广播卸下饰品
            BaubleUnequippedBroadcaster(BaubleConfig.SLOT_TO_DEF[fromSlotName], baubleItem)
            # 饰品栏渲染
            self.RenderBaubleUi(fromSlotPath, needRenderItem)

        # 饰品栏到饰品栏
        elif isinstance(fromSlotPath, type("")) and isinstance(toSlotPath, type("")):
            fromSlotName = BaubleConfig.SLOT_PATH_TO_NAME[fromSlotPath]
            toSlotName = BaubleConfig.SLOT_PATH_TO_NAME[toSlotPath]

            fromItem = GlobalData.baubleInfo[fromSlotName]
            toItem = GlobalData.baubleInfo.get(toSlotName, {})
            # 饰品栏信息
            GlobalData.baubleInfo[fromSlotName] = toItem
            GlobalData.baubleInfo[toSlotName] = fromItem
            # 饰品栏渲染
            self.RenderBaubleUi(fromSlotPath, toItem)
            self.RenderBaubleUi(toSlotPath, fromItem)

        return False

    # 饰品栏渲染
    def RenderBaubleUi(self, slotPath, itemDict):
        imgPath = slotPath.split("/")[-1].replace("btn", "img")
        imgPath = "/".join(slotPath.split("/")[:-1]) + "/" + imgPath
        try:
            baubleImg = self.GetBaseUIControl(imgPath).asImage()
            itemRenderer = self.GetBaseUIControl(slotPath + "/item_renderer").asItemRenderer()
            itemSelected = self.GetBaseUIControl(slotPath + "/item_selected_img").asImage()
        except Exception as e:
            logging.error("铂: {}".format(e))
            logging.error("铂: path: {}".format(slotPath))
            return

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
                durabilityRatio = CalculateDurabilityRatio(itemDict)
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

    def ShowInfo(self, info):
        if GlobalData.uiProfile == 0:
            itemInfoText = self.GetBaseUIControl(BaublePath.itemInfoTextPath).asLabel()
        else:
            itemInfoText = self.GetBaseUIControl(BaublePath.pocketItemInfoTextPath).asLabel()
        itemInfoText.SetText(info)
        GlobalData.itemInfoAlpha = 2.5

    # UI档案统一化注册栏位对应关系
    def unifiedRegTrans(self, path):
        btnName = path.split("/")[-1]
        panelName = path.split("/")[-2]
        if "hand" not in panelName and "other" not in panelName:
            slotName = BaublePath.btnToSlot[btnName]
        else:
            slotName = BaublePath.btnToSlot[btnName] + "_" + re.findall(r"\d+", panelName)[-1]
        BaubleConfig.SLOT_PATH_TO_NAME[path] = slotName
        self.unifiedRegSlotName2Path(slotName)

    # 统一注册槽位名字到路径
    def unifiedRegSlotName2Path(self, slot):
        if GlobalData.uiProfile == 0:
            basePath = BaublePath.baubleContentMobilePath if self.GetBaseUIControl(BaublePath.baubleContentMobilePath) \
                else BaublePath.baubleContentPCPath
            btnName = "/bauble_{}_btn".format(slot.split("_")[0])
            if "hand" in slot or "other" in slot:
                panelName = "/bauble_{}_panel_{}".format(slot.split("_")[0], slot.split("_")[-1])
            else:
                panelName = "/bauble_{}_panel".format(slot)

            BaubleConfig.NAME_TO_SLOT_PATH[slot] = basePath + panelName + btnName
        else:
            if "helmet" in slot or "necklace" in slot or "armor" in slot or "back" in slot:
                basePanelPath = "/bauble_one_stack_panel"
            elif "hand" in slot or "shoes" in slot or "belt" in slot:
                basePanelPath = "/bauble_two_stack_panel"
            else:
                basePanelPath = "/bauble_three_stack_panel"
            btnName = "/bauble_{}_btn".format(slot.split("_")[0])
            if "hand" in slot or "other" in slot:
                panelName = "/bauble_{}_panel_{}".format(slot.split("_")[0], slot.split("_")[-1])
            else:
                panelName = "/bauble_{}_panel".format(slot)

            BaubleConfig.NAME_TO_SLOT_PATH[slot] = \
                BaublePath.pocketBaubleStackPanelPath + basePanelPath + panelName + btnName


# 检测物品槽位
def CheckSlot(itemDict, slotPath):
    if not itemDict or len(itemDict) < 0:
        return False

    comp = clientApi.GetEngineCompFactory().CreateItem(levelId)
    baseInfo = comp.GetItemBasicInfo(itemDict["newItemName"], itemDict["newAuxValue"])
    if baseInfo["maxStackSize"] > 1:
        logging.error("铂: 饰品 {} 最大堆叠数量大于1".format(itemDict["newItemName"]))
        return False
    if itemDict["newItemName"] in BaubleDict.keys():
        baubleValue = BaubleDict[itemDict["newItemName"]]
        if isinstance(baubleValue, type("")):
            targetSlot = baubleValue
        elif isinstance(baubleValue, type([])):
            targetSlot = baubleValue[0]
        else:
            logging.error("铂: 饰品 {} 配置错误, 请检查Script_Platinum/commonConfig.py".format(itemDict["newItemName"]))
            return False

        if BaubleConfig.SLOT_TO_DEF[BaubleConfig.SLOT_PATH_TO_NAME[slotPath]] == targetSlot:
            return True

    return False


# 玩家死亡事件
@AllowCall
def OnPlayerDie(keepInv, pos, dimensionId):
    try:
        if GlobalData.uiProfile == 0:
            GlobalData.uiNode.OnClassicCloseBtnClick()
        else:
            GlobalData.uiNode.OnPocketCloseBtnClick()
    except:
        logging.error("铂: 关闭饰品栏失败!!! 饰品栏尚未初始化")

    if not keepInv:
        # 广播卸下饰品
        for slotName, bauble in GlobalData.baubleInfo.items():
            if len(bauble) > 0:
                BaubleUnequippedBroadcaster(BaubleConfig.SLOT_TO_DEF[slotName], bauble)
                Call("SpawnItem", bauble, pos, dimensionId)
        # 清空饰品栏
        GlobalData.baubleInfo = {}
        # 清空物品栏
        GlobalData.bagInfo = {}
        # 重置临时变量
        GlobalData.slotSelect = -1
        GlobalData.baubleSlotSelect = -1
        GlobalData.itemInfoAlpha = 0.0
