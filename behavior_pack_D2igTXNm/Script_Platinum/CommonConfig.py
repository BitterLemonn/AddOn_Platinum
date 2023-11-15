# coding=utf-8

# 装备饰品广播事件 (请勿更改)
BAUBLE_EQUIPPED_EVENT = "BaubleEquipped"
BAUBLE_UNEQUIPPED_EVENT = "BaubleUnequipped"
PLATINUM_NAMESPACE = "platinum"
PLATINUM_BROADCAST_SERVER = "broadcasterServer"
PLATINUM_BROADCAST_CLIENT = "broadcasterClient"


# 槽位名称 (请勿更改)
class BaubleEnum(object):
    HELMET = "§6栏位: §g头饰§r\n"
    NECKLACE = "§6栏位: §g项链§r\n"
    BACK = "§6栏位: §g背饰§r\n"
    ARMOR = "§6栏位: §g胸饰§r\n"
    HAND = "§6栏位: §g手环§r\n"
    BELT = "§6栏位: §g腰带§r\n"
    SHOES = "§6栏位: §g鞋子§r\n"
    OTHER = "§6栏位: §g护符§r\n"


# 饰品字典(添加饰品时请在此处添加)
'''
支持的格式如下:
物品标识符 : [栏位, 其他物品描述(customTips)]
物品标识符 : [栏位]
物品标识符 : 栏位
'''
BaubleDict = {
    "lemon_platinum:traveler_belt": [BaubleEnum.BELT, "§9装备时:\n+0.5 跨越高度§r"],
}
