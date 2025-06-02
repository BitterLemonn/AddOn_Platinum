from ..QuModLibs.Modules.Services.Globals import BaseEvent


class GetGlobalBaubleSlotInfoEvent(BaseEvent):
    def __init__(self, baubleSlotList):
        BaseEvent.__init__(self)
        self.baubleSlotList = baubleSlotList


class GetTargetBaubleSlotInfoEvent(BaseEvent):
    def __init__(self, playerId, baubleSlotList):
        BaseEvent.__init__(self)
        self.playerId = playerId
        self.baubleSlotList = baubleSlotList
