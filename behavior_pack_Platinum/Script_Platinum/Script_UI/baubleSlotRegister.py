# coding=utf-8
import logging


# 槽位注册字典
class BaubleSlotRegister(object):
    # 单例模式
    __instance = None
    __baubleSlotList = [
        {
            "baubleSlotName": "头盔",  # 槽位名称
            "placeholderPath": "textures/ui/bauble_helmet_slot",  # 占位图路径
            "baubleSlotIdentifier": "bauble_helmet",  # 槽位标识符(唯一)
            "baubleSlotType": "helmet",  # 槽位类型(可继承)
            "isDefault": True  # 是否默认拥有
        },
        {
            "baubleSlotName": "项链",
            "placeholderPath": "textures/ui/bauble_necklace_slot",
            "baubleSlotIdentifier": "bauble_necklace",
            "baubleSlotType": "necklace",
            "isDefault": True
        },
        {
            "baubleSlotName": "背饰",
            "placeholderPath": "textures/ui/bauble_back_slot",
            "baubleSlotIdentifier": "bauble_back",
            "baubleSlotType": "back",
            "isDefault": True
        },
        {
            "baubleSlotName": "胸饰",
            "placeholderPath": "textures/ui/bauble_armor_slot",
            "baubleSlotIdentifier": "bauble_armor",
            "baubleSlotType": "armor",
            "isDefault": True
        },
        {
            "baubleSlotName": "手环",
            "placeholderPath": "textures/ui/bauble_hand_slot",
            "baubleSlotIdentifier": "bauble_hand0",
            "baubleSlotType": "hand",
            "isDefault": True
        },
        {
            "baubleSlotName": "手环",
            "placeholderPath": "textures/ui/bauble_hand_slot",
            "baubleSlotIdentifier": "bauble_hand1",
            "baubleSlotType": "hand",
            "isDefault": True
        },
        {
            "baubleSlotName": "腰带",
            "placeholderPath": "textures/ui/bauble_belt_slot",
            "baubleSlotIdentifier": "bauble_belt",
            "baubleSlotType": "belt",
            "isDefault": True
        },
        {
            "baubleSlotName": "鞋子",
            "placeholderPath": "textures/ui/bauble_shoes_slot",
            "baubleSlotIdentifier": "bauble_shoes",
            "baubleSlotType": "shoes",
            "isDefault": True
        },
        {
            "baubleSlotName": "护符",
            "placeholderPath": "textures/ui/bauble_other_slot",
            "baubleSlotIdentifier": "bauble_other0",
            "baubleSlotType": "other",
            "isDefault": True
        },
        {
            "baubleSlotName": "护符",
            "placeholderPath": "textures/ui/bauble_other_slot",
            "baubleSlotIdentifier": "bauble_other1",
            "baubleSlotType": "other",
            "isDefault": True
        },
        {
            "baubleSlotName": "护符",
            "placeholderPath": "textures/ui/bauble_other_slot",
            "baubleSlotIdentifier": "bauble_other2",
            "baubleSlotType": "other",
            "isDefault": True
        },
        {
            "baubleSlotName": "护符",
            "placeholderPath": "textures/ui/bauble_other_slot",
            "baubleSlotIdentifier": "bauble_other3",
            "baubleSlotType": "other",
            "isDefault": True
        }
    ]

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(BaubleSlotRegister, cls).__new__(cls)
        return cls.__instance

    def getBaubleSlotList(self):
        return self.__baubleSlotList

    def getBaubleSlotIdentifierList(self, defaultFilter=False):
        baubleSlotIdentifierList = []
        for baubleSlotInfoDict in self.__baubleSlotList:
            baubleSlotIdentifier = baubleSlotInfoDict.get("baubleSlotIdentifier")
            if baubleSlotIdentifier not in baubleSlotIdentifierList:
                if defaultFilter and baubleSlotInfoDict.get("isDefault"):
                    baubleSlotIdentifierList.append(baubleSlotIdentifier)
                else:
                    baubleSlotIdentifierList.append(baubleSlotIdentifier)
        return baubleSlotIdentifierList

    def setBaubleSlotList(self, baubleSlotList):
        self.__baubleSlotList = baubleSlotList

    def getBaubleSlotTypeList(self):
        baubleSlotTypeList = []
        for baubleSlotInfoDict in self.__baubleSlotList:
            baubleSlotType = baubleSlotInfoDict.get("baubleSlotType")
            if baubleSlotType not in baubleSlotTypeList:
                baubleSlotTypeList.append(baubleSlotType)
        return baubleSlotTypeList

    def getBaubleSlotTypeBySlotIdentifier(self, baubleSlotIdentifier):
        for slotInfoDict in self.__baubleSlotList:
            if slotInfoDict.get("baubleSlotIdentifier") == baubleSlotIdentifier:
                return slotInfoDict.get("baubleSlotType")
        return None

    def getBaubleSlotIdByTypeList(self, baubleSlotTypeList):
        baubleSlotIdList = []
        for slotInfoDict in self.__baubleSlotList:
            if slotInfoDict.get("baubleSlotType") in baubleSlotTypeList:
                baubleSlotIdList.append(slotInfoDict.get("baubleSlotIdentifier"))
        return baubleSlotIdList

    def getSlotIndex(self, baubleSlotIdentifier):
        baubleType = None
        for slotInfoDict in self.__baubleSlotList:
            if slotInfoDict.get("baubleSlotIdentifier") == baubleSlotIdentifier:
                baubleType = slotInfoDict.get("baubleSlotType")
                break
        if not baubleType:
            logging.error("铂: 获取槽位索引失败, 未找到对应槽位")
            return None
        index = 0
        for slotInfoDict in self.__baubleSlotList:
            if slotInfoDict.get("baubleSlotType") == baubleType:
                if slotInfoDict.get("baubleSlotIdentifier") == baubleSlotIdentifier:
                    return index
                index += 1

    def __getBaubleSlotIdentifierList(self):
        baubleSlotIdentifierList = []
        for baubleSlotInfoDict in self.__baubleSlotList:
            baubleSlotIdentifier = baubleSlotInfoDict.get("baubleSlotIdentifier")
            if baubleSlotIdentifier not in baubleSlotIdentifierList:
                baubleSlotIdentifierList.append(baubleSlotIdentifier)
        return baubleSlotIdentifierList

    def registerSlot(self, baubleSlotInfoDict):
        baubleSlotName = baubleSlotInfoDict.get("baubleSlotName")
        placeholderPath = baubleSlotInfoDict.get("placeholderPath")
        baubleSlotIdentifier = baubleSlotInfoDict.get("baubleSlotIdentifier")
        baubleSlotType = baubleSlotInfoDict.get("baubleSlotType")
        if not baubleSlotName:
            logging.error("铂: 注册槽位失败, 槽位名称为空")
            return False
        elif not placeholderPath:
            logging.error("铂: 注册槽位失败, 占位图路径为空")
            return False
        elif not baubleSlotIdentifier:
            logging.error("铂: 注册槽位失败, 槽位标识符为空")
            return False
        elif baubleSlotIdentifier in self.__getBaubleSlotIdentifierList():
            logging.error("铂: 注册槽位失败, 槽位标识符重复")
            return False
        elif not baubleSlotType:
            logging.error("铂: 注册槽位失败, 槽位类型为空")
            return False
        elif baubleSlotType in self.getBaubleSlotTypeList():
            logging.error("铂: 注册槽位失败, 槽位类型重复, 请使用addSlot方法添加同类型槽位")
            return False
        self.__baubleSlotList.append(baubleSlotInfoDict)
        return True

    def addSlot(self, slotType, baubleIdentifier):
        if slotType not in self.getBaubleSlotTypeList():
            logging.error("铂: 添加槽位失败, 未注册的槽位类型, 请使用registerSlot方法注册槽位")
            return False

        originSlotInfoDict = None
        for slotInfoDict in self.__baubleSlotList:
            if slotInfoDict.get("baubleSlotType") == slotType:
                originSlotInfoDict = slotInfoDict
                break

        registerSlotInfoDict = {
            "baubleSlotName": originSlotInfoDict.get("baubleSlotName"),
            "placeholderPath": originSlotInfoDict.get("placeholderPath"),
            "baubleSlotIdentifier": baubleIdentifier,
            "baubleSlotType": slotType
        }
        self.__baubleSlotList.append(registerSlotInfoDict)
        logging.debug("铂: 添加槽位{}成功".format(baubleIdentifier))
        return True

    def deleteSlot(self, baubleType):
        if baubleType not in self.getBaubleSlotTypeList():
            logging.error("铂: 删除槽位失败, 未注册的槽位类型")
            return False

        deleteSlotInfoDictList = []
        for slotInfoDict in self.__baubleSlotList:
            if slotInfoDict.get("baubleSlotType") == baubleType:
                deleteSlotInfoDictList.append(slotInfoDict)

        if not deleteSlotInfoDictList:
            logging.error("铂: 删除槽位失败, 未找到对应槽位")
            return False
        elif len(deleteSlotInfoDictList) == 1:
            logging.error("铂: 删除槽位失败, 无法删除唯一槽位")
            return False

        removeSlotInfoDict = deleteSlotInfoDictList[-1]
        self.__baubleSlotList.remove(removeSlotInfoDict)
        logging.error("铂: 删除槽位{}成功".format(removeSlotInfoDict.get("baubleSlotIdentifier")))
        return True

    def getSlotNameTypeDict(self):
        slotNameTypeDict = {}
        for slotInfoDict in self.__baubleSlotList:
            slotNameTypeDict[slotInfoDict.get("baubleSlotName")] = slotInfoDict.get("baubleSlotType")
        return slotNameTypeDict

    def getSlotTypeNameDict(self):
        slotTypeNameDict = {}
        for slotInfoDict in self.__baubleSlotList:
            slotTypeNameDict[slotInfoDict.get("baubleSlotType")] = slotInfoDict.get("baubleSlotName")
        return slotTypeNameDict
