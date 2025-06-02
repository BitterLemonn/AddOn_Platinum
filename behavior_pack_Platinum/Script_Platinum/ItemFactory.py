# coding=utf-8
import developLogging as logging


class NBTTransformer(object):
    class DataType(object):
        INT = 1
        SHORT = 2
        INT64 = 3
        FLOAT = 4
        DOUBLE = 5

    @classmethod
    def transform(cls, data, dataType=DataType.INT):
        if isinstance(data, bool):
            return {"__type__": 1, "__value__": data}
        elif isinstance(data, int):
            if dataType == cls.DataType.SHORT:
                return {"__type__": 2, "__value__": data}
            elif dataType == cls.DataType.INT:
                return {"__type__": 3, "__value__": data}
            else:
                return {"__type__": 4, "__value__": data}
        elif isinstance(data, float):
            dataType = cls.DataType.FLOAT if dataType == cls.DataType.INT else dataType
            if dataType == cls.DataType.FLOAT:
                return {"__type__": 5, "__value__": data}
            else:
                return {"__type__": 6, "__value__": data}
        elif isinstance(data, list):
            first = data[0]
            if isinstance(first, bool):
                return {"__type__": 7, "__value__": data}
            elif isinstance(first, int):
                return {"__type__": 11, "__value__": data}
            else:
                dataList = []
                for item in data:
                    dataList.append(cls.transform(item))
                return {"__type__": 9, "__value__": dataList}
        elif isinstance(data, dict):
            dataDict = {}
            for key, value in data.items():
                dataDict[key] = cls.transform(value)
            return dataDict
        elif isinstance(data, str):
            return {"__type__": 8, "__value__": data}
        return None

    @classmethod
    def parse(cls, nbtData):
        # type: (dict) -> Any
        value = nbtData["__value__"]
        return value

    @classmethod
    def parseList(cls, nbtDataList):
        # type: (list[dict]) -> list
        dataList = []
        for nbtData in nbtDataList:
            dataList.append(cls.parse(nbtData))
        return dataList

    @classmethod
    def parseDict(cls, nbtDataDict):
        # type: (dict) -> dict
        dataDict = {}
        for key, nbtData in nbtDataDict.items():
            dataDict[key] = cls.parse(nbtData)
        return dataDict


class EnchantmentData(object):
    def __init__(self, enchId, level):
        self.id = enchId
        self.level = level


class TrimPattern(object):
    SENTRY = "sentry"
    DUNE = "dune"
    COAST = "coast"
    WILD = "wild"
    WARD = "ward"
    EYE = "eye"
    VEX = "vex"
    TIDE = "tide"
    SNOUT = "snout"
    RIB = "rib"
    SPIRE = "spire"
    SILENCE = "silence"
    WAYFINDER = "wayfinder"
    RAISER = "raiser"
    SHAPER = "shaper"
    HOST = "host"
    # 1.21
    # BOLT = "bolt"
    # FLOW = "flow"


class TrimMaterial(object):
    AMETHYST = "amethyst"
    COPPER = "copper"
    DIAMOND = "diamond"
    EMERALD = "emerald"
    GOLD = "gold"
    IRON = "iron"
    LAPIS = "lapis"
    NETHERITE = "netherite"
    QUARTZ = "quartz"
    REDSTONE = "redstone"
    # 1.21
    # AMBER = "amber"


class ItemFactory(object):
    class __UserDataFactory(object):

        def __init__(self, itemDict=None):
            self.__userDataDict = itemDict.get("userData", None) if itemDict else None

            # ------- display 层 -------
            self.__display = self.__userDataDict.get("display", {}) if self.__userDataDict else {}  # type: dict
            self.__lore = self.__display.get("Lore", None)  # type: list or None
            self.__name = self.__display.get("Name", None)  # type: str or None
            # ---------- ench 层 ----------
            self.__ench = self.__userDataDict.get("ench", None) if self.__userDataDict else None  # type: list or None
            # ---------- trim 层 ----------
            self.__trim = self.__userDataDict.get("Trim", None) if self.__userDataDict else None  # type: dict or None
            self.__pattern = self.__trim.get("Pattern", None) if self.__trim else None  # type: str or None
            self.__material = self.__trim.get("Material", None) if self.__trim else None  # type: str or None
            # --------- repairCost 层 ---------
            self.__repairCost = self.__userDataDict.get("RepairCost",
                                                        None) if self.__userDataDict else None  # type: dict or None
            # --------- extraId 层 ---------
            self.__extraId = self.__userDataDict.get("ItemExtraID",
                                                     None) if self.__userDataDict else None  # type: str or None
            # --------- customTips 层 ---------
            self.__customTips = self.__userDataDict.get("ItemCustomTips",
                                                        None) if self.__userDataDict else None  # type: str or None
            # ---------- customData 层 ----------
            self.__customData = self.__userDataDict.get("LemonCustomData", None) \
                if self.__userDataDict else None  # type: dict

        @staticmethod
        def __enchToNBTdata(enchData):
            # type: (EnchantmentData) -> dict
            enchId = enchData.id
            level = enchData.level
            if isinstance(enchId, int):
                return {"id": NBTTransformer.transform(enchId, NBTTransformer.DataType.SHORT),
                        "lvl": NBTTransformer.transform(level, NBTTransformer.DataType.SHORT)}
            else:
                return {"modEnchant": NBTTransformer.transform(enchId),
                        "id": NBTTransformer.transform(255, NBTTransformer.DataType.SHORT),
                        "lvl": NBTTransformer.transform(level, NBTTransformer.DataType.SHORT)}

        @classmethod
        def fromDict(cls, userDataDict):
            return cls(userDataDict)

        def setLore(self, lore):
            self.__lore = [NBTTransformer.transform(lore)]
            return self

        def setLores(self, lores):
            self.__lore = [NBTTransformer.transform(lore) for lore in lores]
            return self

        def addLore(self, lore, index=None):
            if not self.__lore:
                self.__lore = []
            if index is None:
                self.__lore.append(NBTTransformer.transform(lore))
            else:
                self.__lore.insert(index, NBTTransformer.transform(lore))
            return self

        def addLores(self, lores, index=None):
            if not self.__lore:
                self.__lore = []
            lores = [NBTTransformer.transform(lore) for lore in lores]
            if index is None:
                self.__lore.extend(lores)
            else:
                for i, lore in enumerate(lores):
                    self.__lore.insert(index + i, lore)
            return self

        def removeLore(self, index):
            if not self.__lore:
                return self
            self.__lore.pop(index)
            if not self.__lore:
                self.__lore = None
            return self

        def removeAllLores(self):
            self.__lore = None
            return self

        def setName(self, name):
            self.__name = NBTTransformer.transform(name)
            return self

        def removeName(self):
            self.__name = None
            return self

        def setCustomTips(self, customTips):
            self.__customTips = NBTTransformer.transform(customTips)
            return self

        def removeCustomTips(self):
            self.__customTips = None
            return self

        def setExtraId(self, extraId):
            self.__extraId = NBTTransformer.transform(extraId)
            return self

        def removeExtraId(self):
            self.__extraId = None
            return self

        def setEnchantments(self, enchList):
            """
            :type enchList: list[EnchantmentData]
            :param enchList: 附魔列表
            :rtype: ItemFactory.__UserDataFactory
            """
            if not self.__ench:
                self.__ench = []

            for ench in enchList:
                self.__ench.append(self.__enchToNBTdata(ench))
            return self

        def addEnchantment(self, enchData):
            """
            :type enchData: EnchantmentData
            :param enchData: 附魔数据
            :rtype: ItemFactory.__UserDataFactory
            """
            if not self.__ench:
                self.__ench = []

            self.__ench.append(self.__enchToNBTdata(enchData))
            return self

        def addEnchantments(self, enchList):
            """
            :type enchList: list[EnchantmentData]
            :param enchList: 附魔列表
            :rtype: ItemFactory.__UserDataFactory
            """
            if not self.__ench:
                self.__ench = []

            for ench in enchList:
                self.__ench.append(self.__enchToNBTdata(ench))
            return self

        def removeEnchantment(self, enchId):
            """
            :type enchId: int
            :param enchId: 附魔ID
            :rtype: ItemFactory.__UserDataFactory
            """
            if not self.__ench:
                return self

            for i, enchData in enumerate(self.__ench):
                if isinstance(enchId, int):
                    if enchData["id"]["__value__"] == enchId:
                        self.__ench.pop(i)
                        break
                else:
                    if enchData["modEnchant"]["__value__"] == enchId:
                        self.__ench.pop(i)
                        break
            if not self.__ench:
                self.__ench = None
            return self

        def removeAllEnchantments(self):
            self.__ench = None
            return self

        def setTrim(self, pattern, material):
            self.__pattern = NBTTransformer.transform(pattern)
            self.__material = NBTTransformer.transform(material)
            self.__trim = {"Pattern": self.__pattern, "Material": self.__material}
            return self

        def removeTrim(self):
            self.__trim = None
            return self

        def setRepairCost(self, repairCost):
            self.__repairCost = None if repairCost == 0 else NBTTransformer.transform(repairCost)
            return self

        def removeRepairCost(self):
            self.__repairCost = None
            return self

        def setCustomData(self, data):
            self.__customData = NBTTransformer.transform(data)
            return self

        def addCustomData(self, data):
            if not self.__customData:
                self.__customData = {}
            data = NBTTransformer.transform(data)
            self.__customData.update(data)
            return self

        def removeCustomData(self, key):
            if not self.__customData:
                return self
            customData = NBTTransformer.parseDict(self.__customData)
            customData.pop(key)
            self.__customData = NBTTransformer.transform(customData)
            return self

        def removeAllCustomData(self):
            self.__customData = None
            return self

        def build(self):
            userData = self.__userDataDict if self.__userDataDict else {}
            # ---- display 层 ----
            if self.__lore:
                self.__display["Lore"] = self.__lore
            else:
                self.__display.pop("Lore", None)
            if self.__name:
                self.__display["Name"] = self.__name
            else:
                self.__display.pop("Name", None)

            if self.__display != {}:
                userData["display"] = self.__display
            else:
                userData.pop("display", None)

            # ---- ench 层 ----
            if self.__ench:
                enchDataList = []
                for enchData in self.__ench:
                    enchDataList.append(enchData)
                userData["ench"] = enchDataList
            else:
                userData.pop("ench", None)

            # ---- trim 层 ----
            if self.__trim:
                userData["Trim"] = self.__trim
            else:
                userData.pop("Trim", None)

            # ---- repairCost 层 ----
            if self.__repairCost:
                userData["RepairCost"] = self.__repairCost
            else:
                userData.pop("RepairCost", None)

            # ---- customTips 层 ----
            if self.__customTips:
                userData["ItemCustomTips"] = self.__customTips
            else:
                userData.pop("ItemCustomTips", None)

            # ---- extraId 层 ----
            if self.__extraId:
                userData["ItemExtraID"] = self.__extraId
            else:
                userData.pop("ItemExtraID", None)

            # ---- customData 层 ----
            if self.__customData:
                userData["LemonCustomData"] = self.__customData
            else:
                userData.pop("LemonCustomData", None)

            return userData

        def getName(self):
            # type: () -> str or None
            name = NBTTransformer.parse(self.__name) if self.__name else None
            return name

        def getLores(self):
            lores = NBTTransformer.parseList(self.__lore) if self.__lore else None
            return lores

        def getEnchantLevel(self, enchId):
            if not self.__ench:
                return 0
            enchDataList = []
            for enchData in self.__ench:
                enchDataList.append(NBTTransformer.parseDict(enchData))
            for enchData in enchDataList:
                if isinstance(enchId, int):
                    if enchData["id"] == enchId:
                        return enchData["lvl"]
                else:
                    if enchData["modEnchant"] == enchId:
                        return enchData["lvl"]
            return 0

        def getAllEnchantments(self):
            if not self.__ench:
                return None
            enchDataList = []
            for enchData in self.__ench:
                enchDataList.append(NBTTransformer.parseDict(enchData))
            return enchDataList

        def getTrim(self):
            if self.__trim:
                return NBTTransformer.parseDict(self.__trim)
            return None

        def getRepairCost(self):
            if self.__repairCost:
                return NBTTransformer.parse(self.__repairCost)
            return 0

        def getCustomTips(self):
            if self.__customTips:
                return NBTTransformer.parse(self.__customTips)
            return None

        def getCustomData(self):
            if self.__customData:
                return NBTTransformer.parseDict(self.__customData)
            return None

    def __init__(self, itemDict=None):
        self.__itemDict = itemDict if itemDict else {"newItemName": "minecraft:air", "newAuxValue": 0, "count": 1}

        self.__itemName = self.__itemDict["newItemName"]  # type: str
        self.__auxValue = self.__itemDict["newAuxValue"]  # type: int
        self.__count = self.__itemDict["count"]  # type: int
        self.__durability = self.__itemDict.get("durability", None)  # type: int or None

        self.__userData = self.__UserDataFactory.fromDict(self.__itemDict)  # type: ItemFactory.__UserDataFactory

    @classmethod
    def fromDict(cls, itemDict):
        return cls(itemDict)

    # ------------------
    # ---- modifier ----
    # ------------------
    def setCount(self, count):
        """
        设置物品数量
        :type count: int
        :param count: 物品数量
        :return: ItemFactory
        """
        self.__count = count
        return self

    def setAuxValue(self, auxValue):
        """
        设置物品附加值
        :type auxValue: int
        :param auxValue: 物品附加值
        :return: ItemFactory
        """
        self.__auxValue = auxValue
        return self

    def setItemName(self, itemName):
        """
        设置物品名称
        :type itemName: str
        :param itemName: 物品名称
        :return: ItemFactory
        """
        self.__itemName = itemName
        return self

    def setDurability(self, durability):
        """
        设置物品耐久度
        :type durability: int
        :param durability: 物品耐久度
        :return: ItemFactory
        """
        self.__durability = durability
        return self

    def setLore(self, lore):
        """
        设置物品描述
        :type lore: str
        :param lore: 物品描述
        :return: ItemFactory
        """
        self.__userData.setLore(lore)
        return self

    def setLores(self, lores):
        """
        设置物品描述
        :type lores: list[str]
        :param lores: 物品描述列表
        :return: ItemFactory
        """
        self.__userData.setLores(lores)
        return self

    def addLore(self, lore, index=None):
        """
        添加物品描述
        :type lore: str
        :type index: int
        :param lore: 物品描述
        :param index: [可选] 描述插入位置
        :return: ItemFactory
        """
        self.__userData.addLore(lore, index)
        return self

    def addLores(self, lores, index=None):
        """
        添加物品描述列表
        :type lores: list[str]
        :type index: int
        :param lores: 物品描述列表
        :param index: [可选] 描述插入位置
        :return: ItemFactory
        """
        self.__userData.addLores(lores, index)
        return self

    def removeLore(self, index):
        """
        删除物品描述
        :param index: 描述位置
        :return: ItemFactory
        """
        self.__userData.removeLore(index)
        return self

    def removeAllLores(self):
        """
        删除所有物品描述
        :return: ItemFactory
        """
        self.__userData.removeAllLores()
        return self

    def setName(self, name):
        """
        设置物品自定义名称
        :type name: str
        :param name: 物品自定义名称
        :return: ItemFactory
        """
        self.__userData.setName(name)
        return self

    def removeName(self):
        """
        删除物品自定义名称
        :return: ItemFactory
        """
        self.__userData.removeName()
        return self

    def setCustomTips(self, customTips):
        """
        设置物品自定义提示 (覆盖原有信息)
        :type customTips: str
        :param customTips: 物品自定义提示
        :return: ItemFactory
        """
        self.__userData.setCustomTips(customTips)
        return self

    def removeCustomTips(self):
        """
        删除物品自定义提示
        :return: ItemFactory
        """
        self.__userData.removeCustomTips()
        return self

    def setExtraId(self, extraId):
        """
        设置物品额外ID
        :type extraId: str
        :param extraId: 物品额外ID
        :return: ItemFactory
        """
        self.__userData.setExtraId(extraId)
        return self

    def removeExtraId(self):
        """
        删除物品额外ID
        :return: ItemFactory
        """
        self.__userData.removeExtraId()
        return self

    def setEnchantments(self, enchList):
        """
        设置物品附魔
        :type enchList: list[EnchantmentData]
        :param enchList: 附魔列表
        :return: ItemFactory
        """
        self.__userData.setEnchantments(enchList)
        return self

    def addEnchantment(self, enchId, level):
        """
        添加物品附魔
        :type enchId: int or str
        :type level: int
        :return: ItemFactory
        """
        self.__userData.addEnchantment(EnchantmentData(enchId, level))
        return self

    def addEnchantments(self, enchList):
        """
        添加物品附魔
        :type enchList: list[EnchantmentData]
        :param enchList: 附魔列表
        :return: ItemFactory
        """
        self.__userData.addEnchantments(enchList)
        return self

    def removeEnchantment(self, enchId):
        """
        删除物品附魔
        :type enchId: int
        :param enchId: 附魔ID
        :return: ItemFactory
        """
        self.__userData.removeEnchantment(enchId)
        return self

    def removeAllEnchantments(self):
        """
        删除所有物品附魔
        :return: ItemFactory
        """
        self.__userData.removeAllEnchantments()
        return self

    def setTrim(self, pattern, material):
        """
        添加盔甲纹饰 (模组装备无效)
        :type pattern: str
        :type material: str
        :param pattern: 纹饰图案
        :param material: 纹饰材料
        :return: ItemFactory
        """
        self.__userData.setTrim(pattern, material)
        return self

    def removeTrim(self):
        """
        删除盔甲纹饰 (模组装备无效)
        :return: ItemFactory
        """
        self.__userData.removeTrim()
        return self

    def setRepairCost(self, repairCost):
        """
        设置铁砧惩罚 (当惩罚 >= 39 时, 生存模式下无法使用铁砧进行除重命名以外的操作)
        :type repairCost: int
        :param repairCost: 修复花费
        :return: ItemFactory
        """
        self.__userData.setRepairCost(repairCost)
        return self

    def removeRepairCost(self):
        """
        删除铁砧惩罚
        :return: ItemFactory
        """
        self.__userData.removeRepairCost()
        return self

    def setCustomData(self, data):
        """
        设置自定义数据
        :type data: dict
        :param data: 自定义数据
        :return: ItemFactory
        """
        self.__userData.setCustomData(data)
        return self

    def addCustomData(self, key, value):
        """
        添加自定义数据
        :type key: str
        :type value: Any
        :param key: 键
        :param value: 值
        :return: ItemFactory
        """
        self.__userData.addCustomData({key: value})
        return self

    def removeCustomData(self, key):
        """
        删除自定义数据
        :type key: str
        :param key: 键
        :return: ItemFactory
        """
        self.__userData.removeCustomData(key)
        return self

    def removeAllCustomData(self):
        """
        删除所有自定义数据
        :return: ItemFactory
        """
        self.__userData.removeAllCustomData()
        return self

    # ---------------
    # ---- build ----
    # ---------------
    def build(self):
        """
        构建物品字典
        :rtype: dict
        :return: 物品字典
        """
        itemDict = {
            "newItemName": self.__itemName,
            "newAuxValue": self.__auxValue,
            "count": self.__count
        }
        if self.__durability is not None:
            itemDict["durability"] = self.__durability

        userData = self.__userData.build()
        if userData != {}:
            itemDict["userData"] = userData
        return itemDict

    # ----------------
    # ---- getter ----
    # ----------------
    def getCount(self):
        # type: () -> int
        return self.__count

    def getAuxValue(self):
        # type: () -> int
        return self.__auxValue

    def getItemName(self):
        # type: () -> str
        return self.__itemName

    def getDurability(self):
        # type: () -> int or None
        return self.__durability

    def getCustomTips(self):
        # type: () -> str or None
        return self.__userData.getCustomTips()

    def getLores(self):
        # type: () -> list
        lores = self.__userData.getLores()
        if lores is None:
            return []
        return lores

    def getName(self):
        # type: () -> str or None
        return self.__userData.getName()

    def getEnchantLevel(self, enchId):
        return self.__userData.getEnchantLevel(enchId)

    def getAllEnchantments(self):
        return self.__userData.getAllEnchantments()

    def getTrim(self):
        return self.__userData.getTrim()

    def getRepairCost(self):
        return self.__userData.getRepairCost()

    def getUserData(self):
        return self.__userData.build()

    def getCustomData(self):
        return self.__userData.getCustomData()
