# coding=utf-8
from ..QuModLibs.Server import *
from .. import commonConfig
from .. import loggingUtils as logging


class BroadcasterServer(serverApi.GetServerSystemCls()):

    def __init__(self, namespace, name):
        super(BroadcasterServer, self).__init__(namespace, name)
        # 监听饰品注册事件
        self.ListenForEvent(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER,
                            commonConfig.BAUBLE_REGISTER_EVENT, self, self.onBaubleRegister)

    def BaubleRegister(self, data):
        """
        饰品注册事件
        :param data: {baubleName: str, baubleSlot: str, *customTips: str}
        :return:
        """

        baubleName = data["baubleName"]
        baubleSlot = data["baubleSlot"]
        customTips = data.get("customTips", "")
        comp = serverApi.GetEngineCompFactory().CreateGame(serverApi.GetLevelId())
        exist = comp.LookupItemByName(baubleName)

        if baubleSlot in commonConfig.BaubleEnum.__dict__.values():
            if exist:
                if len(customTips) > 0:
                    commonConfig.BaubleDict[baubleName] = [baubleSlot, customTips]
                else:
                    commonConfig.BaubleDict[baubleName] = baubleSlot
                logging.info("铂: 饰品 {} 已注册".format(baubleName))
            else:
                logging.error("铂: 物品 {} 不存在,请检查标识符是否正确".format(baubleName))
        else:
            logging.error("铂: 饰品 {} 插槽 {} 不存在,请检查饰品槽位是否正确".format(baubleName, baubleSlot))


server = serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER)


@AllowCall
def BaubleEquipped(data):
    server.BroadcastEvent(commonConfig.BAUBLE_EQUIPPED_EVENT, data)


@AllowCall
def BaubleUnequipped(data):
    server.BroadcastEvent(commonConfig.BAUBLE_UNEQUIPPED_EVENT, data)
