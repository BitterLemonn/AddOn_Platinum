# -*- coding: utf-8 -*-


class ItemStack(object):
    def __init__(self, name="", count=0, aux=0, userData=None):
        self.name = name
        self.count = count
        self.aux = aux
        self.maxStackSize = 64  # 默认最大堆叠64，特殊物品可覆盖
        self.userData = userData

        self._checkMaxStackSize()

    @classmethod
    def fromDict(cls, data):
        itemStack = cls()
        if data is None:
            return itemStack
        itemStack.name = data.get("newItemName", "")
        itemStack.count = data.get("count", 0)
        itemStack.aux = data.get("newAuxValue", 0)
        itemStack.userData = data.get("userData", None)
        return itemStack

    def _checkMaxStackSize(self):
        if self.name in maxStackStore:
            self.maxStackSize = maxStackStore[self.name]

    def toDict(self):
        return {"newItemName": self.name, "count": self.count, "newAuxValue": self.aux, "userData": self.userData}

    def isEnchanted(self):
        from Script_Platinum.utils import ItemFactory

        return len(ItemFactory.fromDict(self.toDict()).getAllEnchantments() or []) > 0

    def isEmpty(self):
        return self.count <= 0 or self.name == "" or self.name is None

    def isFull(self):
        return self.count >= self.maxStackSize

    def isSameItem(self, other, isIgnoreUserData=False):
        if other is None:
            return False
        selfUserData = self.userData if self.userData is not None else {}
        otherUserData = other.userData if other.userData is not None else {}
        selfAux = self.aux if self.aux is not None and self.aux != 32767 else 0
        otherAux = other.aux if other.aux is not None and other.aux != 32767 else 0
        if isIgnoreUserData:
            selfUserData = {}
            otherUserData = {}
        return self.name == other.name and selfAux == otherAux and selfUserData == otherUserData

    def clone(self):
        newStack = ItemStack()
        newStack.name = self.name
        newStack.count = self.count
        newStack.aux = self.aux
        newStack.userData = self.userData.copy() if isinstance(self.userData, dict) else self.userData
        newStack.maxStackSize = self.maxStackSize
        return newStack


maxStackStore = {}
