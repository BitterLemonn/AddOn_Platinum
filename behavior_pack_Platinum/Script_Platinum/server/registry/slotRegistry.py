# coding=UTF-8
from Script_Platinum.data.slotData import BaubleSlotData
from Script_Platinum.utils import developLogging as logging


class SlotRegistry(object):

    INSTANCE = None

    def __new__(cls):
        if cls.INSTANCE is None:
            cls.INSTANCE = super(SlotRegistry, cls).__new__(cls)
            cls.INSTANCE._slots = []
        return cls.INSTANCE

    def __init__(self):
        pass

    # 获取槽位列表
    def getBaubleSlotList(self, defaultFilter=False):
        if defaultFilter:
            return [slot for slot in self._slots if slot.isDefault]
        return list(self._slots)

    # 获取槽位标识符列表
    def getBaubleSlotIdList(self, defaultFilter=False):
        return [slot.identifier for slot in self.getBaubleSlotList(defaultFilter)]

    # 获取槽位类型列表
    def getBaubleSlotTypeList(self, defaultFilter=False):
        return [slot.slotType for slot in self.getBaubleSlotList(defaultFilter)]

    # 根据标识符获取类型
    def getSlotTypeById(self, slotId):
        for slot in self._slots:
            if slot.identifier == slotId:
                return slot.slotType
        return None

    # 根据类型获取标识符列表
    def getSlotIdByType(self, slotType):
        return [slot.identifier for slot in self._slots if slot.slotType == slotType]

    # 注册槽位
    def registerSlot(self, baubleInfoDict):  # type: (dict[str, str]) -> bool
        """
        注册槽位
        :param baubleInfoDict: 包含槽位信息的字典
        :return: 是否注册成功
        """
        baubleSlotName = baubleInfoDict.get("baubleSlotName", None)
        placeholderPath = baubleInfoDict.get("placeholderPath", None)
        baubleSlotId = baubleInfoDict.get("baubleSlotIdentifier", None)
        baubleSlotType = baubleInfoDict.get("baubleSlotType", None)
        isDefault = baubleInfoDict.get("isDefault", False)
        if baubleSlotId is None or baubleSlotType is None:
            logging.error("铂: 槽位({}:{})注册失败,请至少提供槽位标识符和槽位类型".format(baubleSlotName, baubleSlotId))
            return False
        existingSlot = None
        for slot in self._slots:
            if slot.identifier == baubleSlotId:
                logging.error("铂: 槽位({}:{})注册失败,槽位标识符已存在".format(baubleSlotName, baubleSlotId))
                return False
            if existingSlot is None and slot.slotType == baubleSlotType:
                existingSlot = slot

        # 如果是新槽位类型 需要传入占位图路径
        if existingSlot is None and placeholderPath is None:
            logging.error("铂: 槽位({}:{})注册失败,新槽位类型需要提供占位图路径".format(baubleSlotName, baubleSlotId))
            return False

        # 如果是继承槽位类型 使用已注册的占位图路径和槽位名称
        if existingSlot is not None:
            placeholderPath = existingSlot.placeholderPath
            baubleSlotName = baubleSlotName or existingSlot.name

        newSlot = BaubleSlotData(
            name=baubleSlotName,
            identifier=baubleSlotId,
            slotType=baubleSlotType,
            placeholderPath=placeholderPath,
            isDefault=isDefault,
        )
        self._slots.append(newSlot)
        logging.info("铂: 槽位({}:{})注册成功".format(baubleSlotName, baubleSlotId))
        return True
