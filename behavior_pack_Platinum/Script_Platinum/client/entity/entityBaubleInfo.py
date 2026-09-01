# coding=utf-8
from Script_Platinum import commonConfig
from Script_Platinum.QuModLibs.Client import clientApi
from Script_Platinum.QuModLibs.Modules.Services.Client import BaseService


@BaseService.Init
class EntityBaubleInfoClientService(BaseService):

    @BaseService.REG_API("client/bauble/unequipEntityBaubleBoardcast")
    def takeOffEntityBaubleBoardcast(self, data):  # type: (dict) -> None
        boardCastSys = clientApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_CLIENT)
        if boardCastSys:
            boardCastSys.BroadcastEvent(commonConfig.ENTITY_BAUBLE_UNEQUIPPED_EVENT, data)

    @BaseService.REG_API("client/bauble/equipEntityBaubleBoardcast")
    def equipEntityBaubleBoardcast(self, data):  # type: (dict) -> None
        boardCastSys = clientApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_CLIENT)
        if boardCastSys:
            boardCastSys.BroadcastEvent(commonConfig.ENTITY_BAUBLE_EQUIPPED_EVENT, data)
