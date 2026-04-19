# coding=utf-8

from mod.client import extraClientApi as clientApi
from Script_Platinum import commonConfig


class BoardcastClient(clientApi.GetClientSystemCls()):

    def __init__(self, namespace, name):
        super(BoardcastClient, self).__init__(namespace, name)

    def GetBaubleInfo(self):
        """获取玩家饰品信息"""
        from Script_Platinum.client.player.playerBaubleInfo import PlayerBaubleInfoClientService

        playerBaubleInfo = PlayerBaubleInfoClientService.access().getBaubleInfo()
        infoDict = {
            slotId: itemStack.dumpToDict() if itemStack else None for slotId, itemStack in playerBaubleInfo.items()
        }
        # 兼容旧版本发送事件
        self.BroadcastEvent(commonConfig.BAUBLE_GET_INFO_EVENT, infoDict)
        return infoDict

    def GetSlotInfo(self):
        """获取玩家饰品槽位信息"""
        from Script_Platinum.client.player.playerBaubleSlot import PlayerBaubleSlotClientService

        slotInfo = PlayerBaubleSlotClientService.access().getPlayerSlotList()
        slotInfo = [slot.__dict__ for slot in slotInfo]
        return slotInfo
