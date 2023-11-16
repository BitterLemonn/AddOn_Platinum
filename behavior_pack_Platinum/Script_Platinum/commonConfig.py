# coding=utf-8

"""
在Script_Platinum外使用时
可以将以下参数(除BaubleDict以外)复制到自己的Script目录下
配置饰品仍需修改此处的BaubleDict
"""

# 装备饰品广播事件 (请勿更改)
BAUBLE_EQUIPPED_EVENT = "BaubleEquipped"
BAUBLE_UNEQUIPPED_EVENT = "BaubleUnequipped"
# 当不使用内容库内容时,也可通过服务端发送BaubleRegister事件注册饰品
# 需要服务端namespace为platinum, systemName为broadcasterServer
BAUBLE_REGISTER_EVENT = "BaubleRegister"
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


"""
在Script_Platinum外使用时
可以将以上参数(除BaubleDict以外)复制到自己的Script目录下
配置饰品仍需修改此处的BaubleDict
"""

# 饰品字典(添加饰品时请在此处添加)
"""
支持的格式如下:
物品标识符 : [栏位, 其他物品描述(customTips)]
物品标识符 : [栏位]
物品标识符 : 栏位
"""
BaubleDict = {
    "lemon_platinum:traveler_belt": [BaubleEnum.BELT, "§9装备时:\n+0.5 跨越高度§r"],
}
