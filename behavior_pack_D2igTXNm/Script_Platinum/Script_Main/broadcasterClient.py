from ..QuModLibs.Client import *
from .. import commonConfig


class BroadcasterClient(clientApi.GetClientSystemCls()):

    def __init__(self, namespace, name):
        super(BroadcasterClient, self).__init__(namespace, name)


@AllowCall
def BaubleEquipped(data):
    client = clientApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_CLIENT)
    client.BroadcastEvent(commonConfig.BAUBLE_EQUIPPED_EVENT, data)


@AllowCall
def BaubleUnequipped(data):
    client = clientApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_CLIENT)
    client.BroadcastEvent(commonConfig.BAUBLE_UNEQUIPPED_EVENT, data)
