# coding=utf-8
import logging


class BaubleInfoManager(object):
    __baubleInfoDict = {
        # "lemon_platinum:traveler_belt": {
        #     "baubleSlot": ["belt"],
        #     "customTips": "xxxxx"
        # }
    }

    @classmethod
    def registerBaubleInfo(cls, baubleName, baubleSlot, customTips=None):
        if not isinstance(baubleSlot, list):
            baubleSlot = [baubleSlot]
        if baubleName in cls.__baubleInfoDict.keys():
            logging.error("铂: 饰品 {} 已存在,请勿重复注册".format(baubleName))
            return

        infoDict = {"baubleSlot": baubleSlot}
        if customTips and len(customTips) > 0:
            infoDict["customTips"] = customTips
        cls.__baubleInfoDict[baubleName] = infoDict
        logging.info("铂: 饰品 {} 注册成功".format(baubleName))

    @classmethod
    def getBaubleInfoDict(cls):
        return cls.__baubleInfoDict
