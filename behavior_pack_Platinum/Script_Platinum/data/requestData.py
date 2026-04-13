# coding=utf-8


class BaubleCheckRequestData(object):

    def __init__(self, baubleInfo, slotId, slotType, index=-1, **kwargs):
        self.baubleInfo = baubleInfo
        self.slotId = slotId
        self.slotType = slotType
        self.index = index
