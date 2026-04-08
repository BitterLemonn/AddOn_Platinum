# coding=UTF-8

defaultSlot = [
    {
        "baubleSlotName": "头盔",  # 槽位名称
        "placeholderPath": "textures/ui/bauble_helmet_slot",  # 占位图路径
        "baubleSlotIdentifier": "bauble_helmet",  # 槽位标识符(唯一)
        "baubleSlotType": "helmet",  # 槽位类型(可继承)
        "isDefault": True,  # 是否默认拥有
    },
    {
        "baubleSlotName": "项链",
        "placeholderPath": "textures/ui/bauble_necklace_slot",
        "baubleSlotIdentifier": "bauble_necklace",
        "baubleSlotType": "necklace",
        "isDefault": True,
    },
    {
        "baubleSlotName": "背饰",
        "placeholderPath": "textures/ui/bauble_back_slot",
        "baubleSlotIdentifier": "bauble_back",
        "baubleSlotType": "back",
        "isDefault": True,
    },
    {
        "baubleSlotName": "胸饰",
        "placeholderPath": "textures/ui/bauble_armor_slot",
        "baubleSlotIdentifier": "bauble_armor",
        "baubleSlotType": "armor",
        "isDefault": True,
    },
    {
        "baubleSlotName": "手环",
        "placeholderPath": "textures/ui/bauble_hand_slot",
        "baubleSlotIdentifier": "bauble_hand0",
        "baubleSlotType": "hand",
        "isDefault": True,
    },
    {
        "baubleSlotName": "手环",
        "placeholderPath": "textures/ui/bauble_hand_slot",
        "baubleSlotIdentifier": "bauble_hand1",
        "baubleSlotType": "hand",
        "isDefault": True,
    },
    {
        "baubleSlotName": "腰带",
        "placeholderPath": "textures/ui/bauble_belt_slot",
        "baubleSlotIdentifier": "bauble_belt",
        "baubleSlotType": "belt",
        "isDefault": True,
    },
    {
        "baubleSlotName": "鞋子",
        "placeholderPath": "textures/ui/bauble_shoes_slot",
        "baubleSlotIdentifier": "bauble_shoes",
        "baubleSlotType": "shoes",
        "isDefault": True,
    },
    {
        "baubleSlotName": "护符",
        "placeholderPath": "textures/ui/bauble_other_slot",
        "baubleSlotIdentifier": "bauble_other0",
        "baubleSlotType": "other",
        "isDefault": True,
    },
    {
        "baubleSlotName": "护符",
        "placeholderPath": "textures/ui/bauble_other_slot",
        "baubleSlotIdentifier": "bauble_other1",
        "baubleSlotType": "other",
        "isDefault": True,
    },
    {
        "baubleSlotName": "护符",
        "placeholderPath": "textures/ui/bauble_other_slot",
        "baubleSlotIdentifier": "bauble_other2",
        "baubleSlotType": "other",
        "isDefault": True,
    },
    {
        "baubleSlotName": "护符",
        "placeholderPath": "textures/ui/bauble_other_slot",
        "baubleSlotIdentifier": "bauble_other3",
        "baubleSlotType": "other",
        "isDefault": True,
    },
]


def innerRegisterDefaultSlot():
    from Script_Platinum.server.registry.slotRegistry import SlotRegistry

    registry = SlotRegistry()
    global defaultSlot
    for slotInfo in defaultSlot:
        registry.registerSlot(slotInfo)
