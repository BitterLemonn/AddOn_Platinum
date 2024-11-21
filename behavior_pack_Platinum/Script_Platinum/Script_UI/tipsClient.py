# coding=utf-8
import logging

from ..QuModLibs.Client import *

ScreenNode = clientApi.GetScreenNodeCls()


@Listen(Events.UiInitFinished)
def OnTipsUiInitFinished(args):
    clientApi.RegisterUI("platinum", "info_tips", "Script_Platinum.Script_UI.tipsClient.TipsUI", "info_tips.screen")
    comp = clientApi.GetEngineCompFactory().CreateConfigClient(levelId)
    data = comp.GetConfigData("platinumTips", True)
    isSet = data.get("isSet", 0)
    if isinstance(isSet, bool):
        isSet = 0

    if isSet % 20 == 0:
        clientApi.PushScreen("platinum", "info_tips")


class TipsUI(ScreenNode):

    def __init__(self, namespace, name, param):
        ScreenNode.__init__(self, namespace, name, param)
        self.confirmBtnPath = "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/input_panel/button_panel/button"
        self.waitingTime = 30 * 5

    def Tick(self):
        if self.waitingTime <= 0:
            confirmBtn = self.GetBaseUIControl(self.confirmBtnPath).asButton()
            confirmBtn.SetTouchEnable(True)
            label = self.GetBaseUIControl(self.confirmBtnPath + "/button_label").asLabel()
            label.SetText("我已知晓，不再提示")
            UnListenForEvent("OnScriptTickClient", self, self.Tick)
        else:
            self.waitingTime -= 1
            label = self.GetBaseUIControl(self.confirmBtnPath + "/button_label").asLabel()
            label.SetText("我已知晓，不再提示({}s)".format(self.waitingTime // 30 + 1))

    def Create(self):
        confirmBtn = self.GetBaseUIControl(self.confirmBtnPath).asButton()
        confirmBtn.AddTouchEventParams({"isSwallow": True})
        confirmBtn.SetButtonTouchUpCallback(self.OnConfirmBtnTouchUp)
        confirmBtn.SetTouchEnable(False)

        ListenForEvent("OnScriptTickClient", self, self.Tick)

    def OnConfirmBtnTouchUp(self, _):
        comp = clientApi.GetEngineCompFactory().CreateConfigClient(levelId)
        data = comp.GetConfigData("platinumTips", True)
        data["isSet"] = data.get("isSet", 0) + 1
        comp.SetConfigData("platinumTips", data, True)
        clientApi.PopScreen()
