import logging

from ..QuModLibs.Server import *
from .. import CommonConfig


class BroadcasterServer(serverApi.GetServerSystemCls()):

    def __init__(self, namespace, name):
        super(BroadcasterServer, self).__init__(namespace, name)


@AllowCall
def BaubleEquipped(data):
    server = serverApi.GetSystem(CommonConfig.PLATINUM_NAMESPACE, CommonConfig.PLATINUM_BROADCAST_SERVER)
    server.BroadcastEvent(CommonConfig.BAUBLE_EQUIPPED_EVENT, data)


@AllowCall
def BaubleUnequipped(data):
    server = serverApi.GetSystem(CommonConfig.PLATINUM_NAMESPACE, CommonConfig.PLATINUM_BROADCAST_SERVER)
    server.BroadcastEvent(CommonConfig.BAUBLE_UNEQUIPPED_EVENT, data)
