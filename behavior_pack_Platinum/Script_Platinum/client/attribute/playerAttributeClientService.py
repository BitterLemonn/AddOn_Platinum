# coding=utf-8
from Script_Platinum.QuModLibs.Client import clientApi, compFactory, playerId
from Script_Platinum.QuModLibs.Modules.Services.Client import BaseService, QRequests
from Script_Platinum.data.attributeModifier import calculateModifiedValue


@BaseService.Init
class PlayerAttributeClientService(BaseService):
    """客户端属性同步服务。"""

    def __init__(self):
        BaseService.__init__(self)
        # 本机初始交互距离基准；各设备基准不同，服务端只下发修饰符，由客户端在自身基准上重放相同计算
        self._basePickRange = None  # type: float | None

    @BaseService.REG_API("client/attribute/syncPickRange")
    def syncPickRange(self, data):  # type: (dict | QRequests.RequestResults) -> bool
        if isinstance(data, QRequests.RequestResults):
            data = data.data
        if not isinstance(data, dict):
            return False
        modifiers = data.get("modifiers")
        if not isinstance(modifiers, list):
            return False
        playerComp = compFactory.CreatePlayer(playerId)
        if not playerComp:
            return False
        if self._basePickRange is None:
            current = playerComp.GetPickRange()
            if isinstance(current, bool) or not isinstance(current, (int, float)) or current <= 0.0:
                return False
            self._basePickRange = float(current)
        # ponytail: 客户端服务热重载时基准会被重复捕获（含已加成值），需重进世界重置
        newRange = calculateModifiedValue(
            self._basePickRange, modifiers, clientApi.GetMinecraftEnum().AttributeModifierOperation
        )
        return bool(newRange > 0.0 and playerComp.SetPickRange(newRange))
