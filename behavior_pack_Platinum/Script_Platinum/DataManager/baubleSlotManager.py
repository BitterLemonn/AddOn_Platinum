# coding=utf-8
from .. import developLogging as logging


# 槽位字典(客户端各自拥有 记录客户端拥有的槽位信息 注意维护)
class BaubleSlotManager(object):
    # 单例模式
    _instance = None
    __baubleSlotList = []

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(BaubleSlotManager, cls).__new__(cls)
        return cls._instance

    # 获取槽位列表
    def getBaubleSlotList(self):
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
    def syncDefaultSlot(self, defaultSlotInfoList):
        addSlotInfoList = []
        for slotInfo in defaultSlotInfoList:
            if slotInfo.get("baubleSlotIdentifier") not in self.getBaubleSlotIdentifierList():
                if slotInfo.get("baubleSlotType") not in self.getBaubleSlotTypeList():
                    self.registerSlot(slotInfo)
                else:
                    self.addSlot(slotInfo.get("baubleSlotType"), slotInfo.get("baubleSlotIdentifier"), True)
                addSlotInfoList.append(slotInfo["baubleSlotIdentifier"])
        return addSlotInfoList
