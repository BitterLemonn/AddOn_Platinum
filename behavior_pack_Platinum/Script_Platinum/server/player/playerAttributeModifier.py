# coding=utf-8
import math

from Script_Platinum.QuModLibs.Modules.Services.Server import BaseService
from Script_Platinum.QuModLibs.Server import compFactory, serverApi
from Script_Platinum.data.attributeModifier import calculateModifiedValue


minecraftEnum = serverApi.GetMinecraftEnum()
AttributeModifierOperation = minecraftEnum.AttributeModifierOperation
AttributeOperands = minecraftEnum.AttributeOperands
AttrType = minecraftEnum.AttrType


class PlayerAttributeType(object):
    """引擎属性修饰符未覆盖或不支持修饰符的玩家属性。"""

    FLYING_ABILITY = "flying_ability"
    STEP_HEIGHT = "step_height"
    ARMOR = AttrType.ARMOR

    VALUES = (FLYING_ABILITY, STEP_HEIGHT, ARMOR)


@BaseService.Init
class PlayerAttributeModifierService(BaseService):
    """统一管理引擎 AddModifier 未覆盖的玩家属性。"""

    def __init__(self):
        BaseService.__init__(self)
        self._modifierMap = {}  # type: dict[tuple[str, str | int], dict[str, dict]]
        self._baseValueMap = {}  # type: dict[tuple[str, str | int], float]

    def addModifier(self, playerId, attributeType, modifierId, amount, operation, operand):
        if not self._validateModifier(playerId, attributeType, modifierId, amount, operation, operand):
            return False
        key = (playerId, attributeType)
        modifiers = self._modifierMap.setdefault(key, {})
        if modifierId in modifiers:
            return False
        if key not in self._baseValueMap:
            baseValue = self._getBaseValue(playerId, attributeType)
            if baseValue is None:
                self._removeEmptyKey(key)
                return False
            self._baseValueMap[key] = baseValue
        modifiers[modifierId] = self._createModifier(modifierId, amount, operation, operand)
        if self._apply(key):
            return True
        del modifiers[modifierId]
        self._removeEmptyKey(key)
        return False

    def updateModifier(self, playerId, attributeType, modifierId, amount, operation, operand):
        if not self._validateModifier(playerId, attributeType, modifierId, amount, operation, operand):
            return False
        key = (playerId, attributeType)
        modifiers = self._modifierMap.get(key)
        if not modifiers or modifierId not in modifiers:
            return False
        oldModifier = modifiers[modifierId]
        modifiers[modifierId] = self._createModifier(modifierId, amount, operation, operand)
        if self._apply(key):
            return True
        modifiers[modifierId] = oldModifier
        return False

    def removeModifier(self, playerId, attributeType, modifierId):
        if not self._validateKey(playerId, attributeType, modifierId):
            return False
        key = (playerId, attributeType)
        modifiers = self._modifierMap.get(key)
        if not modifiers or modifierId not in modifiers:
            return False
        oldModifier = modifiers.pop(modifierId)
        if self._apply(key):
            self._removeEmptyKey(key)
            return True
        modifiers[modifierId] = oldModifier
        return False

    def hasModifier(self, playerId, attributeType, modifierId):
        if not self._validateKey(playerId, attributeType, modifierId):
            return False
        return modifierId in self._modifierMap.get((playerId, attributeType), {})

    def getAllModifiers(self, playerId, attributeType):
        if not self._validateAttribute(playerId, attributeType):
            return []
        modifiers = self._modifierMap.get((playerId, attributeType), {})
        return [dict(modifiers[modifierId]) for modifierId in sorted(modifiers)]

    @BaseService.Listen("PlayerIntendLeaveServerEvent")
    def onPlayerIntendLeave(self, data):
        self.clearPlayer(data["playerId"], True)

    @BaseService.Listen("DelServerPlayerEvent")
    def onDelServerPlayer(self, data):
        self.clearPlayer(data["id"], False)

    def onServiceStop(self):
        BaseService.onServiceStop(self)
        for key in self._modifierMap.keys():
            self._restore(key)
        self._modifierMap.clear()
        self._baseValueMap.clear()

    def clearPlayer(self, playerId, restore):
        keys = [key for key in self._modifierMap if key[0] == playerId]
        for key in keys:
            if restore:
                self._restore(key)
            self._modifierMap.pop(key, None)
            self._baseValueMap.pop(key, None)

    @staticmethod
    def _createModifier(modifierId, amount, operation, operand):
        return {
            "modifierId": modifierId,
            "amount": float(amount),
            "operation": operation,
            "operand": operand,
        }

    @staticmethod
    def _validateAttribute(playerId, attributeType):
        return (
            isinstance(playerId, str)
            and bool(playerId)
            and attributeType in PlayerAttributeType.VALUES
        )

    def _validateKey(self, playerId, attributeType, modifierId):
        return (
            self._validateAttribute(playerId, attributeType)
            and isinstance(modifierId, str)
            and bool(modifierId)
        )

    def _validateModifier(self, playerId, attributeType, modifierId, amount, operation, operand):
        if not self._validateKey(playerId, attributeType, modifierId):
            return False
        if isinstance(amount, bool) or not isinstance(amount, (int, long, float)):
            return False
        try:
            amount = float(amount)
        except OverflowError:
            return False
        if math.isnan(amount) or math.isinf(amount):
            return False
        if isinstance(operation, bool) or not isinstance(operation, (int, long)):
            return False
        if operation not in (
            AttributeModifierOperation.OperationAddition,
            AttributeModifierOperation.OperationMultiplyBase,
            AttributeModifierOperation.OperationMultiplyTotal,
            AttributeModifierOperation.OperationCap,
        ):
            return False
        # ponytail: 特殊属性没有引擎最小/最大值接口；需要时再扩展 OperandMin/OperandMax 状态。
        return (
            not isinstance(operand, bool)
            and isinstance(operand, (int, long))
            and operand == AttributeOperands.OperandCurrent
        )

    def _getBaseValue(self, playerId, attributeType):
        if attributeType == PlayerAttributeType.FLYING_ABILITY:
            value = compFactory.CreateFly(playerId).IsPlayerCanFly()
            return float(value) if isinstance(value, bool) else None
        if attributeType == PlayerAttributeType.STEP_HEIGHT:
            value = compFactory.CreateAttr(playerId).GetStepHeight()
            return float(value) if isinstance(value, (int, long, float)) and value > 0 else None
        if attributeType == PlayerAttributeType.ARMOR:
            # SetAttrValue(ARMOR) 设置额外护甲值；装备护甲由引擎另行叠加。
            return 0.0
        return None

    def _apply(self, key):
        modifiers = self._modifierMap.get(key, {})
        if not modifiers:
            return self._restore(key)
        value = calculateModifiedValue(
            self._baseValueMap[key], modifiers.values(), AttributeModifierOperation
        )
        return self._setValue(key[0], key[1], value)

    def _restore(self, key):
        if key not in self._baseValueMap:
            return True
        return self._setValue(key[0], key[1], self._baseValueMap[key])

    @staticmethod
    def _setValue(playerId, attributeType, value):
        if math.isnan(value) or math.isinf(value):
            return False
        if attributeType == PlayerAttributeType.FLYING_ABILITY:
            canFly = value > 0.0
            flyComp = compFactory.CreateFly(playerId)
            return flyComp.ChangePlayerFlyState(canFly, canFly and flyComp.IsPlayerFlying())
        if attributeType == PlayerAttributeType.STEP_HEIGHT:
            return value > 0.0 and compFactory.CreateAttr(playerId).SetStepHeight(value)
        if attributeType == PlayerAttributeType.ARMOR:
            armorValue = int(value)
            if armorValue < 0 or armorValue != value:
                return False
            return compFactory.CreateAttr(playerId).SetAttrValue(AttrType.ARMOR, armorValue, 0)
        return False

    def _removeEmptyKey(self, key):
        if self._modifierMap.get(key):
            return
        self._modifierMap.pop(key, None)
        self._baseValueMap.pop(key, None)
