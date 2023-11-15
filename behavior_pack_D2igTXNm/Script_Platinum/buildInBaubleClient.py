# coding=utf-8
import logging

import CommonConfig
import mod.client.extraClientApi as clientApi


class BuildInBaubleClient(clientApi.GetClientSystemCls()):

    def __init__(self, namespace, name):
        super(BuildInBaubleClient, self).__init__(namespace, name)
        self.listenEvent()

    def listenEvent(self):
        # 监听饰品装备事件
        self.ListenForEvent(CommonConfig.PLATINUM_NAMESPACE, CommonConfig.PLATINUM_BROADCAST_CLIENT,
                            CommonConfig.BAUBLE_EQUIPPED_EVENT, self, self.onBaubleEquipped)
        # 监听饰品卸下事件
        self.ListenForEvent(CommonConfig.PLATINUM_NAMESPACE, CommonConfig.PLATINUM_BROADCAST_CLIENT,
                            CommonConfig.BAUBLE_UNEQUIPPED_EVENT, self, self.onBaubleUnequipped)

    def onBaubleEquipped(self, data):
        """
        饰品装备事件
        :param data: {playerId: str, itemDict: dict, baubleSlot: str}
        """
        playerId = data["playerId"]
        bauble = data["itemDict"]
        slot = data["baubleSlot"]

    def onBaubleUnequipped(self, data):
        """
        饰品卸下事件
        :param data: {playerId: str, itemDict: dict, baubleSlot: str}
        :return:
        """
        playerId = data["playerId"]
        bauble = data["itemDict"]
        slot = data["baubleSlot"]
