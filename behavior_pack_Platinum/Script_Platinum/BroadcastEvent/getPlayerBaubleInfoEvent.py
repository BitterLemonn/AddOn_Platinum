from ..QuModLibs.Modules.Services.Globals import BaseEvent


class GetPlayerBaubleInfoServerEvent(BaseEvent):
    def __init__(self, playerId, baubleDict):
        BaseEvent.__init__(self)
        self.playerId = playerId
        self.baubleDict = baubleDict
