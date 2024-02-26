# coding=utf-8
from ..QuModLibs.Client import *
from ..QuModLibs.UI import *

from .. import loggingUtils as logging
from ..commonConfig import BaubleEnum

import re

CustomUIScreenProxy = clientApi.GetUIScreenProxyCls()


class FlyingItemRenderer:

    def __init__(self, screen, basePath):
        self.flyingTime = 5  # 帧

        self.screen = screen
        self.basePath = basePath

        self.flyingItemPanel = self.screen.GetBaseUIControl(self.basePath)

        self.flyingPool = []
        self.flyingUsing = []

        self.flyingBigPool = []
        self.flyingBigUsing = []

    def OnDestroy(self):
        for flyingRender in self.flyingPool:
            self.screen.RemoveChildControl(flyingRender)
        for flyingRender in self.flyingBigPool:
            self.screen.RemoveChildControl(flyingRender)

    def __CreateFlying(self):
        count = len(self.flyingPool)
        flyingItem = self.screen.CreateChildControl(BaubleConfig.UI_DEF_NEW_FLYING, "flying_item{}".format(count),
                                                    self.flyingItemPanel).asItemRenderer()
        flyingItem.SetVisible(False)
        flyingItem.SetAnchorFrom("top_left")
        flyingItem.SetAnchorTo("top_left")
        self.flyingPool.append(flyingItem)
        return flyingItem

    def __CreateFlyingBig(self):
        count = len(self.flyingBigPool)
        flyingItem = self.screen.CreateChildControl(BaubleConfig.UI_DEF_NEW_FLYING_BIG,
                                                    "flying_item_big{}".format(count),
                                                    self.flyingItemPanel).asItemRenderer()
        flyingItem.SetVisible(False)
        flyingItem.SetAnchorFrom("top_left")
        flyingItem.SetAnchorTo("top_left")
        self.flyingBigPool.append(flyingItem)
        return flyingItem

    def FlyingItem(self, itemDict, fromPos, toPos):
        itemRender = None
        isNew = False
        for flyingRender in self.flyingPool:
            if flyingRender not in self.flyingUsing:
                itemRender = flyingRender
                break

        if not itemRender:
            itemRender = self.__CreateFlying()
            isNew = True

        self.flyingUsing.append(itemRender)
        itemRender.SetUiItem(itemDict["newItemName"], itemDict["newAuxValue"], False, itemDict.get("userData"))
        self.__StartFlying(itemRender, fromPos, toPos, "normal", isNew)

    def FlyingItemBig(self, itemDict, fromPos, toPos):
        itemRender = None
        isNew = False
        for flyingRender in self.flyingBigPool:
            if flyingRender not in self.flyingBigUsing:
                itemRender = flyingRender
                break

        if not itemRender:
            itemRender = self.__CreateFlyingBig()
            isNew = True

        self.flyingBigUsing.append(itemRender)
        itemRender.SetUiItem(itemDict["newItemName"], itemDict["newAuxValue"], False, itemDict.get("userData"))
        self.__StartFlying(itemRender, fromPos, toPos, "big", isNew)

    def __StartFlying(self, itemRender, fromPos, toPos, size, isNew):
        flyingPanelOffset = self.flyingItemPanel.GetGlobalPosition()
        fromPos = [fromPos[0] - flyingPanelOffset[0], fromPos[1] - flyingPanelOffset[1]]
        toPos = [toPos[0] - flyingPanelOffset[0], toPos[1] - flyingPanelOffset[1]]

        offsetAnimateData = {
            "namespace": "PlatinumFlyingItem",
            "flying_animation": {
                "anim_type": "offset",
                "duration": self.flyingTime / 30.0,
                "from": fromPos,
                "to": toPos
            }
        }
        clientApi.RegisterUIAnimations(offsetAnimateData, True)
        if not isNew:
            itemRender.RemoveAnimation("offset")
        itemRender.SetVisible(True)
        itemRender.SetAnimation("offset", "PlatinumFlyingItem", "flying_animation", True)

        comp = clientApi.GetEngineCompFactory().CreateGame(levelId)
        comp.AddTimer(self.flyingTime / 30.0, self.__EndFlying, itemRender, size)

    def __EndFlying(self, itemRender, size):
        itemRender.SetVisible(False)
        try:
            if size == "normal":
                self.flyingUsing.remove(itemRender)
            else:
                self.flyingBigUsing.remove(itemRender)
        except:
            pass


class InfoManager(object):

    def __init__(self, screen, basePath):
        self.screen = screen
        self.basePath = basePath

        self.flyingItemPanel = self.screen.GetBaseUIControl(self.basePath)
        self.hasPanel = False

        self.infoAlpha = 0.0

    def ShowInfo(self, info):

        def SetText():
            try:
                infoPanel = self.screen.GetBaseUIControl(self.basePath + "/info_bg").asImage()
                infoPanel.SetAlpha(2.0)
                self.infoAlpha = 2.0

                infoLabel = self.screen.GetBaseUIControl(self.basePath + "/info_bg/info").asLabel()
                infoLabel.SetText(info)
            except:
                logging.error("铂: 无法找到特定界面 信息界面")

        if self.hasPanel:
            SetText()
        else:
            self.screen.CreateChildControl(BaubleConfig.UI_DEF_NEW_INFO, "info_bg", self.flyingItemPanel)
            self.hasPanel = True
            ListenForEvent("OnScriptTickClient", self, self.OnTick)
            SetText()

    def OnTick(self):
        if self.infoAlpha > 0:
            self.infoAlpha -= 0.05
            infoPanel = self.screen.GetBaseUIControl(self.basePath + "/info_bg").asImage()
            infoPanel.SetAlpha(self.infoAlpha)

    def OnDestroy(self):
        if self.hasPanel:
            self.screen.RemoveChildControl(self.screen.GetBaseUIControl(self.basePath + "/info_bg"))
            UnListenForEvent("OnScriptTickClient", self, self.OnTick)


class BaubleConfig(object):
    PLATINUM_LOCAL_DATA = "platinum_local_data"
    BAUBLE_SLOT_INFO = "bauble_slot_info"
    BAUBLE_BTN_POSITION = "bauble_btn_position"

    UI_DEF = "bauble_base_panel"
    UI_DEF_MAIN = "bauble_base_panel.main"
    UI_DEF_BAUBLE_BTN = "bauble_base_panel.bauble_button"
    UI_DEF_BAUBLE_BTN_BIG = "bauble_base_panel.bauble_btn_big"

    UI_DEF_NEW = "bauble_new"
    UI_DEF_NEW_MAIN = "bauble_new.main"
    UI_DEF_NEW_BAUBLE_CLASSIC = "bauble_new.bauble_classic_new"
    UI_DEF_NEW_BAUBLE_POCKET = "bauble_new.bauble_pocket"
    UI_DEF_NEW_BAUBLE_TRANS_BTN = "bauble_new.transparent_btn"

    UI_DEF_NEW_FLYING = "bauble_new.flying_item"
    UI_DEF_NEW_FLYING_BIG = "bauble_new.flying_item_big"

    UI_DEF_NEW_INFO = "bauble_new.info"

    # 饰品路径对应饰品表
    SlotName2TypeDict = {
        "helmet": BaubleEnum.HELMET,
        "necklace": BaubleEnum.NECKLACE,
        "armor": BaubleEnum.ARMOR,
        "back": BaubleEnum.BACK,
        "hand_1": BaubleEnum.HAND,
        "hand_2": BaubleEnum.HAND,
        "belt": BaubleEnum.BELT,
        "shoes": BaubleEnum.SHOES,
        "other_1": BaubleEnum.OTHER,
        "other_2": BaubleEnum.OTHER,
        "other_3": BaubleEnum.OTHER,
        "other_4": BaubleEnum.OTHER
    }


class GlobalData(object):
    uiProfile = clientApi.GetEngineCompFactory().CreatePlayerView(levelId).GetUIProfile()

    uiPosition = "left_top"

    # 玩家饰品字典
    baubleDict = {
        "helmet": {},
        "necklace": {},
        "armor": {},
        "back": {},
        "hand_1": {},
        "hand_2": {},
        "belt": {},
        "shoes": {},
        "other_1": {},
        "other_2": {},
        "other_3": {},
        "other_4": {}
    }


@AllowCall
def ChangeUiPosition(uiPosition):
    GlobalData.uiPosition = uiPosition
    OnUiInitFinished(None)
    SavePosition()


def SavePosition():
    comp = clientApi.GetEngineCompFactory().CreateConfigClient(levelId)
    configData = comp.GetConfigData(BaubleConfig.PLATINUM_LOCAL_DATA + "_{}".format(playerId))
    configData[BaubleConfig.BAUBLE_BTN_POSITION] = GlobalData.uiPosition
    comp.SetConfigData(BaubleConfig.PLATINUM_LOCAL_DATA + "_{}".format(playerId), configData)


# 背包经典界面代理类
class InventoryClassicProxy(CustomUIScreenProxy):
    def __init__(self, screenName, screenNode):
        CustomUIScreenProxy.__init__(self, screenName, screenNode)
        # 临时变量
        self.baubleSelect = ""
        self.invSelect = -1
        self.invInfo = {}
        self.isTouch = False

        self.oldSelect = -1  # 记录操作 非实际选择

        # 饰品栏打开状态
        self.openState = False
        self.InvPage = 0

        # 原版路径
        self.invCenterPath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/content_stack_panel/player_inventory"
        self.toolBarPath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/content_stack_panel/toolbar_anchor"
        self.playerRenderBgPath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/content_stack_panel/player_inventory/inventory_panel_top_half/player_armor_panel/player_bg"
        self.flyingPanel = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/flying_item_renderer"
        self.invGridPathModel = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/content_stack_panel/player_inventory/inventory_panel_bottom_half/inventory_panel/inventory_grid/grid_item_for_inventory{}"
        self.hotBarGridPathModel = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/content_stack_panel/player_inventory/hotbar_grid/grid_item_for_hotbar{}"

        # 基础路径
        self.baublePath = ""
        self.baubleScrollerPath = self.baublePath + "/bg_img/bauble_scroll_view"
        self.scrollerContentPCPath = self.baubleScrollerPath + "/scroll_mouse/scroll_view/stack_panel/background_and_viewport/scrolling_view_port/scrolling_content"
        self.scrollerContentPEPath = self.baubleScrollerPath + "/scroll_touch/scroll_view/panel/background_and_viewport/scrolling_view_port/scrolling_content"

        # 饰品栏路径
        self.helmetBtnBasePath = "/bauble_helmet_panel/bauble_helmet_btn"
        self.necklaceBtnBasePath = "/bauble_necklace_panel/bauble_necklace_btn"
        self.armorBtnBasePath = "/bauble_armor_panel/bauble_armor_btn"
        self.backBtnBasePath = "/bauble_back_panel/bauble_back_btn"
        self.handBtnBasePath1 = "/bauble_hand_panel_1/bauble_hand_btn"
        self.handBtnBasePath2 = "/bauble_hand_panel_2/bauble_hand_btn"
        self.beltBtnBasePath = "/bauble_belt_panel/bauble_belt_btn"
        self.shoesBtnBasePath = "/bauble_shoes_panel/bauble_shoes_btn"
        self.otherBtnBasePath1 = "/bauble_other_panel_1/bauble_other_btn"
        self.otherBtnBasePath2 = "/bauble_other_panel_2/bauble_other_btn"
        self.otherBtnBasePath3 = "/bauble_other_panel_3/bauble_other_btn"
        self.otherBtnBasePath4 = "/bauble_other_panel_4/bauble_other_btn"

        # 渲染器路径
        self.itemRenderBasePath = "/item_renderer"
        self.itemSelectedBasePath = "/item_selected_img"
        self.durabilityBgBasePath = self.itemRenderBasePath + "/durability_base_img"
        self.durabilityBasePath = self.itemRenderBasePath + "/durability_img"
        self.itemCountBasePath = self.itemRenderBasePath + "/item_count"

        # 饰品按钮列表
        self.baubleBtnList = [
            self.helmetBtnBasePath,
            self.necklaceBtnBasePath,
            self.armorBtnBasePath,
            self.backBtnBasePath,
            self.handBtnBasePath1,
            self.handBtnBasePath2,
            self.beltBtnBasePath,
            self.shoesBtnBasePath,
            self.otherBtnBasePath1,
            self.otherBtnBasePath2,
            self.otherBtnBasePath3,
            self.otherBtnBasePath4
        ]

        self.flyingUtils = FlyingItemRenderer(self.GetScreenNode(), self.flyingPanel)
        self.infoManager = InfoManager(self.GetScreenNode(), self.flyingPanel)

    def OnCreate(self):
        self.CreateBaubleBtn()

    def OnDestroy(self):
        screen = self.GetScreenNode()
        if self.openState:
            self.CloseBaublePanel()

        self.flyingUtils.OnDestroy()
        self.infoManager.OnDestroy()

        try:
            bauble = screen.GetBaseUIControl(self.baublePath)
            screen.RemoveChildControl(bauble)
        except:
            pass

    def OnTick(self):
        # 切换界面隐藏饰品栏
        screen = self.GetScreenNode()
        recipePath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/content_stack_panel/recipe_book"
        recipePanel = screen.GetBaseUIControl(recipePath)

        invPath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/content_stack_panel/toolbar_anchor/toolbar_panel/toolbar_background/toolbar_stack_panel/survival_layout_toggle_panel/survival_layout_toggle/this_toggle/checked"
        invBtn = screen.GetBaseUIControl(invPath)
        invCheck = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/content_stack_panel/toolbar_anchor/toolbar_panel/toolbar_background/toolbar_stack_panel/survival_layout_toggle_panel/survival_layout_toggle/this_toggle/checked_hover"
        invBtnCheck = screen.GetBaseUIControl(invCheck)

        # 非纯背包界面
        if recipePanel and recipePanel.GetVisible() and self.InvPage != 2:
            self.InvPage = 2
            if self.openState:
                self.ResetBaublePanelPosition()
        elif ((invBtn and invBtn.GetVisible()) or (invBtnCheck and invBtnCheck.GetVisible())) and self.InvPage != 1:
            self.InvPage = 1
            if self.openState:
                self.ResetBaublePanelPosition()

    # 设置提示
    def SetInfo(self, info):
        self.infoManager.ShowInfo(info)

    def ResetBaublePanelPosition(self):
        screen = self.GetScreenNode()
        panelPath = self.invCenterPath
        baublePanel = screen.GetBaseUIControl(panelPath + "/bauble_classic_new")
        baublePanel = baublePanel if baublePanel else screen.CreateChildControl(BaubleConfig.UI_DEF_NEW_BAUBLE_CLASSIC,
                                                                                "bauble_classic_new", panelPath)
        if baublePanel:
            if self.InvPage == 1:
                baublePanel.SetAnchorFrom("left_middle")
                baublePanel.SetAnchorTo("right_middle")
            else:
                baublePanel.SetAnchorFrom("right_middle")
                baublePanel.SetAnchorTo("left_middle")

    # 创建饰品栏开关按钮
    def CreateBaubleBtn(self):
        screen = self.GetScreenNode()
        panelPath = self.playerRenderBgPath
        panel = screen.GetBaseUIControl(panelPath)
        if not panel:
            logging.error("铂: 无法找到特定界面")
            return
        try:
            baubleBtn = screen.GetBaseUIControl(panelPath + "/bauble_button").asButton()
        except:
            baubleBtn = screen.CreateChildControl(BaubleConfig.UI_DEF_BAUBLE_BTN, "bauble_button", panel).asButton()

        self.SetBtnPosition(baubleBtn)
        baubleBtn.AddTouchEventParams({"isSwallow": True})
        baubleBtn.SetButtonTouchUpCallback(self.OnBaubleButtonClicked)

    def SetBtnPosition(self, btn):
        position = GlobalData.uiPosition
        if position == "left_top":
            btn.SetFullPosition(axis="x", paramDict={"followType": "parent", "relativeValue": -0.35})
            btn.SetFullPosition(axis="y", paramDict={"followType": "parent", "relativeValue": -0.4})
        elif position == "right_top":
            btn.SetFullPosition(axis="x", paramDict={"followType": "parent", "relativeValue": 0.35})
            btn.SetFullPosition(axis="y", paramDict={"followType": "parent", "relativeValue": -0.4})
        elif position == "left_bottom":
            btn.SetFullPosition(axis="x", paramDict={"followType": "parent", "relativeValue": -0.35})
            btn.SetFullPosition(axis="y", paramDict={"followType": "parent", "relativeValue": 0.4})
        elif position == "right_bottom":
            btn.SetFullPosition(axis="x", paramDict={"followType": "parent", "relativeValue": 0.35})
            btn.SetFullPosition(axis="y", paramDict={"followType": "parent", "relativeValue": 0.4})

    # 饰品栏开关按钮回调
    def OnBaubleButtonClicked(self, args):
        if not self.openState:
            self.OpenBaublePanel()
        else:
            self.CloseBaublePanel()

    # 打开饰品栏
    def OpenBaublePanel(self):
        screen = self.GetScreenNode()
        panelPath = self.invCenterPath
        panel = screen.GetBaseUIControl(panelPath)

        if panel:
            try:
                baublePanel = screen.GetBaseUIControl(panelPath + "/bauble_classic_new")
                baublePanel.SetVisible(True)
            except:
                screen.CreateChildControl(BaubleConfig.UI_DEF_NEW_BAUBLE_CLASSIC, "bauble_classic_new", panel)
                self.baublePath = panelPath + "/bauble_classic_new"
                self.InitBaublePanel()
            self.ResetBaublePanelPosition()
        self.openState = True

        ListenForEvent("OnItemSlotButtonClickedEvent", self, self.OnItemSlotButtonClickedEvent)

    # 关闭饰品栏
    def CloseBaublePanel(self):
        screen = self.GetScreenNode()
        panelPath = self.invCenterPath
        panel = screen.GetBaseUIControl(panelPath)

        if panel:
            try:
                baublePanel = screen.GetBaseUIControl(panelPath + "/bauble_classic_new")
                baublePanel.SetVisible(False)
            except:
                pass

        self.openState = False
        self.SelectBauble()
        self.invSelect = -1

    # 注册饰品栏位按钮回调
    def InitBaublePanel(self):
        screen = self.GetScreenNode()
        # 检查操作方式
        scrollerPath = self.baublePath + self.scrollerContentPCPath
        if not screen.GetBaseUIControl(scrollerPath):
            self.isTouch = True
            scrollerPath = self.baublePath + self.scrollerContentPEPath
        # 饰品栏位按钮注册
        for btnPath in self.baubleBtnList:
            try:
                btn = screen.GetBaseUIControl(scrollerPath + btnPath).asButton()
                btn.AddTouchEventParams({"isSwallow": False})
                btn.SetButtonTouchUpCallback(self.OnBaubleClicked)
                self.RenderBauble(scrollerPath + btnPath)
            except Exception as e:
                logging.error("铂: 饰品栏位按钮回调注册失败: {}".format(e))

    # 饰品栏位按钮回调
    def OnBaubleClicked(self, args):
        btnPath = args["ButtonPath"]

        # if self.invSelect != -1:
        #     self.SetInfo("请先选择饰品槽位来进行穿戴/脱下操作")
        #     return

        if len(self.baubleSelect) == 0:
            # 选中饰品
            self.SelectBauble(btnPath)
        elif self.baubleSelect == btnPath:
            self.SelectBauble()
        else:
            # 交换饰品
            baubleFrom = GlobalData.baubleDict[GetSlotNameByPath(self.baubleSelect)]
            baubleTo = GlobalData.baubleDict[GetSlotNameByPath(btnPath)]

            try:
                baubleIndexFrom = int(re.findall(r"\d+", self.baubleSelect)[-1])
                baubleIndexTo = int(re.findall(r"\d+", btnPath)[-1])
            except:
                baubleIndexTo = 0
                baubleIndexFrom = 0

            if len(baubleFrom) != 0 or len(baubleTo) != 0:
                def changePos(isSuccess):
                    if isSuccess:
                        GlobalData.baubleDict[GetSlotNameByPath(self.baubleSelect)] = baubleTo
                        GlobalData.baubleDict[GetSlotNameByPath(btnPath)] = baubleFrom
                        self.RenderBauble(self.baubleSelect)
                        self.RenderBauble(btnPath)
                        baubleTypeFrom = BaubleConfig.SlotName2TypeDict[GetSlotNameByPath(self.baubleSelect)]
                        baubleTypeTo = BaubleConfig.SlotName2TypeDict[GetSlotNameByPath(btnPath)]
                        # 发送脱下饰品事件
                        if len(baubleFrom) != 0:
                            if baubleTypeFrom == BaubleEnum.HAND or baubleTypeFrom == BaubleEnum.OTHER:
                                BaubleUnequippedBroadcaster(baubleTypeFrom, baubleFrom, baubleIndexFrom)
                            else:
                                BaubleUnequippedBroadcaster(baubleTypeFrom, baubleFrom)
                        if len(baubleTo) != 0:
                            if baubleTypeTo == BaubleEnum.HAND or baubleTypeTo == BaubleEnum.OTHER:
                                BaubleUnequippedBroadcaster(baubleTypeTo, baubleTo, baubleIndexTo)
                            else:
                                BaubleUnequippedBroadcaster(baubleTypeTo, baubleTo)
                        # 发送穿戴饰品事件
                        if len(baubleTo) != 0:
                            if baubleTypeFrom == BaubleEnum.HAND or baubleTypeFrom == BaubleEnum.OTHER:
                                BaubleEquippedBroadcaster(baubleTypeFrom, baubleTo, baubleIndexFrom)
                            else:
                                BaubleEquippedBroadcaster(baubleTypeFrom, baubleTo)
                        if len(baubleFrom) != 0:
                            if baubleTypeTo == BaubleEnum.HAND or baubleTypeTo == BaubleEnum.OTHER:
                                BaubleEquippedBroadcaster(baubleTypeTo, baubleFrom, baubleIndexTo)
                            else:
                                BaubleEquippedBroadcaster(baubleTypeTo, baubleFrom)
                    self.SelectBauble()

                if len(baubleFrom) != 0 and len(baubleTo) != 0:
                    baubleSlotFrom = BaubleConfig.SlotName2TypeDict[GetSlotNameByPath(self.baubleSelect)]
                    baubleSlotTo = BaubleConfig.SlotName2TypeDict[GetSlotNameByPath(btnPath)]

                    def OnCheck(isSuccess):
                        if isSuccess:
                            Request("CheckBauble", (baubleTo, baubleSlotTo), OnResponse=changePos)

                    Request("CheckBauble", (baubleFrom, baubleSlotFrom), OnResponse=OnCheck)
                elif len(baubleFrom) != 0:
                    baubleSlot = BaubleConfig.SlotName2TypeDict[GetSlotNameByPath(btnPath)]
                    Request("CheckBauble", (baubleFrom, baubleSlot), OnResponse=changePos)
                else:
                    baubleSlot = BaubleConfig.SlotName2TypeDict[GetSlotNameByPath(self.baubleSelect)]
                    Request("CheckBauble", (baubleTo, baubleSlot), OnResponse=changePos)

    # 物品栏位按钮回调
    def OnItemSlotButtonClickedEvent(self, data):
        slotId = data["slotIndex"]
        # 非背包返回
        if slotId not in range(0, 36):
            return
        # 选中饰品栏
        if len(self.baubleSelect) != 0:
            self.invSelect = slotId
            comp = clientApi.GetEngineCompFactory().CreateItem(playerId)
            itemDict = comp.GetPlayerItem(clientApi.GetMinecraftEnum().ItemPosType.INVENTORY, slotId, True)
            self.invInfo = itemDict

            # 先移除物品
            Call("RemoveItem", {"playerId": playerId, "slot": slotId})
            # 穿戴饰品
            if itemDict:
                def OnCheck(isSuccess):
                    if isSuccess:
                        self.SwapBauble()
                    else:
                        # 如无法穿戴则返回物品
                        Call("AddItem", {"playerId": playerId, "itemDict": itemDict, "slot": slotId})
                        self.SelectBauble()

                baubleSlot = BaubleConfig.SlotName2TypeDict[GetSlotNameByPath(self.baubleSelect)]
                Request("CheckBauble", (self.invInfo, baubleSlot), OnResponse=OnCheck)
            # 脱下饰品
            elif len(GlobalData.baubleDict[GetSlotNameByPath(self.baubleSelect)]) > 0:
                itemDict = comp.GetPlayerItem(clientApi.GetMinecraftEnum().ItemPosType.INVENTORY, self.oldSelect, True)
                if not itemDict:
                    self.SwapBauble()
                else:
                    self.SelectBauble()
        self.oldSelect = slotId

    # 渲染选中状态
    def SelectBauble(self, baublePath=""):
        lastSelect = self.baubleSelect
        self.baubleSelect = baublePath
        screen = self.GetScreenNode()
        selectPath = baublePath + self.itemSelectedBasePath
        lastSelectPath = lastSelect + self.itemSelectedBasePath
        try:
            if len(baublePath) > 0:
                selectImg = screen.GetBaseUIControl(selectPath).asImage()
                selectImg.SetVisible(True)
            if len(lastSelect) > 0:
                lastSelectImg = screen.GetBaseUIControl(lastSelectPath).asImage()
                lastSelectImg.SetVisible(False)
        except:
            logging.error("铂: 饰品栏位选中器获取失败 {}".format(baublePath.split("/")[-2]))
            return

    # 穿戴或脱下饰品
    def SwapBauble(self):
        baublePath = self.baubleSelect
        itemDict = self.invInfo
        try:
            baubleIndex = int(re.findall(r"\d+", baublePath)[-1])
        except:
            baubleIndex = 0
        # 穿戴或交换
        if itemDict and len(itemDict) > 0:
            slotType = BaubleConfig.SlotName2TypeDict[GetSlotNameByPath(baublePath)]
            originBauble = GlobalData.baubleDict[GetSlotNameByPath(baublePath)]
            # 飞行动画
            self.FlyingItem(itemDict, self.GetInvPathBySlotId(self.invSelect), baublePath)
            # 发送脱下饰品事件
            if len(originBauble) != 0:
                if slotType == BaubleEnum.HAND or slotType == BaubleEnum.OTHER:
                    BaubleUnequippedBroadcaster(slotType, originBauble, baubleIndex)
                else:
                    BaubleUnequippedBroadcaster(slotType, originBauble)
                Call("AddItem", {"playerId": playerId, "itemDict": originBauble, "slot": self.invSelect})
                # 飞行动画
                self.FlyingItem(originBauble, baublePath, self.GetInvPathBySlotId(self.invSelect))
            else:
                Call("RemoveItem", {"playerId": playerId, "slot": self.invSelect})

            GlobalData.baubleDict[GetSlotNameByPath(baublePath)] = itemDict
            # 发送穿戴饰品事件
            if slotType == BaubleEnum.HAND or slotType == BaubleEnum.OTHER:
                BaubleEquippedBroadcaster(slotType, itemDict, baubleIndex)
            else:
                BaubleEquippedBroadcaster(slotType, itemDict)
        else:
            originBauble = GlobalData.baubleDict[GetSlotNameByPath(baublePath)]
            slotType = BaubleConfig.SlotName2TypeDict[GetSlotNameByPath(baublePath)]
            # 发送脱下饰品事件
            if len(originBauble) != 0:
                GlobalData.baubleDict[GetSlotNameByPath(baublePath)] = {}
                if slotType == BaubleEnum.HAND or slotType == BaubleEnum.OTHER:
                    BaubleUnequippedBroadcaster(slotType, originBauble, baubleIndex)
                else:
                    BaubleUnequippedBroadcaster(slotType, originBauble)
                DelayRun(Call, 0.1, "AddItem", {"playerId": playerId, "itemDict": originBauble, "slot": self.invSelect})
            # 飞行动画
            self.FlyingItem(originBauble, baublePath, self.GetInvPathBySlotId(self.invSelect))

        self.RenderBauble(self.baubleSelect)
        self.SelectBauble()

    # 渲染饰品栏
    def RenderBauble(self, baublePath):
        screen = self.GetScreenNode()
        itemDict = GlobalData.baubleDict[GetSlotNameByPath(baublePath)]

        baubleImgPath = "/".join(baublePath.split("/")[0:-1]) + "/" + baublePath.split("/")[-1].replace("btn", "img")
        itemRendererPath = baublePath + self.itemRenderBasePath
        try:
            baubleImg = screen.GetBaseUIControl(baubleImgPath).asImage()
            itemRenderer = screen.GetBaseUIControl(itemRendererPath).asItemRenderer()

            # 穿戴或交换
            if itemDict and len(itemDict) > 0:
                baubleImg.SetVisible(False)
                itemRenderer.SetVisible(True)

                isEnchanted = itemDict.get("enchantData") and len(itemDict.get("enchantData")) > 0
                itemRenderer.SetUiItem(itemDict["newItemName"], itemDict["newAuxValue"], isEnchanted,
                                       itemDict.get("userData"))
                # 耐久显示
                durabilityRatio = self.CalculateDurabilityRatio(itemDict)
                durabilityBg = screen.GetBaseUIControl(baublePath + self.durabilityBgBasePath).asImage()
                durabilityBg.SetVisible(durabilityRatio < 1)

                if durabilityRatio < 1:
                    durationMusk = screen.GetBaseUIControl(baublePath + self.durabilityBasePath).asImage()
                    durationMusk.SetVisible(True)
                    durationMusk.SetSpriteClipRatio(1 - durabilityRatio)
                    durationMusk.SetSpriteColor((1 - durabilityRatio, durabilityRatio, 0))
            # 脱下
            else:
                baubleImg.SetVisible(True)
                itemRenderer.SetVisible(False)
                durabilityBg = screen.GetBaseUIControl(baublePath + self.durabilityBgBasePath)
                durabilityBg.SetVisible(False)
                durationMusk = screen.GetBaseUIControl(baublePath + self.durabilityBasePath)
                durationMusk.SetVisible(False)

        except Exception as e:
            logging.error("铂: 饰品栏位渲染器获取失败 {}, 错误: {}".format(baublePath.split("/")[-2], e))
            return

    # 飞行动画
    def FlyingItem(self, itemDict, fromPath, toPath):
        try:
            fromControl = self.GetScreenNode().GetBaseUIControl(fromPath)
            toControl = self.GetScreenNode().GetBaseUIControl(toPath)
            fromPos = fromControl.GetGlobalPosition()
            toPos = toControl.GetGlobalPosition()
            self.flyingUtils.FlyingItem(itemDict, fromPos, toPos)
        except Exception as e:
            logging.error("铂: 飞行动画获取位置失败 {}".format(e))

    def GetInvPathBySlotId(self, slotId):
        slotId += 1
        if slotId < 9:
            return self.hotBarGridPathModel.format(slotId)
        return self.invGridPathModel.format(slotId - 9)

    @staticmethod
    def CalculateDurabilityRatio(itemDict):
        # 计算耐久度比例，用于显示耐久度槽
        itemComp = clientApi.GetEngineCompFactory().CreateItem(levelId)
        basicInfo = itemComp.GetItemBasicInfo(itemDict.get("itemName", ""), itemDict.get("auxValue", 0))
        if basicInfo:
            currentDurability = itemDict.get("durability")
            if currentDurability is None:
                return 1.0
            maxDurability = basicInfo.get("maxDurability", 0)
            if maxDurability != 0:
                return currentDurability * 1.0 / maxDurability
        return 1.0


# 背包口袋界面代理类
class InventoryPocketProxy(InventoryClassicProxy):
    def __init__(self, screenName, screenNode):
        InventoryClassicProxy.__init__(self, screenName, screenNode)
        self.openState = False

        # 原版路径
        self.playerRenderBgPath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/root_panel/hotbar_and_panels/gamepad_helper_border/both_panels/right_panel/armor_tab_content/content/equipment_and_renderer/armor_panel/armor_and_player/player_preview_border/player_bg"
        self.armorSetPath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/root_panel/hotbar_and_panels/gamepad_helper_border/both_panels/right_panel/armor_tab_content/content/label_and_renderer"
        self.invGridMousePathModel = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/root_panel/hotbar_and_panels/gamepad_helper_border/both_panels/left_panel/inventory_tab_content/tab_content_search_bar_panel/scroll_pane/scroll_mouse/scroll_view/stack_panel/background_and_viewport/scrolling_view_port/scrolling_content/grid/grid_item_for_inventory{}"
        self.invGridTouchPathModel = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/root_panel/hotbar_and_panels/gamepad_helper_border/both_panels/left_panel/inventory_tab_content/tab_content_search_bar_panel/scroll_pane/scroll_touch/scroll_view/panel/background_and_viewport/scrolling_view_port/scrolling_content/grid/grid_item_for_inventory{}"
        self.hotBarGridPathModel = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/root_panel/hotbar_and_panels/hotbar_section_panel/hotbar/hotbar_grid/hotbar_grid_item{}"
        # 饰品栏路径
        self.helmetBtnBasePath = "/bauble_helmet_panel/bauble_helmet_btn"
        self.necklaceBtnBasePath = "/bauble_necklace_panel/bauble_necklace_btn"
        self.armorBtnBasePath = "/bauble_armor_panel/bauble_armor_btn"
        self.backBtnBasePath = "/bauble_back_panel/bauble_back_btn"
        self.handBtnBasePath1 = "/bauble_hand_panel_1/bauble_hand_btn"
        self.handBtnBasePath2 = "/bauble_hand_panel_2/bauble_hand_btn"
        self.beltBtnBasePath = "/bauble_belt_panel/bauble_belt_btn"
        self.shoesBtnBasePath = "/bauble_shoes_panel/bauble_shoes_btn"
        self.otherBtnBasePath1 = "/bauble_other_panel_1/bauble_other_btn"
        self.otherBtnBasePath2 = "/bauble_other_panel_2/bauble_other_btn"
        self.otherBtnBasePath3 = "/bauble_other_panel_3/bauble_other_btn"
        self.otherBtnBasePath4 = "/bauble_other_panel_4/bauble_other_btn"

        self.upperPanelBasePath = "/bauble_panel_pocket_upper/bauble_panel"
        self.lowerPanelBasePath = "/bauble_panel_pocket_lower/bauble_panel"

        # 渲染器路径
        self.itemRenderBasePath = "/item_renderer"
        self.itemSelectedBasePath = "/item_selected_img"
        self.durabilityBgBasePath = self.itemRenderBasePath + "/durability_base_img"
        self.durabilityBasePath = self.itemRenderBasePath + "/durability_img"
        self.itemCountBasePath = self.itemRenderBasePath + "/item_count"

        # 饰品按钮列表
        self.baubleBtnUpperList = [
            self.helmetBtnBasePath,
            self.necklaceBtnBasePath,
            self.armorBtnBasePath,
            self.backBtnBasePath,
            self.handBtnBasePath1,
            self.handBtnBasePath2
        ]
        self.baubleBtnLowerList = [
            self.beltBtnBasePath,
            self.shoesBtnBasePath,
            self.otherBtnBasePath1,
            self.otherBtnBasePath2,
            self.otherBtnBasePath3,
            self.otherBtnBasePath4
        ]

    def OnDestroy(self):
        screen = self.GetScreenNode()
        if self.openState:
            self.CloseBaublePanel()

        self.flyingUtils.OnDestroy()

        try:
            bauble = screen.GetBaseUIControl(self.baublePath)
            screen.RemoveChildControl(bauble)
        except:
            pass

    def CreateBaubleBtn(self):
        screen = self.GetScreenNode()
        panelPath = self.playerRenderBgPath
        panel = screen.GetBaseUIControl(panelPath)
        if not panel:
            logging.error("铂: 无法找到特定界面")
            return
        try:
            baubleBtn = screen.GetBaseUIControl(panelPath + "/bauble_button").asButton()
            baubleBtn.SetVisible(True)
        except:
            baubleBtn = screen.CreateChildControl(BaubleConfig.UI_DEF_BAUBLE_BTN_BIG, "bauble_button", panel).asButton()

        self.SetBtnPosition(baubleBtn)
        baubleBtn.AddTouchEventParams({"isSwallow": True})
        baubleBtn.SetButtonTouchUpCallback(self.OnBaubleButtonClicked)

    def SetBtnPosition(self, btn):
        position = GlobalData.uiPosition
        if position == "left_top":
            btn.SetFullPosition(axis="x", paramDict={"followType": "parent", "relativeValue": -0.40})
            btn.SetFullPosition(axis="y", paramDict={"followType": "parent", "relativeValue": -0.38})
        elif position == "right_top":
            btn.SetFullPosition(axis="x", paramDict={"followType": "parent", "relativeValue": 0.40})
            btn.SetFullPosition(axis="y", paramDict={"followType": "parent", "relativeValue": -0.38})
        elif position == "left_bottom":
            btn.SetFullPosition(axis="x", paramDict={"followType": "parent", "relativeValue": -0.40})
            btn.SetFullPosition(axis="y", paramDict={"followType": "parent", "relativeValue": 0.38})
        elif position == "right_bottom":
            btn.SetFullPosition(axis="x", paramDict={"followType": "parent", "relativeValue": 0.40})
            btn.SetFullPosition(axis="y", paramDict={"followType": "parent", "relativeValue": 0.38})

    def OpenBaublePanel(self):
        screen = self.GetScreenNode()
        panelPath = self.armorSetPath
        panel = screen.GetBaseUIControl(panelPath)
        armorTextPath = panelPath + "/label_panel"
        rendererPath = panelPath + "/renderer_panel"
        if panel:
            try:
                screen.GetBaseUIControl(armorTextPath).SetVisible(False)
                screen.GetBaseUIControl(rendererPath).SetVisible(False)

                baublePanel = screen.GetBaseUIControl(panelPath + "/bauble_pocket_new")
                baublePanel.SetVisible(True)
            except:
                screen.CreateChildControl(BaubleConfig.UI_DEF_NEW_BAUBLE_POCKET, "bauble_pocket_new", panel)
                self.baublePath = panelPath + "/bauble_pocket_new"
                self.initBaublePanel()

            self.openState = True
            ListenForEvent("OnItemSlotButtonClickedEvent", self, self.OnItemSlotButtonClickedEvent)

    def CloseBaublePanel(self):
        screen = self.GetScreenNode()
        panelPath = self.armorSetPath
        panel = screen.GetBaseUIControl(panelPath)
        armorTextPath = panelPath + "/label_panel"
        rendererPath = panelPath + "/renderer_panel"
        if panel:
            try:
                screen.GetBaseUIControl(armorTextPath).SetVisible(True)
                screen.GetBaseUIControl(rendererPath).SetVisible(True)

                baublePanel = screen.GetBaseUIControl(panelPath + "/bauble_pocket_new")
                baublePanel.SetVisible(False)
            except:
                pass

            self.openState = False

    def initBaublePanel(self):
        screen = self.GetScreenNode()
        baublePanel = screen.GetBaseUIControl(self.baublePath)
        if baublePanel:
            for btnPath in self.baubleBtnUpperList:
                try:
                    upperBtnPath = self.baublePath + self.upperPanelBasePath + btnPath
                    btn = screen.GetBaseUIControl(upperBtnPath).asButton()
                    btn.AddTouchEventParams({"isSwallow": False})
                    btn.SetButtonTouchUpCallback(self.OnBaubleClicked)
                    self.RenderBauble(upperBtnPath)
                except Exception as e:
                    logging.error("铂: 饰品栏位按钮回调注册失败: {}".format(e))
            for btnPath in self.baubleBtnLowerList:
                try:
                    lowerBtnPath = self.baublePath + self.lowerPanelBasePath + btnPath
                    btn = screen.GetBaseUIControl(lowerBtnPath).asButton()
                    btn.AddTouchEventParams({"isSwallow": False})
                    btn.SetButtonTouchUpCallback(self.OnBaubleClicked)
                    self.RenderBauble(lowerBtnPath)
                except Exception as e:
                    logging.error("铂: 饰品栏位按钮回调注册失败: {}".format(e))

    def FlyingItem(self, itemDict, fromPath, toPath):
        try:
            fromControl = self.GetScreenNode().GetBaseUIControl(fromPath)
            toControl = self.GetScreenNode().GetBaseUIControl(toPath)
            fromPos = fromControl.GetGlobalPosition()
            toPos = toControl.GetGlobalPosition()
            self.flyingUtils.FlyingItemBig(itemDict, fromPos, toPos)
        except Exception as e:
            logging.error("铂: 飞行动画获取位置失败 {}".format(e))

    def GetInvPathBySlotId(self, slotId):
        slotId += 1
        if slotId < 9:
            return self.hotBarGridPathModel.format(slotId)

        invGridPath = self.invGridMousePathModel.format(slotId - 9)
        if not self.GetScreenNode().GetBaseUIControl(invGridPath):
            invGridPath = self.invGridTouchPathModel.format(slotId - 9)
        return invGridPath


# 监听客户端mod加载完成读取饰品文件
@Listen(Events.OnLocalPlayerStopLoading)
def OnLoadClientAddonScriptsAfter(data):
    comp = clientApi.GetEngineCompFactory().CreateConfigClient(levelId)
    configData = comp.GetConfigData(BaubleConfig.PLATINUM_LOCAL_DATA + "_{}".format(playerId))
    loadData = configData.get(BaubleConfig.BAUBLE_SLOT_INFO, {})
    if len(loadData) == 0:
        logging.error("铂: 读取饰品数据失败!!! 已重置饰品数据")
        GlobalData.baubleDict = {
            "helmet": {},
            "necklace": {},
            "armor": {},
            "back": {},
            "hand_1": {},
            "hand_2": {},
            "belt": {},
            "shoes": {},
            "other_1": {},
            "other_2": {},
            "other_3": {},
            "other_4": {}
        }
    else:
        logging.info("铂: 读取饰品数据成功")
        GlobalData.baubleDict = loadData
        DisplayPlayerBaubleInfo()
        for slotName, bauble in GlobalData.baubleDict.items():
            if len(bauble) > 0:
                try:
                    slotIndex = int(re.findall(r"\d+", slotName)[-1])
                except:
                    slotIndex = 0
                slotType = BaubleConfig.SlotName2TypeDict[slotName]
                if slotType == BaubleEnum.HAND or slotType == BaubleEnum.OTHER:
                    BaubleEquippedBroadcaster(slotType, bauble, slotIndex, True)
                else:
                    BaubleEquippedBroadcaster(slotType, bauble, isFirstLoad=True)

    uiPosition = configData.get(BaubleConfig.BAUBLE_BTN_POSITION, "left_top")
    GlobalData.uiPosition = uiPosition


# 监听客户端关闭保存饰品文件
def QuDestroy():
    SaveData()


def SaveData():
    comp = clientApi.GetEngineCompFactory().CreateConfigClient(levelId)
    configData = comp.GetConfigData(BaubleConfig.PLATINUM_LOCAL_DATA + "_{}".format(playerId))
    configData[BaubleConfig.BAUBLE_SLOT_INFO] = GlobalData.baubleDict
    isSave = comp.SetConfigData(BaubleConfig.PLATINUM_LOCAL_DATA + "_{}".format(playerId), configData)
    if isSave:
        logging.info("铂: 保存饰品数据成功")
    else:
        logging.error("铂: 保存饰品数据失败!!! 丢失玩家饰品数据")


@Listen(Events.UiInitFinished)
def OnUiInitFinished(args):
    NativeScreenManager = clientApi.GetNativeScreenManagerCls()
    # 注册经典背包界面代理
    NativeScreenManager.instance().RegisterScreenProxy("crafting.inventory_screen",
                                                       "Script_Platinum.Script_UI.baubleNewClient.InventoryClassicProxy")
    # 注册口袋背包界面代理
    NativeScreenManager.instance().RegisterScreenProxy("crafting_pocket.inventory_screen_pocket",
                                                       "Script_Platinum.Script_UI.baubleNewClient.InventoryPocketProxy")

    # 注册提示ui
    clientApi.RegisterUI("lemon_artifact", "tips_ui", "Script_Platinum.Script_UI.baubleNewClient.TipNodeUi",
                         "bauble_base_panel.main")


class TipNodeUi(EasyScreenNodeCls):

    def __init__(self):
        self.bgPath = "/tip_message"
        self.labelPath = "/tip_message/label"
        self.showTime = 0

    def ShowTip(self, tip):
        if self.showTime == 0:
            self.showTime = 90
            bg = self.GetBaseUIControl(self.bgPath)
            label = self.GetBaseUIControl(self.labelPath).asLabel()
            label.SetText(tip)
            bg.SetVisible(True)
            bg.PlayAnimation("alpha")

    @EasyScreenNodeCls.Listen(Events.OnScriptTickClient)
    def OnScriptTickClient(self):
        if self.showTime > 0:
            self.showTime -= 1


# 监听玩家死亡事件
@AllowCall
def OnPlayerDie(keepInv, pos, dimensionId):
    if not keepInv:
        # 广播脱下饰品事件
        for slotName, itemDict in GlobalData.baubleDict.items():
            if len(itemDict) > 0:
                slotType = BaubleConfig.SlotName2TypeDict[slotName]
                if slotType == BaubleEnum.HAND or slotType == BaubleEnum.OTHER:
                    slotIndex = int(re.findall(r"\d+", slotName)[-1])
                    BaubleUnequippedBroadcaster(slotType, itemDict, slotIndex)
                else:
                    BaubleUnequippedBroadcaster(slotType, itemDict)
                Call("SpawnItem", itemDict, pos, dimensionId)
                GlobalData.baubleDict[slotName] = {}


# 右键装备饰品
@AllowCall
def EquipBauble(itemDict, slotType):
    for slotName, sType in BaubleConfig.SlotName2TypeDict.items():
        if sType == slotType:
            originBauble = GlobalData.baubleDict[slotName]
            # 饰品栏位为空
            if len(originBauble) == 0:
                GlobalData.baubleDict[slotName] = itemDict
                try:
                    slotIndex = int(re.findall(r"\d+", slotName)[-1])
                except:
                    slotIndex = 0
                BaubleEquippedBroadcaster(slotType, itemDict, slotIndex)
                # 移除玩家物品栏中的饰品
                Call("RemoveItem", {"playerId": playerId})
                # 播放装备音效
                comp = clientApi.GetEngineCompFactory().CreateCustomAudio(levelId)
                comp.PlayCustomMusic("armor.equip_iron", (0, 0, 0), 0.8, 0.8, False, playerId)
                return
            # 饰品栏位不为空 且饰品不为手部或其他
            elif slotType != BaubleEnum.HAND and slotType != BaubleEnum.OTHER:
                GlobalData.baubleDict[slotName] = itemDict
                RightClickChange(slotType, itemDict, originBauble)
                return
    # 饰品栏位不为空 且饰品为手部或其他
    if slotType == BaubleEnum.HAND:
        rightHand = GlobalData.baubleDict["hand_2"]
        GlobalData.baubleDict["hand_2"] = itemDict
        RightClickChange(slotType, itemDict, rightHand)
        return
    elif slotType == BaubleEnum.OTHER:
        other1 = GlobalData.baubleDict["other_1"]
        GlobalData.baubleDict["other_1"] = itemDict
        RightClickChange(slotType, itemDict, other1)
        return


def RightClickChange(slotType, itemDict, oldDict=None):
    def TakeOffOrigin():
        Call("AddItem", {"playerId": playerId, "itemDict": oldDict})

    if oldDict:
        # 脱下原本饰品
        BaubleUnequippedBroadcaster(slotType, oldDict,
                                    2 if slotType == BaubleEnum.HAND else 1 if slotType == BaubleEnum.OTHER else 0)
        DelayRun(TakeOffOrigin, 0.1)

    # 移除玩家物品栏中的饰品
    Call("RemoveItem", {"playerId": playerId})
    BaubleEquippedBroadcaster(slotType, itemDict,
                              2 if slotType == BaubleEnum.HAND else 1 if slotType == BaubleEnum.OTHER else 0)
    # 播放装备音效
    comp = clientApi.GetEngineCompFactory().CreateCustomAudio(levelId)
    comp.PlayCustomMusic("armor.equip_iron", (0, 0, 0), 0.8, 0.8, False, playerId)
    return


# 检测玩家UIProfile
@Listen(Events.OnScriptTickClient)
def OnScriptTickClient():
    comp = clientApi.GetEngineCompFactory().CreatePlayerView(levelId)
    uiProfile = comp.GetUIProfile()
    if uiProfile != GlobalData.uiProfile:
        GlobalData.uiProfile = uiProfile
        OnUiInitFinished(None)


# 工具函数
def GetSlotNameByPath(path):
    return path.split("/")[-2].replace("bauble_", "").replace("_panel", "")


def DelayRun(func, delayTime=0.05, *args, **kwargs):
    clientApi.GetEngineCompFactory().CreateGame(playerId).AddTimer(delayTime, func, *args, **kwargs)


# 获取玩家饰品栏物品信息
def DisplayPlayerBaubleInfo():
    comp = clientApi.GetEngineCompFactory().CreateName(playerId)
    playerName = comp.GetName()
    baubleInfo = GlobalData.baubleDict
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
        displayText.append("{}: {}".format(slotName, item))
    logging.infoLines(displayText)


# 饰品装备广播
def BaubleEquippedBroadcaster(baubleSlot, itemDict, slotIndex=0, isFirstLoad=False):
    Call("BaubleEquipped",
         {"playerId": playerId, "baubleSlot": baubleSlot, "itemDict": itemDict, "isFirstLoad": isFirstLoad,
          "slotIndex": slotIndex})
    CallOTClient(playerId, "BaubleEquipped",
                 {"playerId": playerId, "baubleSlot": baubleSlot, "itemDict": itemDict, "isFirstLoad": isFirstLoad,
                  "slotIndex": slotIndex})
    SaveData()


# 饰品卸下广播
def BaubleUnequippedBroadcaster(baubleSlot, itemDict, slotIndex=0):
    Call("BaubleUnequipped",
         {"playerId": playerId, "baubleSlot": baubleSlot, "itemDict": itemDict, "slotIndex": slotIndex})
    CallOTClient(playerId, "BaubleUnequipped",
                 {"playerId": playerId, "baubleSlot": baubleSlot, "itemDict": itemDict, "slotIndex": slotIndex})
    SaveData()


class ChangeBaubleUtil(object):

    @staticmethod
    @AllowCall
    def GetPlayerBaubleInfo():
        Call("OnGetPlayerBaubleInfo", {"playerId": playerId, "baubleInfo": GlobalData.baubleDict})

    @staticmethod
    @AllowCall
    def SetPlayerBaubleInfo(baubleDict):
        # 取下所有饰品
        for slotName, oldInfo in GlobalData.baubleDict.items():
            slotType = BaubleConfig.SlotName2TypeDict[slotName]
            if len(oldInfo) > 0:
                if slotType == BaubleEnum.HAND or slotType == BaubleEnum.OTHER:
                    slotIndex = int(re.findall(r"\d+", slotName)[-1])
                    BaubleUnequippedBroadcaster(slotType, oldInfo, slotIndex)
                else:
                    BaubleUnequippedBroadcaster(slotType, oldInfo)
        GlobalData.baubleDict = baubleDict
        # 穿上所有饰品
        for slotName, newInfo in GlobalData.baubleDict.items():
            slotType = BaubleConfig.SlotName2TypeDict[slotName]
            if len(newInfo) > 0:
                if slotType == BaubleEnum.HAND or slotType == BaubleEnum.OTHER:
                    slotIndex = int(re.findall(r"\d+", slotName)[-1])
                    BaubleEquippedBroadcaster(slotType, newInfo, slotIndex)
                else:
                    BaubleEquippedBroadcaster(slotType, newInfo)

    @staticmethod
    @AllowCall
    def SetPlayerBaubleInfoWithSlot(baubleInfo, slotName):
        oldInfo = GlobalData.baubleDict[slotName]
        GlobalData.baubleDict[slotName] = baubleInfo
        slotType = BaubleConfig.SlotName2TypeDict[slotName]
        if len(oldInfo) > 0:
            if slotType == BaubleEnum.HAND or slotType == BaubleEnum.OTHER:
                slotIndex = int(re.findall(r"\d+", slotName)[-1])
                BaubleUnequippedBroadcaster(slotType, oldInfo, slotIndex)
            else:
                BaubleUnequippedBroadcaster(slotType, oldInfo)
        if len(baubleInfo) > 0:
            if slotType == BaubleEnum.HAND or slotType == BaubleEnum.OTHER:
                slotIndex = int(re.findall(r"\d+", slotName)[-1])
                BaubleEquippedBroadcaster(slotType, baubleInfo, slotIndex)
            else:
                BaubleEquippedBroadcaster(slotType, baubleInfo)

    @staticmethod
    @AllowCall
    def DecreaseBaubleDurability(num, slotName):
        baubleInfo = GlobalData.baubleDict[slotName]
        if len(baubleInfo) > 0:
            comp = clientApi.GetEngineCompFactory().CreateItem(levelId)
            itemInfo = comp.GetItemBasicInfo(baubleInfo["newItemName"], baubleInfo["newAuxValue"])
            if itemInfo["maxDurability"] > 0:
                baubleInfo["durability"] -= int(num)
                if baubleInfo["durability"] <= 0:
                    baubleInfo = {}
                    # 播放破碎音效
                    comp = clientApi.GetEngineCompFactory().CreateCustomAudio(levelId)
                    comp.PlayCustomMusic("random.break", (0, 0, 0), 0.8, 0.8, False, playerId)
                GlobalData.baubleDict[slotName] = baubleInfo
            else:
                logging.error("铂: 饰品 {} 无耐久值".format(baubleInfo["newItemName"]))
