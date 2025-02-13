# coding=utf-8
import json
from .. import developLogging as logging
import re

from .baubleSlotManager import BaubleSlotManager
from ..QuModLibs.Client import *
from ..QuModLibs.Modules.Services.Client import BaseService
from .. import oldVersionFixer
from ..oldVersionFixer import oldSlotIdFixer


class DataAlias(object):
    PLATINUM_LOCAL_DATA = "platinum_local_data"
    BAUBLE_SLOT_INFO = "bauble_slot_info"
    BAUBLE_BTN_POSITION = "bauble_btn_position"
    BAUBLE_FORMAT_VERSION = "bauble_format_version"
    BAUBLE_COMMAND_MODIFY = "bauble_command_modify"


class BaubleDatabase(object):
    formatVersion = 1
    playerBaubleInfo = {}
    uiPosition = "left_top"
    baubleCommandModifyAdding = []


class BaubleDataController(object):
    @classmethod
    def getUiPosition(cls):
        return BaubleDatabase.uiPosition

    @classmethod
    def getBaubleCommandModifyAdding(cls):
        return BaubleDatabase.baubleCommandModifyAdding

    @classmethod
    def setUiPosition(cls, position):
        BaubleDatabase.uiPosition = position

    @classmethod
    def addBaubleSlot(cls, slotIdentifier, slotInfo=None):
        if slotIdentifier not in BaubleDatabase.playerBaubleInfo.keys():
            BaubleDatabase.playerBaubleInfo[slotIdentifier] = slotInfo

    @classmethod
    def removeBaubleSlot(cls, slotIdentifier):
        if slotIdentifier in BaubleDatabase.playerBaubleInfo.keys():
            return BaubleDatabase.playerBaubleInfo.pop(slotIdentifier)
        return None

    @classmethod
    def addBaubleInfo(cls, slotIdentifier, baubleInfo):
        BaubleDatabase.playerBaubleInfo[slotIdentifier] = baubleInfo

    @classmethod
    def popBaubleInfo(cls, slotIdentifier):
        baubleInfo = BaubleDatabase.playerBaubleInfo.get(slotIdentifier)
        if baubleInfo:
            BaubleDatabase.playerBaubleInfo[slotIdentifier] = None
        return baubleInfo

    @classmethod
    def getBaubleInfo(cls, slotIdentifier):
        return BaubleDatabase.playerBaubleInfo.get(slotIdentifier)

    @classmethod
    def getAllBaubleInfo(cls):
        return BaubleDatabase.playerBaubleInfo

    @classmethod
    def setAllBaubleInfo(cls, baubleInfoDict):
        keys = BaubleDatabase.playerBaubleInfo.keys()
        for key in keys:
            BaubleDatabase.playerBaubleInfo[key] = None
        for slotIdentifier, baubleInfo in baubleInfoDict.items():
            if slotIdentifier in keys:
                BaubleDatabase.playerBaubleInfo[slotIdentifier] = baubleInfo
            else:
                logging.error("铂: 未找到槽位标识符 {}".format(slotIdentifier))

    @classmethod
    def setBaubleInfo(cls, slotIdentifier, baubleInfo):
        if baubleInfo == {} or baubleInfo is None:
            baubleInfo = None
        if slotIdentifier in BaubleDatabase.playerBaubleInfo.keys():
            BaubleDatabase.playerBaubleInfo[slotIdentifier] = baubleInfo
            return True
        else:
            logging.error("铂: 未找到槽位标识符 {}".format(slotIdentifier))
            return False

    @classmethod
    def checkUnRegisterSlot(cls):
        removeDict = {}
        for slotIdentifier in BaubleDatabase.playerBaubleInfo.keys():
            if slotIdentifier not in BaubleSlotManager().getBaubleSlotIdentifierList():
                removeInfo = BaubleDatabase.playerBaubleInfo.pop(slotIdentifier)
                if removeInfo:
                    removeDict[slotIdentifier] = removeInfo
        return removeDict if removeDict else None

    @classmethod
    def clearBaubleInfo(cls):
        BaubleDatabase.playerBaubleInfo.clear()


@BaseService.Init
class BaubleDatabaseService(BaseService):

    def __init__(self):
        BaseService.__init__(self)
        self.__loadingData()

    def onServiceStop(self):
        self.__savingData()

    @staticmethod
    def addingCommandSlot(slotIdentifier, slotType, isDefault=False):
        logging.debug(
            "铂: 添加指令槽位: slotIdentifier: {}, slotType: {}, isDefault: {}".format(slotIdentifier, slotType,
                                                                                       isDefault))
        BaubleDatabase.baubleCommandModifyAdding.append({
            "slotIdentifier": slotIdentifier,
            "slotType": slotType,
            "isDefault": isDefault
        })

    @staticmethod
    def removeCommandSlot(slotIdentifier):
        for index, slotInfo in enumerate(BaubleDatabase.baubleCommandModifyAdding):
            if slotInfo.get("slotIdentifier") == slotIdentifier:
                BaubleDatabase.baubleCommandModifyAdding.pop(index)
                break

    def manualSaving(self):
        self.__savingData()

    def __loadingData(self):
        playerComp = clientApi.GetEngineCompFactory().CreatePlayer(playerId)
        uid = playerComp.getUid()
        comp = clientApi.GetEngineCompFactory().CreateConfigClient(levelId)
        data = comp.GetConfigData(DataAlias.PLATINUM_LOCAL_DATA + "_{}".format(uid))
        if data:
            formatVersion = data.get(DataAlias.BAUBLE_FORMAT_VERSION, 0)
            BaubleDatabase.uiPosition = data.get(DataAlias.BAUBLE_BTN_POSITION, "left_top")
            BaubleDatabase.playerBaubleInfo = self.migrateData(formatVersion,
                                                               data.get(DataAlias.BAUBLE_SLOT_INFO, {}))
            BaubleDatabase.baubleCommandModifyAdding = data.get(DataAlias.BAUBLE_COMMAND_MODIFY, [])
            logging.info(
                "铂: 数据加载成功: baubleCommandModifyAdding: {}".format(BaubleDatabase.baubleCommandModifyAdding))

    def __savingData(self):
        playerComp = clientApi.GetEngineCompFactory().CreatePlayer(playerId)
        uid = playerComp.getUid()
        comp = clientApi.GetEngineCompFactory().CreateConfigClient(levelId)
        dataDict = {
            DataAlias.BAUBLE_SLOT_INFO: BaubleDatabase.playerBaubleInfo,
            DataAlias.BAUBLE_FORMAT_VERSION: BaubleDatabase.formatVersion,
            DataAlias.BAUBLE_BTN_POSITION: BaubleDatabase.uiPosition,
            DataAlias.BAUBLE_COMMAND_MODIFY: BaubleDatabase.baubleCommandModifyAdding
        }
        logging.error(
            "铂: 数据保存成功: baubleCommandModifyAdding: {}".format(BaubleDatabase.baubleCommandModifyAdding))
        comp.SetConfigData(DataAlias.PLATINUM_LOCAL_DATA + "_{}".format(uid), dataDict)

    def migrateData(self, formatVersion, data):
        if formatVersion != BaubleDatabase.formatVersion:
            # 数据版本从0升级到1
            if formatVersion == 0:
                formatVersion = 1
                for baubleName, value in data.items():
                    newId = oldVersionFixer.oldSlotIdFixer(baubleName)
                    data[newId] = value
                    data.pop(baubleName)
            self.migrateData(formatVersion, data)
        return data
