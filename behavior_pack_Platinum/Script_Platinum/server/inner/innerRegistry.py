# coding=UTF-8
from mod.server import extraServerApi as serverApi

from Script_Platinum import commonConfig
from Script_Platinum.utils.serverUtils import compFactory

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


class InnerServerRegistry(serverApi.GetServerSystemCls()):

    def __init__(self, namespace, name):
        super(InnerServerRegistry, self).__init__(namespace, name)
        self.listenEvent()

    def listenEvent(self):
        self.ListenForEvent(
            serverApi.GetEngineNamespace(),
            serverApi.GetEngineSystemName(),
            "LoadServerAddonScriptsAfter",
            self,
            self.onLoadServerAddonScriptsAfter,
        )

    def onLoadServerAddonScriptsAfter(self, data):

        def actualLogic():
            # 获取铂注册系统
            system = serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER)
            # 注册默认槽位(注意需要先注册槽位再注册饰品)
            for slotData in defaultSlot:
                system.AddGlobalBaubleSlot(
                    slotId=slotData["baubleSlotIdentifier"],
                    slotType=slotData["baubleSlotType"],
                    slotName=slotData["baubleSlotName"],
                    slotPlaceHolderPath=slotData["placeholderPath"],
                    isDefault=slotData["isDefault"],
                )
            # 注册饰品
            system.BaubleRegister({"baubleName": "lemon_platinum:traveler_belt", "baubleSlot": "belt"})

        # 如果需要在LoadServerAddonScriptsAfter事件中注册槽位和饰品 需要延迟一帧执行以确保注册系统已经完成初始化
        compFactory.CreateGame(serverApi.GetLevelId()).AddTimer(0, actualLogic)
