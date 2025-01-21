# coding=utf-8
import logging

import commonConfig
import mod.client.extraClientApi as clientApi


class BuildInBaubleClient(clientApi.GetClientSystemCls()):

    def __init__(self, namespace, name):
        super(BuildInBaubleClient, self).__init__(namespace, name)
        logging.debug("BuildInBaubleClient init")
        self.listenEvent()

    def listenEvent(self):
        # 监听饰品装备事件
        self.ListenForEvent(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_CLIENT,
                            commonConfig.BAUBLE_EQUIPPED_EVENT, self, self.onBaubleEquipped)
        # 监听饰品卸下事件
        self.ListenForEvent(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_CLIENT,
                            commonConfig.BAUBLE_UNEQUIPPED_EVENT, self, self.onBaubleUnequipped)

    def onBaubleEquipped(self, data):
        """
        饰品装备事件
        :param data: {"slotIndex": Int, "playerId": str, "isFirstLoad": bool, "baubleSlot": str, "baubleSlotId": str "itemDict": dict}
        """
        playerId = data["playerId"]
        bauble = data["itemDict"]
        isFirstLoad = data["isFirstLoad"]
        slot = data["baubleSlot"]
        slotId = data["baubleSlotId"]
        slotIndex = data["slotIndex"]

    def onBaubleUnequipped(self, data):
        """
        饰品卸下事件
        :param data: {"slotIndex": Int, "playerId": str, "isFirstLoad": bool, "baubleSlot": str, "baubleSlotId": str "itemDict": dict}
        :return:
        """
        logging.error(data)
        playerId = data["playerId"]
        bauble = data["itemDict"]
        isFirstLoad = data["isFirstLoad"]
        slot = data["baubleSlot"]
        slotId = data["baubleSlotId"]
        slotIndex = data["slotIndex"]
