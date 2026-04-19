# coding=utf-8


class BaubleSlotData(object):
    def __init__(self, name, placeholderPath, identifier, slotType, isDefault=False, isCommandAdded=False, **kwargs):
        self.name = name
        self.placeholderPath = placeholderPath
        self.identifier = identifier
        self.slotType = slotType
        self.isDefault = isDefault
        self.isCommandAdded = isCommandAdded

    @classmethod
    def fromDict(cls, data):
        return cls(
            name=data.get("name", None),
            placeholderPath=data.get("placeholderPath", ""),
            identifier=data.get("identifier", None),
            slotType=data.get("slotType", None),
            isDefault=data.get("isDefault", False),
            isCommandAdded=data.get("isCommandAdded", False),
        )

    def __str__(self):
        return "BaubleSlotData(name={}, placeholderPath={}, identifier={}, slotType={}, isDefault={}, isCommandAdded={})".format(
            self.name, self.placeholderPath, self.identifier, self.slotType, self.isDefault, self.isCommandAdded
        )
