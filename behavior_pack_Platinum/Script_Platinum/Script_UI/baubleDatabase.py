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
            logging.error("add slot: {}".format(slotIdentifier))
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
        if slotIdentifier in BaubleDatabase.playerBaubleInfo.keys():
            return BaubleDatabase.playerBaubleInfo.pop(slotIdentifier)
        return None

    @classmethod
    def getBaubleInfo(cls, slotIdentifier):
        return BaubleDatabase.playerBaubleInfo.get(slotIdentifier)

    @classmethod
    def getAllBaubleInfo(cls):
        return BaubleDatabase.playerBaubleInfo

    @classmethod
    def checkUnRegisterSlot(cls):
        removeList = []
        for slotIdentifier in BaubleDatabase.playerBaubleInfo.keys():
            if slotIdentifier not in BaubleSlotRegister().getBaubleSlotIdentifierList():
                removeInfo = BaubleDatabase.playerBaubleInfo.pop(slotIdentifier)
                if removeInfo:
                    removeList.append(removeInfo)
        return removeList if removeList else None


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
