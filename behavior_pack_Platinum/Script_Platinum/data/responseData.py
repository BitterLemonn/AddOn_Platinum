# coding=utf-8
from Script_Platinum.data.itemStack import ItemStack


class _BaseResponseData(object):

    def toDict(self):
        def _toDict(obj):
            if isinstance(obj, dict):
                return {k: _toDict(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [_toDict(v) for v in obj]
            if isinstance(obj, tuple):
                return tuple(_toDict(v) for v in obj)
            if hasattr(obj, "toDict") and callable(obj.toDict):
                return obj.toDict()
            if hasattr(obj, "__dict__") and not isinstance(obj, type):
                return {k: _toDict(v) for k, v in obj.__dict__.items()}
            return obj

        return {k: _toDict(v) for k, v in self.__dict__.items()}


class BaubleCheckResponseData(_BaseResponseData):

    def __init__(self, suc, baubleInfo=None, slotId=None, index=-1, **kwargs):
        self.suc = suc
        self.baubleInfo = baubleInfo  # type: ItemStack
        self.slotId = slotId
        self.index = index

    @classmethod
    def fromDict(cls, data):
        baubleInfo = data.get("baubleInfo")
        if isinstance(baubleInfo, dict):
            baubleInfo = ItemStack.fromDict(baubleInfo)
        return cls(suc=data.get("suc"), baubleInfo=baubleInfo, slotId=data.get("slotId"), index=data.get("index", -1))
