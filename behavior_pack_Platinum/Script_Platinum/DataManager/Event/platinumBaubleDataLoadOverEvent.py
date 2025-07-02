from ...QuModLibs.Modules.Services.Client import BaseEvent


class PlatinumBaubleDataLoadOverEvent(BaseEvent):

    def __init__(self, playerId):
        BaseEvent.__init__(self)
        self.playerId = playerId
