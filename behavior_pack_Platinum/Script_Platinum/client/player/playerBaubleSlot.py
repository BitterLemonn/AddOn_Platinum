# coding=utf-8

from Script_Platinum.QuModLibs.Client import *
from Script_Platinum.QuModLibs.Modules.Services.Client import BaseService, QRequests
from Script_Platinum.data.slotData import BaubleSlotData

slotList = []  # type: list[BaubleSlotData]


@BaseService.Init
class PlayerBaubleSlotClientService(BaseService):

    def __init__(self):
        BaseService.__init__(self)

    @BaseService.REG_API("client/slot/playerSlotSync")
    def playerSlotSync(self, data):  # type: (list[dict]) -> None
        if isinstance(data, QRequests.RequestResults):
            data = data.data
        global slotList
        slotList = [BaubleSlotData.fromDict(slot) for slot in data]

    @BaseService.Listen("OnLocalPlayerStopLoading")
    def onLocalPlayerStopLoading(self, data):
        # 请求玩家槽位列表
        self.syncRequest("server/slot/requestPlayerSlotList", QRequests.Args().setCallBack(self.playerSlotSync))
