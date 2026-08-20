# coding=utf-8
from Script_Platinum.QuModLibs.Server import *
from Script_Platinum.QuModLibs.Modules.Services.Server import BaseService
from Script_Platinum.server.items.itemService import SlotRegistry
from Script_Platinum.server.player.playerBaubleSlot import addPlayerSlot, deletePlayerSlotById, getPlayerSlotList
from Script_Platinum.server.command.slotCommandUtils import (
    MAX_SLOT_COUNT,
    createCommandSlotIds,
    getDeletableCommandSlots,
    isValidSlotCount,
)
from Script_Platinum.data.slotData import BaubleSlotData


def _extractArgs(args):
    """将指令参数列表转换为 {name: value} 字典"""
    result = {}
    for argDict in args:
        name = argDict.get("name")
        value = argDict.get("value")
        if name is not None:
            result[name] = value
    return result


def _setFailed(data, msg):
    """设置指令执行失败状态和消息"""
    data["return_failed"] = True
    data["return_msg_key"] = msg


@BaseService.Init
class CommandService(BaseService):

    def __init__(self):
        BaseService.__init__(self)
        self.slotRegistry = SlotRegistry()  # type: SlotRegistry

    @BaseService.Listen("CustomCommandTriggerServerEvent")
    def onCustomCommandTriggerServerEvent(self, data):
        command = data.get("command")
        args = data.get("args")
        origin = data.get("origin")

        # 仅允许玩家执行
        if not origin.get("entityId"):
            _setFailed(data, "§c铂: 仅允许玩家执行该指令§r")
            return

        handler = {
            "platinum_add": self._handleAdd,
            "platinum_del": self._handleDel,
            "platinum_help": self._handleHelp,
        }.get(command)

        if handler is not None:
            handler(data, args)

    # 改变饰品栏入口位置
    @BaseService.Listen("ServerChatEvent")
    def onServerChatEvent(self, data):
        playerId = data["playerId"]
        msg = data["message"]
        if msg.startswith("#platinum_"):
            comp = serverApi.GetEngineCompFactory().CreateMsg(playerId)
            data["cancel"] = True
            msg = msg.replace("#platinum_", "")
            if msg in ["left_top", "right_top", "left_bottom", "right_bottom"]:
                Call(playerId, "ChangeUiPosition", msg)

                position = (
                    "左上角"
                    if msg == "left_top"
                    else "右上角" if msg == "right_top" else "左下角" if msg == "left_bottom" else "右下角"
                )

                comp.NotifyOneMessage(playerId, "铂: 饰品栏按钮已切换至{}".format(position))
            elif msg in ["get_gs"]:
                self.getGlobalBaubleSlotInfo()
            elif msg in ["get_ts"]:
                self.getTargetBaubleSlotInfo(playerId)
            else:
                comp.NotifyOneMessage(playerId, "§c铂: 未知指令§r")

    # ------------------------------------------------------------------
    #  platinum_add — 添加槽位
    # ------------------------------------------------------------------

    def _handleAdd(self, data, args):
        parsed = _extractArgs(args)
        print(parsed)
        targetTuple = parsed.get("目标", ())
        slotType = parsed.get("槽位类型", "")
        count = parsed.get("数量", 0)
        isGlobal = parsed.get("是否为全局注册", False)

        # 参数完整性校验
        if not targetTuple or not slotType or not isValidSlotCount(count):
            _setFailed(data, "§c铂: 参数异常 数量必须为1-{}的整数§r".format(MAX_SLOT_COUNT))
            return

        if not isinstance(isGlobal, bool):
            _setFailed(data, "§c铂: 参数异常 请检查指令是否输入正确§r")
            return

        # 槽位类型是否存在
        if slotType not in self.slotRegistry.getBaubleSlotTypeList():
            _setFailed(data, "§c铂: 槽位类型不存在 请检查槽位类型是否正确 输入/platinum_help查看帮助§r")
            return

        # 过滤出真实玩家
        playerList = [pid for pid in targetTuple if Entity(pid).IsPlayer]
        if not playerList:
            _setFailed(data, "§c铂: 未找到目标玩家 请检查目标是否正确§r")
            return

        # 全局注册时目标必须为全部玩家
        if isGlobal and len(playerList) != len(serverApi.GetPlayerList()):
            _setFailed(data, "§c铂: 全局注册时目标玩家必须为全部玩家§r")
            return

        currentSlotCount = len(self.slotRegistry.getBaubleSlotList())
        if currentSlotCount + count > MAX_SLOT_COUNT:
            _setFailed(
                data,
                "§c铂: 创建失败 当前已有{}个槽位 创建{}个后将超过{}个槽位上限§r".format(
                    currentSlotCount, count, MAX_SLOT_COUNT
                ),
            )
            return

        slotIds = createCommandSlotIds(self.slotRegistry.getBaubleSlotIdList(), count)
        createdSlots = []
        for slotId in slotIds:
            if not self.slotRegistry.registerSlot(BaubleSlotData(None, None, slotId, slotType, isGlobal, True)):
                _setFailed(data, "§c铂: 批量创建中断 已创建{}个槽位§r".format(len(createdSlots)))
                return
            createdSlots.append(self.slotRegistry.getSlotDataById(slotId))

        if isGlobal:
            data["return_msg_key"] = "铂: 已全局创建{}个{}槽位".format(count, slotType)
        else:
            for playerId in playerList:
                for slotData in createdSlots:
                    addPlayerSlot(playerId, slotData)
            data["return_msg_key"] = "铂: 已为目标玩家创建{}个{}槽位".format(count, slotType)

    # ------------------------------------------------------------------
    #  platinum_del — 删除槽位
    # ------------------------------------------------------------------

    def _handleDel(self, data, args):
        parsed = _extractArgs(args)
        targetTuple = parsed.get("目标", ())
        slotType = parsed.get("槽位类型", "")
        count = parsed.get("数量", 0)

        if not targetTuple or not slotType or not isValidSlotCount(count):
            _setFailed(data, "§c铂: 参数异常 数量必须为1-{}的整数§r".format(MAX_SLOT_COUNT))
            return

        playerList = [pid for pid in targetTuple if Entity(pid).IsPlayer]
        if not playerList:
            _setFailed(data, "§c铂: 未找到目标玩家 请检查目标是否正确§r")
            return

        if slotType not in self.slotRegistry.getBaubleSlotTypeList():
            _setFailed(data, "§c铂: 槽位类型不存在 请检查槽位类型是否正确 输入/platinum_help查看帮助§r")
            return

        allPlayerIds = serverApi.GetPlayerList()
        targetsAllPlayers = len(playerList) == len(allPlayerIds)
        ownedSlotIds = [slot.identifier for playerId in playerList for slot in getPlayerSlotList(playerId)]
        slotsToDelete = getDeletableCommandSlots(
            self.slotRegistry.getBaubleSlotList(), slotType, ownedSlotIds, count, targetsAllPlayers
        )
        if len(slotsToDelete) < count:
            _setFailed(data, "§c铂: 目标玩家仅有{}个可删除的{}指令槽位§r".format(len(slotsToDelete), slotType))
            return

        for slotData in slotsToDelete:
            slotId = slotData.identifier
            for playerId in playerList:
                if any(slot.identifier == slotId for slot in getPlayerSlotList(playerId)):
                    deletePlayerSlotById(playerId, slotId)

            # 检查是否所有在线玩家都不再持有该槽位，若都不持有则取消注册
            stillOwned = any(any(slot.identifier == slotId for slot in getPlayerSlotList(pid)) for pid in allPlayerIds)
            if not stillOwned:
                self.slotRegistry.deleteSlotById(slotId)

        data["return_msg_key"] = "铂: 已删除{}个{}槽位".format(count, slotType)

    # ------------------------------------------------------------------
    #  platinum_help — 帮助信息
    # ------------------------------------------------------------------

    def _handleHelp(self, data, args):
        parsed = _extractArgs(args)
        control = parsed.get("操作", "")

        if control == "help":
            data["return_msg_key"] = (
                "铂: 查看帮助\n"
                "§6/platinum_add <槽位类型> [数量1-107] [目标] [是否全局] - 创建槽位 总量上限107\n"
                "§6/platinum_del <槽位类型> [数量1-107] [目标] - 删除最近创建的指令槽位\n"
                "§6/platinum_help slot_type - 查看已注册的槽位类型列表\n"
                "§6/platinum_help slot_id - 查看已注册的槽位id列表"
            )
        elif control == "slot_type":
            allSlotType = self.slotRegistry.getBaubleSlotTypeList()
            data["return_msg_key"] = "铂: 已注册的槽位类型列表:\n{}".format(", ".join(allSlotType))
        elif control == "slot_id":
            allSlotId = self.slotRegistry.getBaubleSlotIdList()
            data["return_msg_key"] = "铂: 已注册的槽位id列表:\n{}".format(", ".join(allSlotId))
