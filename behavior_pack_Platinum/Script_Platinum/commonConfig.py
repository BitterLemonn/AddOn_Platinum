# coding=utf-8
"""
MIT License
Copyright (c) 2023 Bitterlemon

建议将以下参数(除BaubleDict以外)复制到自己的Script目录下
"""
import developLogging as logging

# 饰品广播事件 (请勿更改!!)
BAUBLE_EQUIPPED_EVENT = "BaubleEquipped"
BAUBLE_UNEQUIPPED_EVENT = "BaubleUnequipped"
BAUBLE_GET_INFO_EVENT = "BaubleGetInfo"
BAUBLE_GET_GLOBAL_INFO_EVENT = "BaubleGetGlobalInfo"
BAUBLE_GET_TARGET_INFO_EVENT = "BaubleGetTargetInfo"

PLATINUM_NAMESPACE = "platinum"
PLATINUM_BROADCAST_SERVER = "broadcasterServer"
PLATINUM_BROADCAST_CLIENT = "broadcasterClient"


# 槽位名称 (请勿更改!!)
# 旧版本槽位枚举 不建议使用
# 请查看readme使用新版本slotId
class BaubleEnum(object):
    HELMET = "§6栏位: §g头饰§r\n"
    NECKLACE = "§6栏位: §g项链§r\n"
    BACK = "§6栏位: §g背饰§r\n"
    ARMOR = "§6栏位: §g胸饰§r\n"
    HAND = "§6栏位: §g手环§r\n"
    BELT = "§6栏位: §g腰带§r\n"
    SHOES = "§6栏位: §g鞋子§r\n"
    OTHER = "§6栏位: §g护符§r\n"
