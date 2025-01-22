# coding=utf-8
from .. import developLogging as logging
from ..DataManager.baubleSlotServerService import BaubleSlotServerService

from ..ItemFactory import ItemFactory
from ..QuModLibs.Modules.Services.Globals import BaseTimer, QRequests
from ..QuModLibs.Server import *
from ..QuModLibs.Modules.Services.Server import BaseService
from ..DataManager.baubleInfoManager import BaubleInfoManager
from ..Script_UI.baubleServer import BaubleServerService
from ..DataManager.baubleSlotManager import BaubleSlotManager
from .. import serverUtil


@AllowCall
def NeedSendInfo(playerId):
    comp = serverApi.GetEngineCompFactory().CreateMsg(playerId)
    comp.NotifyOneMessage(playerId,
                          "铂: 如遇到饰品无法安装请先尝试铂自带的旅行者腰带, 如可以正常安装反馈问题请到无法安装的饰品模组处反馈, 请勿在铂模组处反馈, 谢谢!",
                          "§6")


@BaseService.Init
class PlatinumServerService(BaseService):
    def __init__(self):
        BaseService.__init__(self)
        comp = serverApi.GetEngineCompFactory().CreateItem(levelId)
        comp.GetUserDataInEvent("InventoryItemChangedServerEvent")

    @BaseService.Listen("InventoryItemChangedServerEvent")
    def OnInventoryItemChangedServerEvent(self, data):
        playerId = data.get("playerId")
        itemDict = data.get("newItemDict")
        slot = data.get("slot")
        itemName = itemDict.get("newItemName")
        if itemName and itemName in BaubleInfoManager.getBaubleInfoDict().keys():
            baubleInfo = BaubleInfoManager.getBaubleInfoDict().get(itemName)
            try:
                customTips = ItemFactory(itemDict).getCustomTips()
                baubleTips = baubleInfo.get("customTips")
                if "§6栏位: §g" in (customTips or ""):
                    return
                else:
                    baubleSlotTypeList = baubleInfo.get("baubleSlot")
                    tips = "§6栏位: §g"
                    for slotType in baubleSlotTypeList:
                        isLast = baubleSlotTypeList.index(slotType) == len(baubleSlotTypeList) - 1
                        slotName = BaubleSlotManager().getSlotTypeNameDict().get(slotType)
                        tips += slotName + ("、" if not isLast else "") + ("§r\n" if isLast else "")
                    customTips = "%name%%category%%enchanting%\n" + tips + \
                                 (baubleTips if baubleTips else "") + "%attack_damage%"
                    itemDict = ItemFactory(itemDict).setCustomTips(customTips).build()
                    self.addTimer(BaseTimer(
                        callObject=serverUtil.GivePlayerItem,
                        kwargsDict={
                            "playerId": playerId,
                            "itemDict": itemDict,
                            "slot": slot
                        },
                        time=0.0
                    ))

            except Exception as e:
                logging.error("铂: 饰品 {} 描述格式错误, 请检查Script_Platinum/commonConfig.py {}".format(
                    itemDict.get("newItemName"), e)
                )

    @BaseService.Listen("CustomCommandTriggerServerEvent")
    def OnCustomCommandTriggerServerEvent(self, data):
        command = data.get("command")
        args = data.get("args")
        origin = data.get("origin")

        entityId = origin.get("entityId")
        dimensionId = origin.get("dimension")
        # 添加槽位
        if command == "platinum_add":
            if not entityId:
                data["return_failed"] = False
                data["return_msg_key"] = "铂: 仅允许玩家执行该指令"

            targetTuple = ()
            slotName = ""
            slotType = ""
            isGlobal = False
            for argDict in args:
                name = argDict.get("name")
                value = argDict.get("value")
                if name == "目标":
                    targetTuple = value
                elif name == "槽位id":
                    slotName = value
                elif name == "槽位类型":
                    slotType = value
                elif name == "是否为全局注册":
                    isGlobal = value
            if not targetTuple or not slotName or not slotType:
                data["return_failed"] = False
                data["return_msg_key"] = "§c铂: 参数异常 请检查指令是否输入正确§r"
                return
            # 检查输入槽位类型是否存在
            allSlotType = BaubleSlotManager().getBaubleSlotTypeList()
            if slotType not in allSlotType:
                data["return_failed"] = False
                data["return_msg_key"] = "§c铂: 槽位类型不存在 请检查槽位类型是否正确 输入/platinum_help查看帮助§r"
                return
            # 检查槽位id是否已存在
            allSlotId = BaubleSlotManager().getBaubleSlotIdentifierList()
            if slotName in allSlotId:
                data["return_failed"] = False
                data["return_msg_key"] = "§c铂: 目标槽位id已存在 请重新输入槽位id§r"
                return
            playerList = [player for player in targetTuple if Entity(player).IsPlayer]
            if not playerList:
                data["return_failed"] = False
                data["return_msg_key"] = "§c铂: 未找到目标玩家 请检查目标是否正确§r"
                return
            # 对比玩家列表是否为全部玩家
            allPlayerList = serverApi.GetPlayerList()
            if len(playerList) != len(allPlayerList) and isGlobal:
                data["return_failed"] = False
                data["return_msg_key"] = "§c铂: 全局注册时目标玩家必须为全部玩家§r"
                return

            if isGlobal:
                BaubleServerService.access().addGlobalBaubleSlot(slotId=slotName, slotType=slotType,
                                                                 isCommandModify=True)
                data["return_msg_key"] = "铂: 已执行全局注册槽位 {}".format(slotName)
            else:
                for playerId in playerList:
                    BaubleServerService.access().addTargetBaubleSlot(playerId, slotName, slotType, isCommandModify=True)
                data["return_msg_key"] = "铂: 已执行为特定玩家注册槽位 {}".format(slotName)
        elif command == "platinum_del":
            if not entityId:
                data["return_failed"] = False
                data["return_msg_key"] = "铂: 仅允许玩家执行该指令"
            targetTuple = ()
            slotName = ""
            for argDict in args:
                name = argDict.get("name")
                value = argDict.get("value")
                if name == "目标":
                    targetTuple = value
                elif name == "槽位id":
                    slotName = value

            if not targetTuple or not slotName:
                data["return_failed"] = False
                data["return_msg_key"] = "§c铂: 参数异常 请检查指令是否输入正确§r"
                return

            playerList = [player for player in targetTuple if Entity(player).IsPlayer]
            if not playerList:
                data["return_failed"] = False
                data["return_msg_key"] = "§c铂: 未找到目标玩家 请检查目标是否正确§r"
                return
            if slotName not in BaubleSlotManager().getBaubleSlotIdentifierList(True):
                for playerId in playerList:
                    self.syncRequest(playerId, "platinum/removeBaubleSlot",
                                     QRequests.Args(slotName, isCommandModify=True))
                data["return_msg_key"] = "铂: 已执行删除槽位 {}".format(slotName)
            else:
                data["return_failed"] = False
                data["return_msg_key"] = "§c铂: 槽位id {} 为默认槽位，无法删除".format(slotName)
        elif command == "platinum_help":
            control = ""
            for argDict in args:
                name = argDict.get("name")
                value = argDict.get("value")
                if name == "操作":
                    control = value
            if control == "help":
                data["return_msg_key"] = "铂: 查看帮助\n" \
                                         "§6/platinum_help slot_type - 查看已注册的槽位类型列表\n" \
                                         "§6/platinum_help slot_id - 查看已注册的槽位id列表"
            elif control == "slot_type":
                allSlotType = BaubleSlotServerService.access().getBaubleSlotTypeList()
                data["return_msg_key"] = "铂: 已注册的槽位类型列表:\n{}".format(", ".join(allSlotType))
            elif control == "slot_id":
                allSlotId = BaubleSlotServerService.access().getBaubleSlotIdentifierList()
                data["return_msg_key"] = "铂: 已注册的槽位id列表:\n{}".format(", ".join(allSlotId))
