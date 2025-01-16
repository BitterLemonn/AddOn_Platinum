# coding=utf-8
import json
import logging

from .baubleSlotRegister import BaubleSlotRegister
from ..QuModLibs.Client import *
from ..QuModLibs.Modules.Services.Client import BaseService


class BaubleDatabase(object):
    playerBaubleInfo = {}


class BaubleDataController(object):

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
        if slotIdentifier in BaubleDatabase.playerBaubleInfo.keys():
            BaubleDatabase.playerBaubleInfo[slotIdentifier] = baubleInfo
        else:
            logging.error("铂: 未找到槽位标识符 {}".format(slotIdentifier))

    @classmethod
    def checkUnRegisterSlot(cls):
        removeDict = {}
        for slotIdentifier in BaubleDatabase.playerBaubleInfo.keys():
            if slotIdentifier not in BaubleSlotRegister().getBaubleSlotIdentifierList():
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

    def manualSaving(self):
        self.__savingData()

    def __loadingData(self):
        comp = clientApi.GetEngineCompFactory().CreateConfigClient(levelId)
        data = comp.GetConfigData("baubleDatabase")
        BaubleDatabase.playerBaubleInfo = data

    def __savingData(self):
        comp = clientApi.GetEngineCompFactory().CreateConfigClient(levelId)
        comp.SetConfigData("baubleDatabase", BaubleDatabase.playerBaubleInfo)
