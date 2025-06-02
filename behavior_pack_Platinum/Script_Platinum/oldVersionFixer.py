# coding=utf-8
import logging

import commonConfig
import re


def oldSlotTypeListToNew(slotTypeList):
    newBaubleList = []
    for baubleSlot in slotTypeList:
        newBaubleList.append(oldSlotTypeToNew(baubleSlot))
    return newBaubleList


def oldSlotTypeToNew(slotType):
    if slotType == commonConfig.BaubleEnum.BELT:
        return "belt"
    elif slotType == commonConfig.BaubleEnum.BACK:
        return "back"
    elif slotType == commonConfig.BaubleEnum.HELMET:
        return "helmet"
    elif slotType == commonConfig.BaubleEnum.NECKLACE:
        return "necklace"
    elif slotType == commonConfig.BaubleEnum.ARMOR:
        return "armor"
    elif slotType == commonConfig.BaubleEnum.HAND:
        return "hand"
    elif slotType == commonConfig.BaubleEnum.SHOES:
        return "shoes"
    elif slotType == commonConfig.BaubleEnum.OTHER:
        return "other"
    else:
        return slotType


def newSlotTypeToOld(slotType):
    if slotType == "helmet":
        return commonConfig.BaubleEnum.HELMET
    elif slotType == "necklace":
        return commonConfig.BaubleEnum.NECKLACE
    elif slotType == "back":
        return commonConfig.BaubleEnum.BACK
    elif slotType == "armor":
        return commonConfig.BaubleEnum.ARMOR
    elif slotType == "hand":
        return commonConfig.BaubleEnum.HAND
    elif slotType == "belt":
        return commonConfig.BaubleEnum.BELT
    elif slotType == "shoes":
        return commonConfig.BaubleEnum.SHOES
    elif slotType == "other":
        return commonConfig.BaubleEnum.OTHER
    else:
        return slotType


def oldSlotIdFixer(oldName):
    oldNameList = ["helmet", "necklace", "back", "armor", "hand_1", "hand_2", "belt", "shoes", "other_1", "other_2",
                   "other_3", "other_4"]
    if oldName in oldNameList:
        # 判断原字符串是否存在数字
        num = re.search(r"\d", oldName)
        if num:
            return "bauble_" + oldName.replace("_", "").replace(num.group(), "") + str(int(num.group()) - 1)
        else:
            return "bauble_" + oldName.replace("_", "")
    else:
        return oldName
