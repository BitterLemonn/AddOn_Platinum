import commonConfig


def oldSlotTypeChanger(baubleSlotList):
    newBaubleList = []
    for baubleSlot in baubleSlotList:
        if baubleSlot == commonConfig.BaubleEnum.BELT:
            newBaubleList.append("belt")
        elif baubleSlot == commonConfig.BaubleEnum.HELMET:
            newBaubleList.append("helmet")
        elif baubleSlot == commonConfig.BaubleEnum.HAND:
            newBaubleList.append("hand")
        elif baubleSlot == commonConfig.BaubleEnum.NECKLACE:
            newBaubleList.append("necklace")
        elif baubleSlot == commonConfig.BaubleEnum.ARMOR:
            newBaubleList.append("armor")
        elif baubleSlot == commonConfig.BaubleEnum.BACK:
            newBaubleList.append("back")
        elif baubleSlot == commonConfig.BaubleEnum.SHOES:
            newBaubleList.append("shoes")
        elif baubleSlot == commonConfig.BaubleEnum.OTHER:
            newBaubleList.append("other")
        else:
            newBaubleList.append(baubleSlot)
    return newBaubleList


def oldVersionFixer(baubleSlot):
    if baubleSlot == "helmet":
        return commonConfig.BaubleEnum.HELMET
    elif baubleSlot == "necklace":
        return commonConfig.BaubleEnum.NECKLACE
    elif baubleSlot == "back":
        return commonConfig.BaubleEnum.BACK
    elif baubleSlot == "armor":
        return commonConfig.BaubleEnum.ARMOR
    elif baubleSlot == "hand":
        return commonConfig.BaubleEnum.HAND
    elif baubleSlot == "belt":
        return commonConfig.BaubleEnum.BELT
    elif baubleSlot == "shoes":
        return commonConfig.BaubleEnum.SHOES
    elif baubleSlot == "other":
        return commonConfig.BaubleEnum.OTHER
    else:
        return baubleSlot
