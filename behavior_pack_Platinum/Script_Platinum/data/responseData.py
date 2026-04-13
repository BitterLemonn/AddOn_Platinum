# coding=utf-8
from Script_Platinum.data.itemStack import ItemStack


class BaubleCheckResponseData(object):

    def __init__(self, suc, baubleInfo=None, slotId=None, index=-1, **kwargs):
        self.suc = suc
        self.baubleInfo = self._parseBaubleInfo(baubleInfo)  # type: ItemStack
        self.slotId = slotId
        self.index = index
        self.__dict__ = {
            'suc': self.suc,
            'baubleInfo': self.baubleInfo.toDict(),
            'slotId': self.slotId,
            'index': self.index,
        }

    def _parseBaubleInfo(self, baubleInfo):
        if isinstance(baubleInfo, dict):
            return ItemStack.fromDict(baubleInfo)
        return baubleInfo
