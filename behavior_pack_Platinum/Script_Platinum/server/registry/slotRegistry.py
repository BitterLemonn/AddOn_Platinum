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

    # 根据标识符获取数据
    def getSlotDataById(self, slotId):  # type: (str) -> BaubleSlotData
        for slot in self._slots:
            if slot.identifier == slotId:
                return slot
        return None

    # 根据类型获取名称
    def getSlotTypeNameByType(self, slotType):
        for slot in self._slots:
            if slot.slotType == slotType:
                return slot.name
        return None

    # 根据标识符获取同类型中的index
    def getSlotIndexById(self, slotId):
        slotType = self.getSlotTypeById(slotId)
        if slotType is None:
            return -1
        sameTypeSlots = [slot for slot in self._slots if slot.slotType == slotType]
        for index, slot in enumerate(sameTypeSlots):
            if slot.identifier == slotId:
                return index + 1
        return -1

    # 根据类型获取标识符列表
    def getSlotIdByType(self, slotType):
        return [slot.identifier for slot in self._slots if slot.slotType == slotType]

    # 注册槽位
    def registerSlot(self, baubleSlotData):  # type: (BaubleSlotData) -> bool
        """
        注册槽位
        :param baubleSlotData: 槽位数据对象
        :return: 是否注册成功
        """
        baubleSlotName = baubleSlotData.name
        placeholderPath = baubleSlotData.placeholderPath
        baubleSlotId = baubleSlotData.identifier
        baubleSlotType = baubleSlotData.slotType
        isDefault = baubleSlotData.isDefault
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
                break

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
        logging.sucess("铂: 槽位({}:{})注册成功".format(baubleSlotName, baubleSlotId))
        return True

    def isSlotIdExist(self, slotId):
        """检查槽位标识符是否已存在"""
        return any(slot.identifier == slotId for slot in self._slots)
