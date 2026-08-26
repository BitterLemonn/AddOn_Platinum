# coding=utf-8


class BaubleEventData(object):

    def __init__(self, playerId, baubleSlotId, baubleSlotType, slotIndex, itemStack, isFirstLoad=False):
        self.baubleSlotId = baubleSlotId
        self.baubleSlot = baubleSlotType
        self.slotIndex = slotIndex
        self.itemDict = itemStack.toDict() if itemStack is not None else None
        self.isFirstLoad = isFirstLoad
        self.playerId = playerId

    def dumpToDict(self):
        return self.__dict__


class EntityBaubleEventData(object):

    def __init__(self, entityId, baubleSlotId, baubleSlotType, slotIndex, itemStack, isFirstLoad=False):
        self.baubleSlotId = baubleSlotId
        self.baubleSlot = baubleSlotType
        self.slotIndex = slotIndex
        self.itemDict = itemStack.toDict() if itemStack is not None else None
        self.isFirstLoad = isFirstLoad
        self.entityId = entityId

    def dumpToDict(self):
        return self.__dict__


class EntityBaubleDropEventData(object):

    def __init__(self, entityId, itemList, cancel=False):
        self.entityId = entityId
        self.itemList = itemList
        self.cancel = cancel

    def dumpToDict(self):
        return self.__dict__


class BaubleInfoData(object):

    def __init__(self, baubleId, slotType, customTips=None, **kwargs):
        self.baubleId = baubleId
        self.slotType = slotType
        self.customTips = customTips
