from ..QuModLibs.Client import *
from .. import CommonConfig

class BroadcasterClient(clientApi.GetClientSystemCls()):

    def __init__(self, namespace, name):
        super(BroadcasterClient, self).__init__(namespace, name)


@AllowCall
def BaubleEquipped(data):
    client = clientApi.GetSystem(CommonConfig.PLATINUM_NAMESPACE, CommonConfig.PLATINUM_BROADCAST_CLIENT)
    client.BroadcastEvent(CommonConfig.BAUBLE_EQUIPPED_EVENT, data)


@AllowCall
def BaubleUnequipped(data):
    client = clientApi.GetSystem(CommonConfig.PLATINUM_NAMESPACE, CommonConfig.PLATINUM_BROADCAST_CLIENT)
    client.BroadcastEvent(CommonConfig.BAUBLE_UNEQUIPPED_EVENT, data)
