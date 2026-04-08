# coding=utf-8


class BaubleSlotData(object):
    def __init__(self, name, placeholderPath, identifier, slotType, isDefault=False, **kwargs):
        self.name = name
        self.placeholderPath = placeholderPath
        self.identifier = identifier
        self.slotType = slotType
        self.isDefault = isDefault

    @classmethod
    def fromDict(cls, data):
        return cls(
            name=data.get("baubleSlotName", ""),
            placeholderPath=data.get("placeholderPath", ""),
            identifier=data.get("baubleSlotIdentifier", ""),
            slotType=data.get("baubleSlotType", ""),
            isDefault=data.get("isDefault", False),
        )
