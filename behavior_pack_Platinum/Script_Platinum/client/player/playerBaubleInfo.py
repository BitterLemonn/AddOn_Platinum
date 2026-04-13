# coding=utf-8
from Script_Platinum.QuModLibs.Client import *
from Script_Platinum.QuModLibs.Modules.Services.Client import BaseService, QRequests
from Script_Platinum.data.itemStack import ItemStack


@BaseService.Init
class PlayerBaubleInfoClientService(BaseService):

    def __init__(self):
        BaseService.__init__(self)
        self.baubleInfo = {}  # type: dict[str, ItemStack]
        self.listener = []  # type: list[function]

    @BaseService.REG_API("client/bauble/syncFromServer")
    def syncFromServer(self, data):  # type: (dict) -> None
        self.baubleInfo = {slotId: ItemStack.fromDict(item) for slotId, item in data.items()}
        self._callListener()

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

    def popBaubleInfoBySlot(self, slotId):  # type: (str) -> ItemStack | None
        """根据槽位ID获取并移除玩家饰品信息"""
        self.syncRequest("server/slot/popBaubleInfoBySlot", QRequests.Args(slotId))
