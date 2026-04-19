# coding=utf-8
from Script_Platinum.QuModLibs.Server import *
from Script_Platinum.QuModLibs.Modules.Services.Server import BaseService
from Script_Platinum.server.items.itemService import SlotRegistry
from Script_Platinum.server.player.playerBaubleSlot import addPlayerSlot, deletePlayerSlotById, getPlayerSlotList
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
    data["return_failed"] = False
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
        targetTuple = parsed.get("目标", ())
        slotId = parsed.get("槽位id", "")
        slotType = parsed.get("槽位类型", "")
        isGlobal = parsed.get("是否为全局注册", False)

        # 参数完整性校验
        if not targetTuple or not slotId or not slotType:
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

        # 检测玩家是否已拥有该槽位
        for playerId in playerList:
            if any(slot.identifier == slotId for slot in getPlayerSlotList(playerId)):
                _setFailed(data, "§c铂: 玩家{}已拥有槽位id {} 无法重复添加§r".format(Entity(playerId).Name, slotId))
                return

        # 检测槽位id是否存在且全局属性是否冲突
        existingSlot = self.slotRegistry.getSlotDataById(slotId)
        if existingSlot is not None:
            if existingSlot.isDefault:
                _setFailed(data, "§c铂: 槽位id {} 为全局槽位 无法重复注册§r".format(slotId))
                return

            if isGlobal and not existingSlot.isDefault:
                _setFailed(data, "§c铂: 槽位id {} 已存在且非默认槽位 无法全局注册§r".format(slotId))
                return
        # 全局注册时目标必须为全部玩家
        if isGlobal and len(playerList) != len(serverApi.GetPlayerList()):
            _setFailed(data, "§c铂: 全局注册时目标玩家必须为全部玩家§r")
            return

        # 执行注册
        if not self.slotRegistry.isSlotIdExist(slotId):
            self.slotRegistry.registerSlot(BaubleSlotData(None, None, slotId, slotType, isGlobal, True))

        if isGlobal:
            data["return_msg_key"] = "铂: 已执行全局注册槽位 {}".format(slotId)
        else:
            slotData = self.slotRegistry.getSlotDataById(slotId)
            for playerId in playerList:
                addPlayerSlot(playerId, slotData)
            data["return_msg_key"] = "铂: 已执行为特定玩家注册槽位 {}".format(slotId)

    # ------------------------------------------------------------------
    #  platinum_del — 删除槽位
    # ------------------------------------------------------------------

    def _handleDel(self, data, args):
        parsed = _extractArgs(args)
        targetTuple = parsed.get("目标", ())
        slotId = parsed.get("槽位id", "")

        if not targetTuple or not slotId:
            _setFailed(data, "§c铂: 参数异常 请检查指令是否输入正确§r")
            return

        playerList = [pid for pid in targetTuple if Entity(pid).IsPlayer]
        if not playerList:
            _setFailed(data, "§c铂: 未找到目标玩家 请检查目标是否正确§r")
            return

        # 默认槽位不可删除
        defaultSlots = self.slotRegistry.getBaubleSlotList(defaultFilter=True)
        if slotId in defaultSlots:
            # 如果不为指令添加的默认槽位 则提示无法删除
            commandAddedSlotIds = [slot.identifier for slot in defaultSlots if slot.isCommandAdded]
            if slotId not in commandAddedSlotIds:
                _setFailed(data, "§c铂: 槽位id {} 为模组默认槽位，无法删除§r".format(slotId))
                return
            # 如果目标不为全体玩家 则提示无法删除
            if len(playerList) != len(serverApi.GetPlayerList()):
                _setFailed(data, "§c铂: 删除默认槽位时目标玩家必须为全部玩家§r")
                return

        for playerId in playerList:
            deletePlayerSlotById(playerId, slotId)

        # 检查是否所有玩家都不再持有该槽位，若都不持有则取消注册
        stillOwned = any(
            any(slot.identifier == slotId for slot in getPlayerSlotList(pid)) for pid in serverApi.GetPlayerList()
        )
        if not stillOwned:
            self.slotRegistry.deleteSlotById(slotId)

        data["return_msg_key"] = "铂: 已执行删除槽位 {}".format(slotId)

    # ------------------------------------------------------------------
    #  platinum_help — 帮助信息
    # ------------------------------------------------------------------

    def _handleHelp(self, data, args):
        parsed = _extractArgs(args)
        control = parsed.get("操作", "")

        if control == "help":
            data["return_msg_key"] = (
                "铂: 查看帮助\n"
                "§6/platinum_help slot_type - 查看已注册的槽位类型列表\n"
                "§6/platinum_help slot_id - 查看已注册的槽位id列表"
            )
        elif control == "slot_type":
            allSlotType = self.slotRegistry.getBaubleSlotTypeList()
            data["return_msg_key"] = "铂: 已注册的槽位类型列表:\n{}".format(", ".join(allSlotType))
        elif control == "slot_id":
            allSlotId = self.slotRegistry.getBaubleSlotIdList()
            data["return_msg_key"] = "铂: 已注册的槽位id列表:\n{}".format(", ".join(allSlotId))
