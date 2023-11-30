# coding=utf-8
from ..QuModLibs.Client import *
from ..QuModLibs.UI import *

from .. import loggingUtils as logging
from ..commonConfig import BaubleEnum
from ..commonConfig import BaubleDict

CustomUIScreenProxy = clientApi.GetUIScreenProxyCls()


class BaubleConfig(object):
    PLATINUM_LOCAL_DATA = "platinum_local_data"
    BAUBLE_SLOT_INFO = "bauble_slot_info"

    UI_DEF = "bauble_base_panel"
    UI_DEF_MAIN = "bauble_base_panel.main"
    UI_DEF_BAUBLE_BTN = "bauble_base_panel.bauble_button"

    UI_DEF_NEW = "bauble_new"
    UI_DEF_NEW_MAIN = "bauble_new.main"
    UI_DEF_NEW_BAUBLE_CLASSIC = "bauble_new.bauble_classic_new"
    UI_DEF_NEW_BAUBLE_POCKET = "bauble_new.bauble_pocket"
    UI_DEF_NEW_BAUBLE_TRANS_BTN = "bauble_new.transparent_btn"

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


# 背包经典界面代理类
class InventoryClassicProxy(CustomUIScreenProxy):
    def __init__(self, screenName, screenNode):
        CustomUIScreenProxy.__init__(self, screenName, screenNode)
        # 临时变量
        self.baubleSelect = ""
        self.invSelect = -1
        self.invInfo = {}
        self.isTouch = False

        # 饰品栏打开状态
        self.openState = False

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

    def OnCreate(self):
        self.CreateBaubleBtn()

    def OnDestroy(self):
        screen = self.GetScreenNode()
        if self.openState:
            self.CloseBaublePanel()

        panelPath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/content_stack_panel/survival_padding"
        baublePanel = screen.GetBaseUIControl(panelPath + "/bauble_classic_new")
        screen.RemoveChildControl(baublePanel)
        panelPath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/content_stack_panel/player_inventory/inventory_panel_top_half/player_armor_panel/player_bg"
        baubleBtn = screen.GetBaseUIControl(panelPath + "/bauble_button").asButton()
        screen.RemoveChildControl(baubleBtn)

        UnListenForEvent("OnItemSlotButtonClickedEvent", self, self.OnItemSlotButtonClickedEvent)

    def OnTick(self):
        # 切换界面隐藏饰品栏
        screen = self.GetScreenNode()
        panelPath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/content_stack_panel/player_inventory/inventory_panel_top_half/player_armor_panel/player_bg"

        recipePath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/content_stack_panel/recipe_book"
        recipePanel = screen.GetBaseUIControl(recipePath)

        invPath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/content_stack_panel/toolbar_anchor/toolbar_panel/toolbar_background/toolbar_stack_panel/survival_layout_toggle_panel/survival_layout_toggle/this_toggle/checked"
        invBtn = screen.GetBaseUIControl(invPath)
        invCheck = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/content_stack_panel/toolbar_anchor/toolbar_panel/toolbar_background/toolbar_stack_panel/survival_layout_toggle_panel/survival_layout_toggle/this_toggle/checked_hover"
        invBtnCheck = screen.GetBaseUIControl(invCheck)

        if recipePanel and recipePanel.GetVisible():
            try:
                baubleBtn = screen.GetBaseUIControl(panelPath + "/bauble_button").asButton()
                baubleBtn.SetVisible(False)

                if self.openState:
                    self.CloseBaublePanel()
            except:
                pass
        elif (invBtn and invBtn.GetVisible()) or (invBtnCheck and invBtnCheck.GetVisible()):
            try:
                baubleBtn = screen.GetBaseUIControl(panelPath + "/bauble_button").asButton()
                if not baubleBtn.GetVisible():
                    baubleBtn.SetVisible(True)
                    screen.UpdateScreen(True)
            except:
                pass

    # 创建饰品栏开关按钮
    def CreateBaubleBtn(self):
        screen = self.GetScreenNode()
        panelPath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/content_stack_panel/player_inventory/inventory_panel_top_half/player_armor_panel/player_bg"
        panel = screen.GetBaseUIControl(panelPath)
        if not panel:
            logging.error("铂: 无法找到特定界面")
            return
        try:
            baubleBtn = screen.GetBaseUIControl(panelPath + "/bauble_button").asButton()
        except:
            baubleBtn = screen.CreateChildControl(BaubleConfig.UI_DEF_BAUBLE_BTN, "bauble_button", panel).asButton()
        baubleBtn.AddTouchEventParams({"isSwallow": True})
        baubleBtn.SetButtonTouchUpCallback(self.OnBaubleButtonClicked)

    # 饰品栏开关按钮回调
    def OnBaubleButtonClicked(self, args):
        if not self.openState:
            self.OpenBaublePanel()
        else:
            self.CloseBaublePanel()

    # 打开饰品栏
    def OpenBaublePanel(self):
        screen = self.GetScreenNode()
        panelPath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/content_stack_panel/survival_padding"
        panel = screen.GetBaseUIControl(panelPath)

        if panel:
            try:
                baublePanel = screen.GetBaseUIControl(panelPath + "/bauble_classic_new")
                baublePanel.SetVisible(True)
            except:
                screen.CreateChildControl(BaubleConfig.UI_DEF_NEW_BAUBLE_CLASSIC, "bauble_classic_new", panel)
                self.baublePath = panelPath + "/bauble_classic_new"
                self.InitBaublePanel()
        self.openState = True

        ListenForEvent("OnItemSlotButtonClickedEvent", self, self.OnItemSlotButtonClickedEvent)

    # 关闭饰品栏
    def CloseBaublePanel(self):
        screen = self.GetScreenNode()
        panelPath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/content_stack_panel/survival_padding"
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

        if self.invSelect != -1:
            self.SelectBauble()
            return
        elif len(self.baubleSelect) == 0:
            # 选中饰品
            if self.invSelect == -1:
                self.SelectBauble(btnPath)
        elif self.baubleSelect == btnPath:
            self.SelectBauble()
        else:
            # 交换饰品
            baubleFrom = GlobalData.baubleDict[GetSlotNameByPath(self.baubleSelect)]
            baubleTo = GlobalData.baubleDict[GetSlotNameByPath(btnPath)]
            if len(baubleFrom) != 0 or len(baubleTo) != 0:
                def changePos():
                    GlobalData.baubleDict[GetSlotNameByPath(self.baubleSelect)] = baubleTo
                    GlobalData.baubleDict[GetSlotNameByPath(btnPath)] = baubleFrom
                    self.RenderBauble(self.baubleSelect)
                    self.RenderBauble(btnPath)
                    # 发送脱下饰品事件
                    if len(baubleFrom) != 0:
                        BaubleUnequippedBroadcaster(
                            BaubleConfig.SlotName2TypeDict[GetSlotNameByPath(self.baubleSelect)],
                            baubleFrom)
                    if len(baubleTo) != 0:
                        BaubleUnequippedBroadcaster(BaubleConfig.SlotName2TypeDict[GetSlotNameByPath(btnPath)],
                                                    baubleTo)
                    # 发送穿戴饰品事件
                    if len(baubleTo) != 0:
                        BaubleEquippedBroadcaster(BaubleConfig.SlotName2TypeDict[GetSlotNameByPath(btnPath)], baubleTo)
                    if len(baubleFrom) != 0:
                        BaubleEquippedBroadcaster(BaubleConfig.SlotName2TypeDict[GetSlotNameByPath(self.baubleSelect)],
                                                  baubleFrom)

                if len(baubleFrom) != 0 and len(baubleTo) != 0:
                    if CheckBauble(baubleFrom, self.baubleSelect) and CheckBauble(baubleTo, btnPath):
                        changePos()
                elif len(baubleFrom) != 0:
                    if CheckBauble(baubleFrom, btnPath):
                        changePos()
                else:
                    if CheckBauble(baubleTo, self.baubleSelect):
                        changePos()

            self.SelectBauble()

    # 物品栏位按钮回调
    def OnItemSlotButtonClickedEvent(self, data):
        slotId = data["slotIndex"]
        # 未选中物品时
        if self.invSelect == -1:
            if len(self.baubleSelect) != 0:
                self.invSelect = slotId
                comp = clientApi.GetEngineCompFactory().CreateItem(playerId)
                itemDict = comp.GetPlayerItem(clientApi.GetMinecraftEnum().ItemPosType.INVENTORY, slotId, True)
                self.invInfo = itemDict
                # 穿戴饰品
                if itemDict:
                    if CheckBauble(self.invInfo, self.baubleSelect):
                        self.SwapBauble()
                    else:
                        self.SelectBauble()
                # 脱下饰品
                elif len(GlobalData.baubleDict[GetSlotNameByPath(self.baubleSelect)]) > 0:
                    self.SwapBauble()

            # 不能通过先点击物品栏再点击饰品栏的方式直接穿上饰品
            else:
                comp = clientApi.GetEngineCompFactory().CreateItem(playerId)
                itemDict = comp.GetPlayerItem(clientApi.GetMinecraftEnum().ItemPosType.INVENTORY, slotId)
                if itemDict:
                    self.invSelect = slotId
        # 选中物品时
        else:
            self.invSelect = -1
            self.invInfo = {}

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
        # 穿戴或交换
        if itemDict and len(itemDict) > 0:
            slotType = BaubleConfig.SlotName2TypeDict[GetSlotNameByPath(baublePath)]
            originBauble = GlobalData.baubleDict[GetSlotNameByPath(baublePath)]

            # 发送脱下饰品事件
            if len(originBauble) != 0:
                BaubleUnequippedBroadcaster(slotType, originBauble)
                # 鼠标不延迟
                if not self.isTouch:
                    Call("AddItem", {"playerId": playerId, "itemDict": originBauble, "slot": self.invSelect})
                else:
                    DelayRun(Call, 0.1, "AddItem",
                             {"playerId": playerId, "itemDict": originBauble, "slot": self.invSelect})
            else:
                Call("RemoveItem", {"playerId": playerId, "slot": self.invSelect})

            GlobalData.baubleDict[GetSlotNameByPath(baublePath)] = itemDict
            # 发送穿戴饰品事件
            BaubleEquippedBroadcaster(slotType, itemDict)
        else:
            originBauble = GlobalData.baubleDict[GetSlotNameByPath(baublePath)]
            slotType = BaubleConfig.SlotName2TypeDict[GetSlotNameByPath(baublePath)]
            # 发送脱下饰品事件
            if len(originBauble) != 0:
                GlobalData.baubleDict[GetSlotNameByPath(baublePath)] = {}
                BaubleUnequippedBroadcaster(slotType, originBauble)
                # 鼠标不延迟
                if not self.isTouch:
                    Call("AddItem", {"playerId": playerId, "itemDict": originBauble, "slot": self.invSelect})
                else:
                    DelayRun(Call, 0.1, "AddItem",
                             {"playerId": playerId, "itemDict": originBauble, "slot": self.invSelect})

        self.RenderBauble(self.baubleSelect)
        self.SelectBauble()
        self.invSelect = -1

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
            # 脱下
            else:
                baubleImg.SetVisible(True)
                itemRenderer.SetVisible(False)

        except Exception as e:
            logging.error("铂: 饰品栏位渲染器获取失败 {}, 错误: {}".format(baublePath.split("/")[-2], e))
            return


# 背包口袋界面代理类
class InventoryPocketProxy(InventoryClassicProxy):
    def __init__(self, screenName, screenNode):
        InventoryClassicProxy.__init__(self, screenName, screenNode)
        self.openState = False

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

        UnListenForEvent("OnItemSlotButtonClickedEvent", self, self.OnItemSlotButtonClickedEvent)
        try:
            panelPath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/root_panel/hotbar_and_panels/gamepad_helper_border/both_panels/right_panel/armor_tab_content/content/equipment_and_renderer/armor_panel/armor_and_player/player_preview_border/player_bg"
            baubleBtn = screen.GetBaseUIControl(panelPath + "/bauble_button")
            self.GetScreenNode().RemoveChildControl(baubleBtn)
            panelPath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/root_panel/hotbar_and_panels/gamepad_helper_border/both_panels/right_panel/armor_tab_content/content/label_and_renderer"
            baublePanel = screen.GetBaseUIControl(panelPath + "/bauble_pocket_new")
            self.GetScreenNode().RemoveChildControl(baublePanel)
        except:
            pass

    def CreateBaubleBtn(self):
        screen = self.GetScreenNode()
        panelPath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/root_panel/hotbar_and_panels/gamepad_helper_border/both_panels/right_panel/armor_tab_content/content/equipment_and_renderer/armor_panel/armor_and_player/player_preview_border/player_bg"
        panel = screen.GetBaseUIControl(panelPath)
        if not panel:
            logging.error("铂: 无法找到特定界面")
            return
        try:
            baubleBtn = screen.GetBaseUIControl(panelPath + "/bauble_button").asButton()
        except:
            baubleBtn = screen.CreateChildControl(BaubleConfig.UI_DEF_BAUBLE_BTN, "bauble_button", panel).asButton()
        baubleBtn.AddTouchEventParams({"isSwallow": True})
        baubleBtn.SetButtonTouchUpCallback(self.OnBaubleButtonClicked)

    def OpenBaublePanel(self):
        screen = self.GetScreenNode()
        panelPath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/root_panel/hotbar_and_panels/gamepad_helper_border/both_panels/right_panel/armor_tab_content/content/label_and_renderer"
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
        panelPath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/root_panel/hotbar_and_panels/gamepad_helper_border/both_panels/right_panel/armor_tab_content/content/label_and_renderer"
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


# 监听客户端mod加载完成读取饰品文件
@Listen(Events.OnLocalPlayerStopLoading)
def OnLoadClientAddonScriptsAfter(data):
    comp = clientApi.GetEngineCompFactory().CreateConfigClient(levelId)
    configData = comp.GetConfigData(BaubleConfig.PLATINUM_LOCAL_DATA)
    GlobalData.baubleDict = configData.get(BaubleConfig.BAUBLE_SLOT_INFO, {})
    if len(GlobalData.baubleDict) == 0:
        logging.error("铂: 读取饰品数据失败!!!")
    else:
        logging.info("铂: 读取饰品数据成功")
        DisplayPlayerBaubleInfo()
        for slotName, bauble in GlobalData.baubleDict.items():
            if len(bauble) > 0:
                BaubleEquippedBroadcaster(BaubleConfig.SlotName2TypeDict[slotName], bauble)


# 监听客户端关闭保存饰品文件
def QuDestroy():
    comp = clientApi.GetEngineCompFactory().CreateConfigClient(levelId)
    configData = comp.GetConfigData(BaubleConfig.PLATINUM_LOCAL_DATA)
    configData[BaubleConfig.BAUBLE_SLOT_INFO] = GlobalData.baubleDict
    isSave = comp.SetConfigData(BaubleConfig.PLATINUM_LOCAL_DATA, configData)
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


@Listen(Events.PushScreenEvent)
def OnPushScreenEvent(data):
    NativeScreenManager = clientApi.GetNativeScreenManagerCls()
    try:
        if "inventory_screen" not in data["screenName"]:
            if GlobalData.uiProfile == 0:
                NativeScreenManager.instance().UnRegisterScreenProxy("crafting.inventory_screen",
                                                                     "Script_Platinum.Script_UI.baubleNewClient.InventoryClassicProxy")
            else:
                NativeScreenManager.instance().UnRegisterScreenProxy("crafting_pocket.inventory_screen_pocket",
                                                                     "Script_Platinum.Script_UI.baubleNewClient.InventoryPocketProxy")
        else:
            if GlobalData.uiProfile == 0:
                NativeScreenManager.instance().RegisterScreenProxy("crafting.inventory_screen",
                                                                   "Script_Platinum.Script_UI.baubleNewClient.InventoryClassicProxy")
            else:
                NativeScreenManager.instance().RegisterScreenProxy("crafting_pocket.inventory_screen_pocket",
                                                                   "Script_Platinum.Script_UI.baubleNewClient.InventoryPocketProxy")
    except:
        pass


# 监听玩家死亡事件
@AllowCall
def OnPlayerDie(keepInv, pos, dimensionId):
    if not keepInv:
        # 广播脱下饰品事件
        for slotName, itemDict in GlobalData.baubleDict.items():
            if len(itemDict) > 0:
                slotType = BaubleConfig.SlotName2TypeDict[slotName]
                Call("BaubleUnequipped", {"playerId": playerId, "itemDict": itemDict, "baubleSlot": slotType})
                CallOTClient(playerId, "BaubleUnequipped",
                             {"playerId": playerId, "itemDict": itemDict, "baubleSlot": slotType})
                Call("SpawnItem", itemDict, pos, dimensionId)
                GlobalData.baubleDict[slotName] = {}


# 工具函数
def GetSlotNameByPath(path):
    return path.split("/")[-2].replace("bauble_", "").replace("_panel", "")


def CheckBauble(itemDict, baublePath):
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

        if targetSlot == BaubleConfig.SlotName2TypeDict[GetSlotNameByPath(baublePath)]:
            return True

    return False


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
def BaubleEquippedBroadcaster(baubleSlot, itemDict):
    Call("BaubleEquipped", {"playerId": playerId, "baubleSlot": baubleSlot, "itemDict": itemDict})
    CallOTClient(playerId, "BaubleEquipped", {"playerId": playerId, "baubleSlot": baubleSlot, "itemDict": itemDict})


# 饰品卸下广播
def BaubleUnequippedBroadcaster(baubleSlot, itemDict):
    Call("BaubleUnequipped", {"playerId": playerId, "baubleSlot": baubleSlot, "itemDict": itemDict})
    CallOTClient(playerId, "BaubleUnequipped", {"playerId": playerId, "baubleSlot": baubleSlot, "itemDict": itemDict})
