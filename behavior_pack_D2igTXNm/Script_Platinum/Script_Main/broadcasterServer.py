from ..QuModLibs.Server import *
from .. import commonConfig


class BroadcasterServer(serverApi.GetServerSystemCls()):

    def __init__(self, namespace, name):
        super(BroadcasterServer, self).__init__(namespace, name)


@AllowCall
def BaubleEquipped(data):
    server = serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER)
    server.BroadcastEvent(commonConfig.BAUBLE_EQUIPPED_EVENT, data)


@AllowCall
def BaubleUnequipped(data):
    server = serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER)
    server.BroadcastEvent(commonConfig.BAUBLE_UNEQUIPPED_EVENT, data)
