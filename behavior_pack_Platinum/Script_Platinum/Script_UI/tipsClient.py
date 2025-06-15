# coding=utf-8
from .. import developLogging as logging

from ..QuModLibs.Client import *
from ..QuModLibs.Modules.Services.Client import BaseService

ScreenNode = clientApi.GetScreenNodeCls()


@BaseService.Init
class TipsClientService(BaseService):

    def __init__(self):
        BaseService.__init__(self)
        self.isShowTips = False

    @BaseService.Listen(Events.UiInitFinished)
    def OnTipsUiInitFinished(self, args):
        if not self.isShowTips:
            self.isShowTips = True
            clientApi.RegisterUI("platinum", "info_tips", "Script_Platinum.Script_UI.tipsClient.TipsUI",
                                 "info_tips.screen")
            comp = clientApi.GetEngineCompFactory().CreateConfigClient(levelId)
            data = comp.GetConfigData("platinumTips", True)
            if not data.get("dontShow", False):
                isSet = data.get("isSet", 0)
                if isinstance(isSet, bool):
                    isSet = 0
                isSet += 1
                logging.debug("铂: 已进入游戏{}次".format(isSet))
                if isSet % 20 == 0:
                    clientApi.PushScreen("platinum", "info_tips")
                comp.SetConfigData("platinumTips", {"isSet": isSet}, True)


class TipsUI(ScreenNode):

    def __init__(self, namespace, name, param):
        ScreenNode.__init__(self, namespace, name, param)
        self.basePath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/input_panel/button_stack_panel"
        self.confirmBtnPath = self.basePath + "/confirm_panel/button"
        self.dontShowBtnPath = self.basePath + "/dont_show_panel/button"
        self.waitingTime = 30 * 5

    def Tick(self):
        if self.waitingTime <= 0:
            confirmBtn = self.GetBaseUIControl(self.confirmBtnPath).asButton()
            confirmBtn.SetTouchEnable(True)
            confirmLabel = self.GetBaseUIControl(self.confirmBtnPath + "/button_label").asLabel()
            confirmLabel.SetText("我已知晓")
            dontShowBtn = self.GetBaseUIControl(self.dontShowBtnPath).asButton()
            dontShowBtn.SetTouchEnable(True)
            dontShowLabel = self.GetBaseUIControl(self.dontShowBtnPath + "/button_label").asLabel()
            dontShowLabel.SetText("不再提示")
            UnListenForEvent("OnScriptTickClient", self, self.Tick)
        else:
            self.waitingTime -= 1
            confirmLabel = self.GetBaseUIControl(self.confirmBtnPath + "/button_label").asLabel()
            confirmLabel.SetText("我已知晓({}s)".format(self.waitingTime // 30 + 1))
            dontShowLabel = self.GetBaseUIControl(self.dontShowBtnPath + "/button_label").asLabel()
            dontShowLabel.SetText("不再提示({}s)".format(self.waitingTime // 30 + 1))

    def Create(self):
        confirmBtn = self.GetBaseUIControl(self.confirmBtnPath).asButton()
        confirmBtn.AddTouchEventParams({"isSwallow": True})
        confirmBtn.SetButtonTouchUpCallback(self.OnConfirmBtnTouchUp)
        confirmBtn.SetTouchEnable(False)
        dontShowBtn = self.GetBaseUIControl(self.dontShowBtnPath).asButton()
        dontShowBtn.AddTouchEventParams({"isSwallow": True})
        dontShowBtn.SetButtonTouchUpCallback(self.OnDontShowBtnTouchUp)
        dontShowBtn.SetTouchEnable(False)

        ListenForEvent("OnScriptTickClient", self, self.Tick)

    def OnConfirmBtnTouchUp(self, _):
        clientApi.PopScreen()

    def OnDontShowBtnTouchUp(self, _):
        comp = clientApi.GetEngineCompFactory().CreateConfigClient(levelId)
        data = comp.GetConfigData("platinumTips", True)
        data["dontShow"] = True
        comp.SetConfigData("platinumTips", data, True)
        clientApi.PopScreen()
