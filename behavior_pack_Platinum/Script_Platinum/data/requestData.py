# coding=utf-8


from Script_Platinum.data.responseData import ItemStack


class _BaseRequestData(object):

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


class BaubleCheckRequestData(_BaseRequestData):

    def __init__(self, baubleInfo, slotId, slotType, index=-1, **kwargs):
        self.baubleInfo = baubleInfo  # type: ItemStack
        self.slotId = slotId
        self.slotType = slotType
        self.index = index

    @classmethod
    def fromDict(cls, data):
        baubleInfo = data.get("baubleInfo")
        if isinstance(baubleInfo, dict):
            baubleInfo = ItemStack.fromDict(baubleInfo)
        return cls(
            baubleInfo=baubleInfo, slotId=data.get("slotId"), slotType=data.get("slotType"), index=data.get("index", -1)
        )


class ChangeBaubleRequestData(_BaseRequestData):

    def __init__(self, baubleInfo, slotId, index=-1, **kwargs):
        self.baubleInfo = baubleInfo  # type: ItemStack
        self.slotId = slotId
        self.index = index

    @classmethod
    def fromDict(cls, data):
        baubleInfo = data.get("baubleInfo")
        if isinstance(baubleInfo, dict):
            baubleInfo = ItemStack.fromDict(baubleInfo)
        return cls(baubleInfo=baubleInfo, slotId=data.get("slotId"), index=data.get("index", -1))
