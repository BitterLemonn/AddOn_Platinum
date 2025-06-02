# -*- coding: utf-8 -*-
lambda: "By Zero123 TIME: 2024/05/06"

class _ItemBasicInfo:
    """ 基础物品信息 """
    class ITEM_CATEGORY:
        """ 创造模式栏分类 """
        CONSTRUCTION = "construction"
        """ 建筑 """
        NATURE = "nature"
        """ 自然 """
        EQUIPMENT = "equipment"
        """ 装备 """
        ITEMS = "items"
        """ 物品 """
        CUSTOM = "custom"
        """ 自定义 """
        UNKNOW = ""
        """ 未知不存在的 """

    class CUSTOM_TIPS:
        """ 自定义Tips"""
        ITEM_NAME = "%name%"
        """ 物品名称 """
        ITEM_TYPE = "%category%"
        """ 物品类型分页 """
        ITEM_ENCHANTING = "%enchanting%"
        """ 物品附魔信息 """
        ITEM_ATTACK_DAMAGE = "%attack_damage%"
        """ 攻击伤害 """

    def getArgs(self, itemName, auxValue, isEnchanted):
        return {}
        
    def __init__(self, itemName = "", auxValue = 0, isEnchanted = False):
        # type: (str, int, bool) -> None
        self.args = self.getArgs(itemName, auxValue, isEnchanted)
        self.itemName = ""          # type: str
        """ 本地化物品名称 """
        self.maxStackSize = 0       # type: int
        """ 最大堆叠数量 """
        self.maxDurability = 0      # type: int
        """ 最大耐久值 """
        self.itemCategory = ""      # type: str
        """ 创造模式栏分类 """
        self.itemType = ""          # type: str
        """ 物品类别 """
        self.weaponDamage = 0       # type: int
        """ 武器攻击力 """
        self.armorDefense = 0       # type: int
        """ 护甲防御力 """
        self.update()
    
    def update(self):
        if self.args == None:
            return
        self.itemName = self.args.get("itemName", "")
        self.maxStackSize = self.args.get("maxStackSize", 0)
        self.maxDurability = self.args.get("maxDurability", 0)
        self.itemCategory = self.args.get("itemCategory", "")
        self.itemType = self.args.get("itemType", "")
        self.weaponDamage = self.args.get("weaponDamage", 0)
        self.armorDefense = self.args.get("armorDefense", 0)

class _ItemData:
    NULL_ITEM = "minecraft:air"
    def __init__(self, dicArgs = {}, userId = None, index = -1):
        # type: (dict | None, str | None, int) -> None
        self._dicArgs = dicArgs
        self.index = index
        """ 物品下标索引 通常指背包位置 仅特定方法拿到的物品信息才会持有该属性 """
        self.userId = userId
        """ 用户ID 通常指持有者玩家 """
        self.empty = False          # type: bool
        """ 是否为空物品 当物品为空气/数量参数为0时视为空物品 """
        self.newItemName = ""       # type: str
        """ 物品标识符名称 """
        self.newAuxValue = 0        # type: int
        """ 物品附加值 """
        self.count = 0              # type: int
        """ 物品数量 """
        self.extraId = ""           # type: str
        """ 物品自定义标识符 """
        self.durability = 0         # type: int
        """ 剩余耐久值 若物品本身无耐久则始终为0 """
        self.customTips = ""        # type: str
        """ 自定义Tips说明 """
        self.userData = {}
        """ 物品userData 需主动表明获取userData否则始终为空 """
        self.enchantData = []
        """ 游戏原版附魔数据 暂不支持操作 """
        self.modEnchantData = []
        """ MOD自定义附魔数据 暂不支持操作 """
        self.itemUpdate()
    
    def getEnchantState(self):
        """ 获取是否为附魔状态 """
        return len(self.enchantData) > 0 or len(self.modEnchantData) > 0

    @classmethod
    def create(cls):
        return cls()
    
    def __str__(self):
        return "<{}.{} {} ({})>".format(self.__class__.__name__, id(self), self.getFormatItemName(), self.count)
    
    def getDict(self):
        """ 获取并拷贝一份dict参数 """
        if self._dicArgs == None:
            return self.__class__.createItemData(_ItemData.NULL_ITEM, 0).getDict()
        return {k:v for k, v in self._dicArgs.items()}
    
    def getJSONData(self):
        if self.empty:
            return None
        return self.getDict()
    
    @classmethod
    def createItemData(cls, itemName = "", count = 1, aux = 0):
        """ 快速创建一个简易物品参数 """
        return cls(
            {
                "newItemName": itemName,
                "itemName": itemName,
                "count": count,
                "aux": aux
            }
        )
    
    def equal(self, otherItem):
        # type: (_ItemData) -> bool
        """ 比较与另外一个物品是否相当 相同物品不同数据参数也会视为不同 """
        if otherItem.empty or self.empty:
            # 空物品不与任何物品相当
            return False
        return (
            otherItem.newItemName == self.newItemName and
            otherItem.newAuxValue == self.newAuxValue and
            otherItem.durability == self.durability and
            otherItem.customTips == self.customTips and
            otherItem.extraId == self.extraId and
            otherItem.userData == self.userData and
            otherItem.enchantData == self.enchantData and
            otherItem.modEnchantData == self.modEnchantData
        )
    
    def getFormatItemName(self):
        """ 获取格式化后的物品名称 统一空物品值 """
        if not self.newItemName:
            return _ItemData.NULL_ITEM
        return self.newItemName
    
    def getItemBasicInfo(self):
        # type: () -> _ItemBasicInfo
        """ 获取物品基础信息 """
        return _ItemBasicInfo(self.newItemName, self.newAuxValue)

    def itemUpdate(self):
        """ 更新计算物品属性 """
        dicArgs = self._dicArgs
        if dicArgs == None:
            self.empty = True
        else:
            self.newItemName = dicArgs.get("newItemName", "")
            if self.newItemName == _ItemData.NULL_ITEM:
                self.empty = True
                return
            self.newAuxValue = dicArgs.get("newAuxValue", 0)
            self.count = dicArgs.get("count", 0)
            if self.count <= 0:
                self.empty = True
                return
            self.extraId = dicArgs.get("extraId", "")
            self.durability = dicArgs.get("durability", 0)
            self.customTips = dicArgs.get("customTips", "")
            self.userData = dicArgs.get("userData", {})
            self.enchantData = dicArgs.get("enchantData", [])
            self.modEnchantData = dicArgs.get("modEnchantData", [])
    
    def setItemName(self, _itemName = None):
        """ 设置物品标识符 """
        if not _itemName or _itemName == _ItemData.NULL_ITEM:
            self.newItemName = _ItemData.NULL_ITEM
            self._dicArgs = None
            self.empty = True
            return
        if self._dicArgs == None:
            self._dicArgs = {}
        self._dicArgs["newItemName"] = _itemName
        self._dicArgs["itemName"] = _itemName
        if not "newAuxValue" in self._dicArgs:
            self._dicArgs["newAuxValue"] = 0
            self.newAuxValue = 0
        self.newItemName = _itemName
        self.itemUpdate()

    def setItemAux(self, _aux = 0):
        """ 设置物品Aux 空物品无效 """
        if self.empty:
            return False
        self.newAuxValue = _aux
        self._dicArgs["newAuxValue"] = _aux
        return True
    
    def nameIsNull(self, name = ""):
        return not name or name == _ItemData.NULL_ITEM
    
    def setCount(self, _count = 0):
        # type: (int) -> bool
        """ 设置物品数量 超过最大堆叠值将视为最大值 """
        if self.empty and self.nameIsNull(self.newItemName):
            return False
        maxCount = self.getItemBasicInfo().maxStackSize
        _count = min(maxCount, _count)
        self._dicArgs["count"] = _count
        self.count = _count
        if self.count <= 0:
            self.empty = True
        elif self.count > 0 and not self.nameIsNull(self.newItemName):
            self.empty = False
        return True
    
    def setDurability(self, _durability = 0):
        # type: (int) -> bool
        """ 设置物品耐久值 超过最大值将视为最大值 """
        if self.empty:
            return False
        maxValue = self.getItemBasicInfo().maxDurability
        _durability = min(_durability, maxValue)
        self._dicArgs["durability"] = _durability
        self.durability = _durability
        return True
    
    def setCustomTips(self, newCustomTips = ""):
        """ 设置物品自定义Tips """
        if self.empty:
            return False
        self._dicArgs["customTips"] = newCustomTips
        self.customTips = newCustomTips
    
    def setExtraId(self, _extraId = ""):
        """ 设置物品自定义标识符 """
        if self.empty:
            return False
        self.extraId = _extraId
        self._dicArgs["extraId"] = _extraId
    
    def setUserData(self, _userData = {}):
        """ 设置用户参数 根据文档说明该参数存放附魔 颜色等相关原版数据 请勿随意操作 """
        if self.empty:
            return False
        self.userData = _userData
        self._dicArgs["userData"] = _userData
    
    def getJSONExtraId(self):
        # type: () -> dict
        """ 获取extraId并转换为JSON """
        from json import loads
        try:
            return loads(self.extraId)
        except Exception:
            pass
        return {}

    def setJSONExtraId(self, joData = {}, ensureAscii = True):
        # type: (dict, bool) -> None
        """ 设置JSONExtraId """
        from json import dumps
        newStr = dumps(joData, ensure_ascii=ensureAscii)
        self.setExtraId(newStr)

class _InventoryData:
    """ 背包物品信息 """
    USE_ITEM_CLS = _ItemData
    def __init__(self, _size = 27, _userId = None):
        # type: (int, str | None) -> None
        self._size = _size
        """ 背包最大容量 """
        self._inventoryList = []    # type: list[_ItemData]
        """ 背包信息列表 """
        self._userId = _userId
        """ 用户ID 通常指持有者实体 """
    
    def __str__(self):
        return "<{}.{} {}>".format(self.__class__.__name__, id(self), [str(x) for x in self._inventoryList])
    
    def dumps(self):
        """ 返回格式化后的JSON数据 """
        return {
            "u": self._userId,
            "s": self._size,
            "i": [x.getJSONData() for x in self.walk()]
        }
    
    def moveItemTo(self, moveIndex, otherInventoryData, otherIndex = 0):
        # type: (int, _InventoryData, int) -> int
        """ 尝试将一栏物品移动到另外一个背包的特定位置 返回移动后剩余未移动成功的数值当数值为0视为完全移动完毕 """
        otherItemData = otherInventoryData.getItem(otherIndex)
        myItem = self.getItem(moveIndex)
        if myItem.empty:
            # 当前移动物品是空的 不允许移动操作
            return myItem.count
        if otherItemData.empty:
            # 对方背包物品为空 完整移动
            otherItemData.setCount(otherItemData.count + myItem.count)
            myItem.setCount(myItem.count - otherItemData.count)
            return myItem.count
        if not myItem.equal(otherItemData):
            # 两种物品截然不同禁止移动堆叠
            return myItem.count
        # 两种物品相同且都不为空并有一定默认数量
        beforeOtherCount = otherItemData.count    # 移动之前对方持有数量
        otherItemData.setCount(beforeOtherCount + myItem.count)
        afterOtherCount = otherItemData.count     # 移动之后对方持有数量
        useCount = afterOtherCount - beforeOtherCount
        myItem.setCount(myItem.count - useCount)
        return myItem.count

    def exchangeItemTo(self, myIndex, otherInventoryData, otherIndex = 0):
        # type: (int, _InventoryData, int) -> int
        """ 交换两个背包的物品无论类型是否相同 """
        otherItemData = otherInventoryData.getItem(otherIndex)
        myItem = self.getItem(myIndex)
        self._inventoryList[myIndex] = otherItemData
        otherInventoryData._inventoryList[otherIndex] = myItem
    
    def simulatedOperation(self, _index, toInventoryData, toIndex):
        # type: (int, _InventoryData, int) -> None
        """ 模拟操作背包物品 是moveItemTo与exchangeItemTo的整合
            @return - 将返回带有index操作后的 (原卡槽对象, Other卡槽对象, 状态码)

            状态码:
                0 移动叠加
                1 交换物品
        """
        myItem = self.getItem(_index)
        beforeCount = myItem.count      # 移动之前数量
        self.moveItemTo(_index, toInventoryData, toIndex)
        lastCount = myItem.count        # 移动后剩余数量
        state = 0                       # 操作状态
        if beforeCount == lastCount:
            # 没有任何成功性的移动 尝试交换物品
            self.exchangeItemTo(_index, toInventoryData, toIndex)
            state = 1
        return (self.getItem(_index), toInventoryData.getItem(toIndex), state)

    def moveSomeItemsTo(self, moveIndex, moveMaxCount, otherInventoryData, otherIndex = 0):
        # type: (int, int, _InventoryData, int) -> int
        """ 尝试将一部分物品移动到另外一个背包的特定位置 模拟长按移动部分物品操作 """
        myItem = self.getItem(moveIndex)
        if myItem.count <= moveMaxCount:
            # 待移动的总数量小于最大移动数量 直接完整移动
            return self.moveItemTo(moveIndex, otherInventoryData, otherIndex)
        oldCount = myItem.count                 # 原先数量
        myItem.setCount(moveMaxCount)           # 设置为需要移动数量
        notUseCount = oldCount - myItem.count   # 未选中移动数量
        _back = self.moveItemTo(moveIndex, otherInventoryData, otherIndex)  # 移动后剩余数量
        myItem.setCount(notUseCount + _back)    # 合并剩余原物品数量
        return myItem.count
    
    @classmethod
    def loads(cls, _json):
        # type: (dict) -> _InventoryData
        """ 从JSON数据加载回对象 """
        _userId = _json.get("u", None)
        _size = _json.get("s", 0)
        _inventoryList = _json.get("i", [])
        iv = cls.loadItemDictList(_inventoryList, _userId)
        iv._size = _size
        return iv

    @classmethod
    def loadItemDictList(cls, itemDictList = [], userId = None):
        # type: (list[dict | None], str | None) -> _InventoryData
        """ 加载物品字典列表 """
        inventoryData = cls(len(itemDictList), userId)
        for itemDict in itemDictList:
            inventoryData._inventoryList.append(
                cls.USE_ITEM_CLS(itemDict, userId)
            )
        return inventoryData

    @classmethod
    def createOptInventoryDataWithIndexItems(cls, *args):
        # type: (_ItemData) -> _InventoryData
        """ 基于一部分带有index上下文的物品构造一个临时背包用于操作 对于提供的ItemData将视为待操作对象 因此会强制认定为非empty """
        maxLength = 0
        for obj in args:
            maxLength = max(obj.index + 1, maxLength)
        newInventory = cls(maxLength)
        newInventory.initItemList()
        for itemData in args:
            newObj = None
            if itemData.empty:
                newObj = cls.USE_ITEM_CLS.createItemData(
                    _ItemData.NULL_ITEM, 0
                )
            else:
                newObj = cls.USE_ITEM_CLS(
                    itemData.getDict()
                )
            newInventory._inventoryList[itemData.index] = newObj
            newObj.empty = False
            newObj.index = itemData.index
        return newInventory

    def getItemsDictMap(self, itemPosType = 0, leaveBlankValues = False):
        # type: (int, bool) -> dict[tuple[int, int], dict]
        """ 获取批物品字典
            leaveBlankValues 设置为True时将会保留空物品
        """
        itemDictMap = {}
        for obj in self.walk():
            if not leaveBlankValues and obj.empty:
                continue
            itemDictMap[(itemPosType, obj.index)] = obj.getDict()
        return itemDictMap

    def initItemList(self):
        """ 初始化物品列表 当列表元素数目与总背包数目不足时将会补足为空 """
        for _ in range(len(self._inventoryList), self._size):
            self._inventoryList.append(self.createNullItem())
    
    def walk(self):
        """ 返回一个物品背包生成器以便遍历操作 """
        for i in range(self._size):
            yield self.getItem(i)
    
    def getItem(self, _index):
        # type: (int) -> _ItemData
        """ 基于下标索引获取物品 """
        if _index >= self._size:
            raise Exception("超出背包物品最大值")
        if _index >= len(self._inventoryList):
            # 索引超出列表持有范围 进行补全
            self.initItemList()
        itemData = self._inventoryList[_index]
        itemData.index = _index
        return itemData
    
    def createNullItem(self):
        """ 创建一个空物品对象 """
        return self.__class__.USE_ITEM_CLS.createItemData(_ItemData.NULL_ITEM, 0)