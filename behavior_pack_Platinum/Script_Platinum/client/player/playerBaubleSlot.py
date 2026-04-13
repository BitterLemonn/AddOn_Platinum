# coding=utf-8

from Script_Platinum.QuModLibs.Client import *
from Script_Platinum.QuModLibs.Modules.Services.Client import BaseService, QRequests
from Script_Platinum.data.slotData import BaubleSlotData


@BaseService.Init
class PlayerBaubleSlotClientService(BaseService):

    def __init__(self):
        BaseService.__init__(self)
        self.slotList = []  # type: list[BaubleSlotData]
        self.listener = []  # type: list[function]

    @BaseService.REG_API("client/slot/playerSlotSync")
    def playerSlotSync(self, data):  # type: (list[dict]) -> None
        if isinstance(data, QRequests.RequestResults):
            data = data.data
        self.slotList = [BaubleSlotData.fromDict(slot) for slot in data]
        self._callListener()

    @BaseService.Listen("OnLocalPlayerStopLoading")
    def onLocalPlayerStopLoading(self, data):
        # 请求玩家槽位列表
        self.syncRequest("server/slot/requestPlayerSlotList", QRequests.Args().setCallBack(self.playerSlotSync))

    def addPlayerSlotListener(self, callback):
        """添加一个监听器, 当玩家槽位信息更新时会调用这个监听器"""
        if callback not in self.listener:
            self.listener.append(callback)

    def removePlayerSlotListener(self, callback):
        """移除一个监听器"""
        if callback in self.listener:
            self.listener.remove(callback)

    def getPlayerSlotList(self):
        """获取玩家槽位列表"""
        return self.slotList

    def _callListener(self):
        for callback in self.listener:
            callback(self.slotList)
