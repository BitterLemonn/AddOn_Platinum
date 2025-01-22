# coding=utf-8
from ..QuModLibs.Modules.Services.Server import BaseService, QRequests
from ..QuModLibs.Server import Events
from .. import developLogging as logging


# 服务端已注册槽位管理
@BaseService.Init
class BaubleSlotServerService(BaseService):

    def __init__(self):
        BaseService.__init__(self)
        self.__baubleSlotList = [
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

    # 获取槽位列表
    def getBaubleSlotList(self, defaultFilter=False):
        if defaultFilter:
            return [slotInfoDict for slotInfoDict in self.__baubleSlotList if slotInfoDict.get("isDefault")]
        return self.__baubleSlotList

    # 设置槽位列表
    def setBaubleSlotList(self, baubleSlotList):
        self.__baubleSlotList = baubleSlotList

    # 获取槽位标识符列表
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

    # 获取槽位类型列表
    def getBaubleSlotTypeList(self):
        baubleSlotTypeList = []
        for baubleSlotInfoDict in self.__baubleSlotList:
            baubleSlotType = baubleSlotInfoDict.get("baubleSlotType")
            if baubleSlotType not in baubleSlotTypeList:
                baubleSlotTypeList.append(baubleSlotType)
        return baubleSlotTypeList

    # 根据槽位标识符获取槽位类型
    def getBaubleSlotTypeBySlotIdentifier(self, baubleSlotIdentifier):
        for slotInfoDict in self.__baubleSlotList:
            if slotInfoDict.get("baubleSlotIdentifier") == baubleSlotIdentifier:
                return slotInfoDict.get("baubleSlotType")
        return None

    # 根据槽位类型获取槽位标识符列表
    def getBaubleSlotIdByTypeList(self, baubleSlotTypeList):
        baubleSlotIdList = []
        for slotInfoDict in self.__baubleSlotList:
            if slotInfoDict.get("baubleSlotType") in baubleSlotTypeList:
                baubleSlotIdList.append(slotInfoDict.get("baubleSlotIdentifier"))
        return baubleSlotIdList

    # 根据槽位标识符获取槽位索引
    def getSlotIndex(self, baubleSlotIdentifier):
        baubleType = None
        for slotInfoDict in self.__baubleSlotList:
            if slotInfoDict.get("baubleSlotIdentifier") == baubleSlotIdentifier:
                baubleType = slotInfoDict.get("baubleSlotType")
                break
        if not baubleType:
            logging.error("铂: 获取槽位索引失败, 未找到对应槽位")
            return None

        baubleSlotList = []
        for slotInfoDict in self.__baubleSlotList:
            if slotInfoDict.get("baubleSlotType") == baubleType:
                baubleSlotList.append(slotInfoDict.get("baubleSlotIdentifier"))
        return baubleSlotList.index(baubleSlotIdentifier) if len(baubleSlotList) > 1 else -1

    def __getBaubleSlotIdentifierList(self):
        baubleSlotIdentifierList = []
        for baubleSlotInfoDict in self.__baubleSlotList:
            baubleSlotIdentifier = baubleSlotInfoDict.get("baubleSlotIdentifier")
            if baubleSlotIdentifier not in baubleSlotIdentifierList:
                baubleSlotIdentifierList.append(baubleSlotIdentifier)
        return baubleSlotIdentifierList

    # 注册槽位
    def registerSlot(self, baubleSlotInfoDict):
        baubleSlotName = baubleSlotInfoDict.get("baubleSlotName")
        placeholderPath = baubleSlotInfoDict.get("placeholderPath")
        baubleSlotIdentifier = baubleSlotInfoDict.get("baubleSlotIdentifier")
        baubleSlotType = baubleSlotInfoDict.get("baubleSlotType")
        isDefault = baubleSlotInfoDict.get("isDefault", False)
        baubleSlotInfoDict["isDefault"] = isDefault
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
        if isDefault:
            self.syncToClient()
        return True

    # 添加槽位
    def addSlot(self, slotType, baubleIdentifier, isDefault=False):
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
            "baubleSlotType": slotType,
            "isDefault": isDefault
        }
        self.__baubleSlotList.append(registerSlotInfoDict)
        logging.debug("铂: 添加槽位{}成功".format(baubleIdentifier))
        if isDefault:
            self.syncToClient()
        return True

    # 删除槽位
    def deleteSlot(self, baubleSlotId):
        # 判断槽位是否存在
        if baubleSlotId not in self.getBaubleSlotIdentifierList():
            logging.error("铂: 删除槽位失败, 未找到对应槽位")
            return False
        # 判断是否为默认槽位
        for slotInfoDict in self.__baubleSlotList:
            if slotInfoDict.get("baubleSlotIdentifier") == baubleSlotId:
                if slotInfoDict.get("isDefault"):
                    logging.error("铂: 删除槽位失败, 无法删除默认槽位")
                    return False
                break
        # 删除槽位
        for slotInfoDict in self.__baubleSlotList:
            if slotInfoDict.get("baubleSlotIdentifier") == baubleSlotId:
                self.__baubleSlotList.remove(slotInfoDict)
                break
        return True

    # 获取槽位名称类型字典
    def getSlotNameTypeDict(self):
        slotNameTypeDict = {}
        for slotInfoDict in self.__baubleSlotList:
            slotNameTypeDict[slotInfoDict.get("baubleSlotName")] = slotInfoDict.get("baubleSlotType")
        return slotNameTypeDict

    # 获取槽位类型名称字典
    def getSlotTypeNameDict(self):
        slotTypeNameDict = {}
        for slotInfoDict in self.__baubleSlotList:
            slotTypeNameDict[slotInfoDict.get("baubleSlotType")] = slotInfoDict.get("baubleSlotName")
        return slotTypeNameDict

    # 同步默认槽位信息
    def syncToClient(self, targetPlayer=None):
        defaultSlot = self.getBaubleSlotList(True)
        self.syncRequest(targetPlayer or "*", "platinum/syncBaubleDefaultSlot", QRequests.Args(defaultSlot))
