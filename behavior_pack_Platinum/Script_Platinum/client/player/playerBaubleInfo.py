# coding=utf-8
from Script_Platinum import commonConfig
from Script_Platinum.QuModLibs.Client import *
from Script_Platinum.QuModLibs.Modules.Services.Client import BaseService, QRequests
from Script_Platinum.data.itemStack import ItemStack
from Script_Platinum.data.requestData import ChangeBaubleRequestData


@BaseService.Init
class PlayerBaubleInfoClientService(BaseService):

    def __init__(self):
        BaseService.__init__(self)
        self.baubleInfo = {}  # type: dict[str, ItemStack]
        self.listener = []  # type: list[function]

    @BaseService.REG_API("client/bauble/unequipBaubleBoardcast")
    def takeOffBaubleBoardcast(self, data):  # type: (dict) -> None
        boardCastSys = clientApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_CLIENT)
        if boardCastSys:
            boardCastSys.BroadcastEvent(commonConfig.BAUBLE_UNEQUIPPED_EVENT, data)

    @BaseService.REG_API("client/bauble/equipBaubleBoardcast")
    def equipBaubleBoardcast(self, data):  # type: (dict) -> None
        boardCastSys = clientApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_CLIENT)
        if boardCastSys:
            boardCastSys.BroadcastEvent(commonConfig.BAUBLE_EQUIPPED_EVENT, data)

    @BaseService.REG_API("client/bauble/syncFromServer")
    def syncFromServer(self, data):  # type: (dict) -> None
        self.baubleInfo = {slotId: ItemStack.fromDict(item) if item else None for slotId, item in data.items()}
        self._callListener()

    @BaseService.Listen("OnLocalPlayerStopLoading")
    def onLocalPlayerStopLoading(self, data):
        def playerSlotSync(data):  # type: (QRequests.RequestResults) -> None
            if isinstance(data, QRequests.RequestResults):
                data = data.data
                self.syncFromServer(data)

        # 请求玩家饰品信息
        self.syncRequest("server/player/requestBaubleInfo", QRequests.Args().setCallBack(playerSlotSync))

    def addBaubleInfoListener(self, callback):
        """添加一个监听器, 当玩家饰品信息更新时会调用这个监听器"""
        if callback not in self.listener:
            self.listener.append(callback)

    def removeBaubleInfoListener(self, callback):
        """移除一个监听器"""
        if callback in self.listener:
            self.listener.remove(callback)

    def _callListener(self):
        for callback in self.listener:
            callback(self.baubleInfo)

    def getBaubleInfo(self):  # type: () -> dict[str, ItemStack]
        """获取玩家饰品信息"""
        return self.baubleInfo

    def getBaubleInfoBySlot(self, slotId):  # type: (str) -> ItemStack | None
        """根据槽位ID获取玩家饰品信息"""
        return self.baubleInfo.get(slotId, None)

    def popBaubleInfoBySlot(self, slotId, index):  # type: (str, int) -> ItemStack | None
        """根据槽位ID获取并移除玩家饰品信息"""
        self.syncRequest(
            "server/player/changeBauble",
            QRequests.Args(ChangeBaubleRequestData(None, slotId, index).toDict()),
        )
