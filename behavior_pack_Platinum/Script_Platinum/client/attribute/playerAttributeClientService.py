# coding=utf-8
from Script_Platinum.QuModLibs.Client import compFactory, playerId
from Script_Platinum.QuModLibs.Modules.Services.Client import BaseService, QRequests


@BaseService.Init
class PlayerAttributeClientService(BaseService):
    """客户端属性同步服务。"""

    @BaseService.REG_API("client/attribute/syncPickRange")
    def syncPickRange(self, data):  # type: (dict | QRequests.RequestResults) -> bool
        if isinstance(data, QRequests.RequestResults):
            data = data.data
        if not isinstance(data, dict):
            return False
        pickRange = data.get("pickRange")
        if pickRange is None:
            return False
        targetPlayerId = data.get("playerId") or playerId
        playerComp = compFactory.CreatePlayer(targetPlayerId)
        if playerComp:
            return bool(playerComp.SetPickRange(float(pickRange)))
        return False
