# coding=utf-8
from ..QuModLibs.Client import *
from ..QuModLibs.UI import *
from .. import loggingUtils as logging
from ..CommonConfig import BaubleDict
from ..CommonConfig import BaubleEnum
import re

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
class CommonConfig(object):
    UI_DEF = "bauble_base_panel"
    UI_DEF_MAIN = "bauble_base_panel.main"
    UI_DEF_BAUBLE_BTN = "bauble_base_panel.bauble_button"

    PLATINUM_LOCAL_DATA = "platinum_local_data"
    BAUBLE_SLOT_INFO = "bauble_slot_info"

    SLOT_PATH_TO_NAME = {
        "bauble_helmet_btn": BaubleEnum.HELMET,
        "bauble_necklace_btn": BaubleEnum.NECKLACE,
        "bauble_back_btn": BaubleEnum.BACK,
        "bauble_armor_btn": BaubleEnum.ARMOR,
        "bauble_hand_btn": BaubleEnum.HAND,
        "bauble_belt_btn": BaubleEnum.BELT,
        "bauble_shoes_btn": BaubleEnum.SHOES,
        "bauble_other_btn": BaubleEnum.OTHER
    }
    NAME_TO_SLOT_PATH = {}


# ui路径
class BaublePath(object):
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


# 全局变量
class GlobalData(object):
    try:
        uiNode = ScreenNode.ScreenNode()
    except:
        uiNode = None

    bagInfo = {}
    baubleInfo = {}
    slotToPath = {}

    slotSelect = -1
    baubleSlotSelect = -1

    itemInfoAlpha = 0.0


# 背包界面代理类
class InventoryProxy(CustomUIScreenProxy):
    def __init__(self, screenName, screenNode):
        CustomUIScreenProxy.__init__(self, screenName, screenNode)
        self.config = CommonConfig()

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


# 监听客户端mod加载完成读取饰品文件
@Listen(Events.OnLocalPlayerStopLoading)
def OnLoadClientAddonScriptsAfter(data):
    comp = clientApi.GetEngineCompFactory().CreateConfigClient(levelId)
    configData = comp.GetConfigData(CommonConfig.PLATINUM_LOCAL_DATA)
    GlobalData.baubleInfo = configData.get(CommonConfig.BAUBLE_SLOT_INFO, {})
    if len(GlobalData.baubleInfo) == 0:
        logging.error("铂: 未找到玩家饰品数据, 或读取失败!!!")
    else:
        logging.info("铂: 读取饰品数据成功")
        for path, bauble in GlobalData.baubleInfo.items():
            if len(bauble) > 0:
                BaubleEquippedBroadcaster(CommonConfig.SLOT_PATH_TO_NAME[path.split("/")[-1]], bauble)


# 监听客户端关闭保存饰品文件
def QuDestroy():
    comp = clientApi.GetEngineCompFactory().CreateConfigClient(levelId)
    configData = comp.GetConfigData(CommonConfig.PLATINUM_LOCAL_DATA)
    configData[CommonConfig.BAUBLE_SLOT_INFO] = GlobalData.baubleInfo
    isSave = comp.SetConfigData(CommonConfig.PLATINUM_LOCAL_DATA, configData)
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
def DelayRun(func, delayTime=0.1, *args):
    comp = clientApi.GetEngineCompFactory().CreateGame(levelId)
    comp.AddTimer(delayTime, func, *args)


# 检测物品槽位
def CheckSlot(itemDict, slotPath):
    if itemDict["newItemName"] in BaubleDict.keys():
        baubleValue = BaubleDict[itemDict["newItemName"]]
        if isinstance(baubleValue, type("")):
            targetSlot = baubleValue
        elif isinstance(baubleValue, type([])):
            targetSlot = baubleValue[0]
        else:
            logging.error("铂: {}饰品配置错误, 请检查Script_Platinum/CommonConfig.py".format(itemDict["newItemName"]))
            return False

        if CommonConfig.SLOT_PATH_TO_NAME[slotPath] == targetSlot:
            return True

    return False


# 玩家右键装备饰品
@AllowCall
def EquipBauble(itemDict, baubleSlot):
    isEquip = False
    if baubleSlot != BaubleEnum.OTHER and baubleSlot != BaubleEnum.HAND:
        baublePath = CommonConfig.NAME_TO_SLOT_PATH[baubleSlot]
        if len(GlobalData.baubleInfo.get(baublePath, {})) == 0:
            GlobalData.baubleInfo[baublePath] = itemDict
            isEquip = True
    elif baubleSlot == BaubleEnum.OTHER:
        baublePath = CommonConfig.NAME_TO_SLOT_PATH[BaubleEnum.OTHER]
        baublePath = "/".join(baublePath.split("/")[:-2])
        baublePathList = [
            baublePath + "/bauble_other_panel_1/bauble_other_btn",
            baublePath + "/bauble_other_panel_2/bauble_other_btn",
            baublePath + "/bauble_other_panel_3/bauble_other_btn",
            baublePath + "/bauble_other_panel_4/bauble_other_btn"
        ]
        for baublePath in baublePathList:
            if len(GlobalData.baubleInfo.get(baublePath, {})) == 0:
                GlobalData.baubleInfo[baublePath] = itemDict
                isEquip = True
                break
    elif baubleSlot == BaubleEnum.HAND:
        baublePath = CommonConfig.NAME_TO_SLOT_PATH[BaubleEnum.HAND]
        baublePath = "/".join(baublePath.split("/")[:-2])
        baublePathList = [
            baublePath + "/bauble_hand_panel_1/bauble_hand_btn",
            baublePath + "/bauble_hand_panel_2/bauble_hand_btn"
        ]
        for baublePath in baublePathList:
            if len(GlobalData.baubleInfo.get(baublePath, {})) == 0:
                GlobalData.baubleInfo[baublePath] = itemDict
                isEquip = True
                break
    if isEquip:
        # 广播装备饰品
        BaubleEquippedBroadcaster(baubleSlot, itemDict)
        # 移除玩家手上物品
        Call("RemoveItem", {"playerId": clientApi.GetLocalPlayerId()})


@EasyScreenNodeCls.Binding(CommonConfig.UI_DEF_MAIN)
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
            itemInfoBg = GlobalData.uiNode.GetBaseUIControl(BaublePath.itemInfoBgPath).asImage()
            itemInfoBg.SetAlpha(GlobalData.itemInfoAlpha)
        except:
            pass

    # 打开按钮点击回调
    def OnOpenBtnClick(self):
        self.SetAllResponse(False)

        baublePath = BaublePath
        swallowInputPanel = self.GetBaseUIControl(baublePath.swallowInputPanel).asInputPanel()
        swallowInputPanel.SetVisible(True)
        swallowInputPanel.SetIsModal(True)

        DelayRun(self.GetBagInfoAndRender)
        for baubleSlotPath, itemDict in GlobalData.baubleInfo.items():
            DelayRun(self.RenderBaubleUi, 0.1, baubleSlotPath, itemDict)

    # 关闭按钮点击回调
    @EasyScreenNodeCls.OnClick(BaublePath.closeBtnPath)
    def OnCloseBtnClick(self):
        self.SetAllResponse(True)
        baublePath = BaublePath
        swallowInputPanel = self.GetBaseUIControl(baublePath.swallowInputPanel).asInputPanel()
        swallowInputPanel.SetVisible(False)
        swallowInputPanel.SetIsModal(False)

        # 重置临时变量
        GlobalData.slotSelect = -1
        GlobalData.baubleSlotSelect = -1
        GlobalData.itemInfoAlpha = 0.0

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
            btnPath = targetBaublePath + panelPath + btnPath
            baubleBtn = self.GetBaseUIControl(btnPath).asButton()

            # 注册路径对应槽位
            if CommonConfig.SLOT_PATH_TO_NAME.get(btnPath, None) is None:
                CommonConfig.SLOT_PATH_TO_NAME[btnPath] = Path2SlotName(btnPath)
                CommonConfig.NAME_TO_SLOT_PATH[Path2SlotName(btnPath)] = btnPath

            baubleBtn.AddTouchEventParams({"isSwallow": True})
            baubleBtn.SetButtonTouchUpCallback(self.OnBaubleSlotClick)

        # 清除初始路径键值
        for key in CommonConfig.SLOT_PATH_TO_NAME.keys():
            if not key.startswith("/"):
                CommonConfig.SLOT_PATH_TO_NAME.pop(key)

    # 饰品栏槽位点击回调
    def OnBaubleSlotClick(self, data):
        path = data["ButtonPath"]
        itemSelected = self.GetBaseUIControl(path + "/item_selected_img").asImage()

        itemInfo = GlobalData.baubleInfo.get(path, None)
        # 显示物品信息
        if itemInfo and len(itemInfo) > 0:
            itemName = GlobalData.baubleInfo[path]["newItemName"]
            customTips = GlobalData.baubleInfo[path]["customTips"]
            comp = clientApi.GetEngineCompFactory().CreateItem(levelId)
            itemName = comp.GetItemBasicInfo(itemName)["itemName"]

            showText = itemName if len(customTips) == 0 else customTips
            self.ShowInfo(showText)

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
            # 判断是否能够装备
            if CheckSlot(GlobalData.bagInfo[GlobalData.slotSelect], path):
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
                # 广播卸下饰品
                BaubleUnequippedBroadcaster(CommonConfig.SLOT_PATH_TO_NAME[toSlot], oldBaubleItem)
            else:
                # 移除玩家物品
                Call("RemoveItem", {"playerId": clientApi.GetLocalPlayerId(), "slot": fromSlot})
            DelayRun(self.GetBagInfoAndRender)
            # 饰品栏信息
            GlobalData.baubleInfo[toSlot] = baubleItem
            # 广播装备饰品
            BaubleEquippedBroadcaster(CommonConfig.SLOT_PATH_TO_NAME[toSlot], baubleItem)
            # 饰品栏渲染
            self.RenderBaubleUi(toSlot, baubleItem)

        # 饰品栏到物品栏
        elif isinstance(fromSlot, type("")) and isinstance(toSlot, type(1)):
            baubleItem = GlobalData.baubleInfo[fromSlot]
            bagItem = GlobalData.bagInfo[toSlot]
            needRenderItem = {}
            if bagItem and len(bagItem) > 0:
                # 移除玩家物品
                Call("RemoveItem", {"playerId": clientApi.GetLocalPlayerId(), "slot": toSlot})
                needRenderItem = bagItem
                # 广播装备饰品
                BaubleEquippedBroadcaster(CommonConfig.SLOT_PATH_TO_NAME[fromSlot], bagItem)
            # 添加玩家物品
            Call("AddItem", {"playerId": clientApi.GetLocalPlayerId(), "slot": toSlot, "itemDict": baubleItem})
            DelayRun(self.GetBagInfoAndRender)
            # 饰品栏信息
            GlobalData.baubleInfo[fromSlot] = needRenderItem
            # 广播卸下饰品
            BaubleUnequippedBroadcaster(CommonConfig.SLOT_PATH_TO_NAME[fromSlot], baubleItem)
            # 饰品栏渲染
            self.RenderBaubleUi(fromSlot, needRenderItem)

        # 饰品栏到饰品栏
        elif isinstance(fromSlot, type("")) and isinstance(toSlot, type("")):
            fromItem = GlobalData.baubleInfo[fromSlot]
            toItem = GlobalData.baubleInfo.get(toSlot, {})
            # 饰品栏信息
            GlobalData.baubleInfo[fromSlot] = toItem
            GlobalData.baubleInfo[toSlot] = fromItem
            # 饰品栏渲染
            self.RenderBaubleUi(fromSlot, toItem)
            self.RenderBaubleUi(toSlot, fromItem)

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
        itemInfoText = self.GetBaseUIControl(BaublePath.itemInfoTextPath).asLabel()
        itemInfoText.SetText(info)
        GlobalData.itemInfoAlpha = 2.5


def Path2SlotName(path):
    slotName = CommonConfig.SLOT_PATH_TO_NAME[path.split("/")[-1]]
    return slotName
