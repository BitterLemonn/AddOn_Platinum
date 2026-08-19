# coding=utf-8
import math

from Script_Platinum.QuModLibs.Modules.Services.Server import BaseService
from Script_Platinum.QuModLibs.Server import compFactory, serverApi
from Script_Platinum.data.attributeModifier import calculateModifiedValue

minecraftEnum = serverApi.GetMinecraftEnum()
AttributeModifierOperation = minecraftEnum.AttributeModifierOperation
AttributeOperands = minecraftEnum.AttributeOperands
AttrType = minecraftEnum.AttrType


class PlatinumAttributeType(object):
    """玩家属性修饰符类型。"""

    FLYING_ABILITY = "flying_ability"
    STEP_HEIGHT = "step_height"
    ARMOR = AttrType.ARMOR
    HUNGER = AttrType.HUNGER
    NATURAL_REGEN = "natural_regen"
    NATURAL_REGEN_LEVEL = "natural_regen_level"
    NATURAL_REGEN_TICK = "natural_regen_tick"

    VALUES = (
        FLYING_ABILITY,
        STEP_HEIGHT,
        ARMOR,
        HUNGER,
        NATURAL_REGEN,
        NATURAL_REGEN_LEVEL,
        NATURAL_REGEN_TICK,
    )


@BaseService.Init
class PlatinumAttributeModifierService(BaseService):
    """统一管理玩家属性修饰符。"""

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
        modifier = self._createModifier(modifierId, amount, operation, operand)
        if attributeType == PlatinumAttributeType.HUNGER:
            if not compFactory.CreateAttr(playerId).AddModifier(
                attributeType,
                modifierId,
                modifier["amount"],
                operation,
                operand,
            ):
                self._removeEmptyKey(key)
                return False
            modifiers[modifierId] = modifier
            return True
        if key not in self._baseValueMap:
            baseValue = self._getBaseValue(playerId, attributeType)
            if baseValue is None:
                self._removeEmptyKey(key)
                return False
            self._baseValueMap[key] = baseValue
        modifiers[modifierId] = modifier
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
        modifier = self._createModifier(modifierId, amount, operation, operand)
        if attributeType == PlatinumAttributeType.HUNGER:
            if not compFactory.CreateAttr(playerId).UpdateModifier(
                attributeType,
                modifierId,
                modifier["amount"],
                operation,
                operand,
            ):
                return False
            modifiers[modifierId] = modifier
            return True
        modifiers[modifierId] = modifier
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
        if attributeType == PlatinumAttributeType.HUNGER:
            if compFactory.CreateAttr(playerId).RemoveModifier(attributeType, modifierId):
                self._removeEmptyKey(key)
                return True
            modifiers[modifierId] = oldModifier
            return False
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
        return isinstance(playerId, str) and bool(playerId) and attributeType in PlatinumAttributeType.VALUES

    def _validateKey(self, playerId, attributeType, modifierId):
        return self._validateAttribute(playerId, attributeType) and isinstance(modifierId, str) and bool(modifierId)

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
        if attributeType == PlatinumAttributeType.HUNGER:
            return (
                not isinstance(operand, bool)
                and isinstance(operand, (int, long))
                and operand
                in (
                    AttributeOperands.OperandMin,
                    AttributeOperands.OperandMax,
                    AttributeOperands.OperandCurrent,
                )
            )
        # ponytail: 自定义属性没有引擎最小/最大值接口；需要时再扩展 OperandMin/OperandMax 状态。
        return (
            not isinstance(operand, bool)
            and isinstance(operand, (int, long))
            and operand == AttributeOperands.OperandCurrent
        )

    def _getBaseValue(self, playerId, attributeType):
        if attributeType == PlatinumAttributeType.FLYING_ABILITY:
            value = compFactory.CreateFly(playerId).IsPlayerCanFly()
            return float(value) if isinstance(value, bool) else None
        if attributeType == PlatinumAttributeType.STEP_HEIGHT:
            value = compFactory.CreateAttr(playerId).GetStepHeight()
            return float(value) if isinstance(value, (int, long, float)) and value > 0 else None
        if attributeType == PlatinumAttributeType.ARMOR:
            # SetAttrValue(ARMOR) 设置额外护甲值；装备护甲由引擎另行叠加。
            return 0.0
        playerComp = compFactory.CreatePlayer(playerId)
        if attributeType == PlatinumAttributeType.NATURAL_REGEN:
            value = playerComp.IsPlayerNaturalRegen()
            return float(value) if isinstance(value, bool) else None
        if attributeType == PlatinumAttributeType.NATURAL_REGEN_LEVEL:
            value = playerComp.GetPlayerHealthLevel()
            if isinstance(value, bool) or not isinstance(value, (int, long)) or value < 0:
                return None
            return float(value)
        if attributeType == PlatinumAttributeType.NATURAL_REGEN_TICK:
            value = playerComp.GetPlayerHealthTick()
            if isinstance(value, bool) or not isinstance(value, (int, long)) or value < 1:
                return None
            return float(value)
        return None

    def _apply(self, key):
        modifiers = self._modifierMap.get(key, {})
        if not modifiers:
            return self._restore(key)
        value = calculateModifiedValue(self._baseValueMap[key], modifiers.values(), AttributeModifierOperation)
        return self._setValue(key[0], key[1], value)

    def _restore(self, key):
        if key[1] == PlatinumAttributeType.HUNGER:
            result = True
            attrComp = compFactory.CreateAttr(key[0])
            for modifierId in self._modifierMap.get(key, {}):
                if not attrComp.RemoveModifier(key[1], modifierId):
                    result = False
            return result
        if key not in self._baseValueMap:
            return True
        return self._setValue(key[0], key[1], self._baseValueMap[key])

    @staticmethod
    def _setValue(playerId, attributeType, value):
        if math.isnan(value) or math.isinf(value):
            return False
        if attributeType == PlatinumAttributeType.FLYING_ABILITY:
            canFly = value > 0.0
            flyComp = compFactory.CreateFly(playerId)
            return flyComp.ChangePlayerFlyState(canFly, canFly and flyComp.IsPlayerFlying())
        if attributeType == PlatinumAttributeType.STEP_HEIGHT:
            return value > 0.0 and compFactory.CreateAttr(playerId).SetStepHeight(value)
        if attributeType == PlatinumAttributeType.ARMOR:
            armorValue = int(value)
            if armorValue < 0 or armorValue != value:
                return False
            return compFactory.CreateAttr(playerId).SetAttrValue(AttrType.ARMOR, armorValue, 0)
        playerComp = compFactory.CreatePlayer(playerId)
        if attributeType == PlatinumAttributeType.NATURAL_REGEN:
            return playerComp.SetPlayerNaturalRegen(value > 0.0)
        if attributeType == PlatinumAttributeType.NATURAL_REGEN_LEVEL:
            healthLevel = int(value)
            starveLevel = playerComp.GetPlayerStarveLevel()
            if healthLevel < 0 or healthLevel != value or starveLevel < 0 or healthLevel < starveLevel:
                return False
            return playerComp.SetPlayerHealthLevel(healthLevel)
        if attributeType == PlatinumAttributeType.NATURAL_REGEN_TICK:
            healthTick = int(value)
            if healthTick < 1 or healthTick != value:
                return False
            return playerComp.SetPlayerHealthTick(healthTick)
        return False

    def _removeEmptyKey(self, key):
        if self._modifierMap.get(key):
            return
        self._modifierMap.pop(key, None)
        self._baseValueMap.pop(key, None)
