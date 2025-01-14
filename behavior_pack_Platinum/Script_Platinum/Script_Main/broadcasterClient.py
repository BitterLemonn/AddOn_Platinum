from ..QuModLibs.Client import *
from ..QuModLibs.Modules.Services.Client import BaseService
from .. import commonConfig


class BroadcasterClient(clientApi.GetClientSystemCls()):

    def __init__(self, namespace, name):
        super(BroadcasterClient, self).__init__(namespace, name)


@BaseService.Init
class BroadcasterClientService(BaseService):

    def __init__(self):
        BaseService.__init__(self)

    @BaseService.REG_API("platinum/onBaubleTakeOff")
    def onBaubleTakeOff(self, data):
        client = clientApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_CLIENT)
        client.BroadcastEvent(commonConfig.BAUBLE_UNEQUIPPED_EVENT, data)

    @BaseService.REG_API("platinum/onBaublePutOn")
    def onBaublePutOn(self, data):
        client = clientApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_CLIENT)
        client.BroadcastEvent(commonConfig.BAUBLE_EQUIPPED_EVENT, data)
