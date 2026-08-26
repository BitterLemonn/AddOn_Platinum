# coding=utf-8
import math

try:
    integerTypes = (int, long)
except NameError:
    integerTypes = (int,)

from Script_Platinum.QuModLibs.Modules.Services.Server import BaseService
from Script_Platinum.QuModLibs.Server import Entity, compFactory, levelId, serverApi
from Script_Platinum.data.attributeModifier import calculateModifiedValue
from Script_Platinum.utils import developLogging as logging

minecraftEnum = serverApi.GetMinecraftEnum()
AttributeModifierOperation = minecraftEnum.AttributeModifierOperation
AttributeOperands = minecraftEnum.AttributeOperands
AttrType = minecraftEnum.AttrType
PlayerExhauseRatioType = getattr(minecraftEnum, "PlayerExhauseRatioType", None)
ItemPosType = getattr(minecraftEnum, "ItemPosType", None)
ArmorSlotType = getattr(minecraftEnum, "ArmorSlotType", None)


class PlatinumAttributeType(object):
    """实体属性修饰符类型。"""

    FLYING_ABILITY = "flying_ability"
    STEP_HEIGHT = "step_height"
    GRAVITY = "gravity"
    SCALE = "scale"
    ATTACK_SPEED_AMPLIFIER = "attack_speed_amplifier"
    PICKUP_AREA_HORIZONTAL = "pickup_area_horizontal"
    PICKUP_AREA_VERTICAL = "pickup_area_vertical"
    ARMOR = AttrType.ARMOR
    NATURAL_REGEN = "natural_regen"
    NATURAL_REGEN_LEVEL = "natural_regen_level"
    NATURAL_REGEN_TICK = "natural_regen_tick"
    NATURAL_STARVE = "natural_starve"
    STARVE_LEVEL = "starve_level"
    STARVE_TICK = "starve_tick"
    HUNGER_MAX = "hunger_max"
    MAX_EXHAUSTION = "max_exhaustion"
    EXHAUSTION_RATIO_GLOBAL = "exhaustion_ratio_global"
    EXHAUSTION_RATIO_HEAL = "exhaustion_ratio_heal"
    EXHAUSTION_RATIO_JUMP = "exhaustion_ratio_jump"
    EXHAUSTION_RATIO_SPRINT_JUMP = "exhaustion_ratio_sprint_jump"
    EXHAUSTION_RATIO_MINE = "exhaustion_ratio_mine"
    EXHAUSTION_RATIO_ATTACK = "exhaustion_ratio_attack"

    VALUES = (
        FLYING_ABILITY,
        STEP_HEIGHT,
        GRAVITY,
        SCALE,
        ATTACK_SPEED_AMPLIFIER,
        PICKUP_AREA_HORIZONTAL,
        PICKUP_AREA_VERTICAL,
        ARMOR,
        NATURAL_REGEN,
        NATURAL_REGEN_LEVEL,
        NATURAL_REGEN_TICK,
        NATURAL_STARVE,
        STARVE_LEVEL,
        STARVE_TICK,
        HUNGER_MAX,
        MAX_EXHAUSTION,
        EXHAUSTION_RATIO_GLOBAL,
        EXHAUSTION_RATIO_HEAL,
        EXHAUSTION_RATIO_JUMP,
        EXHAUSTION_RATIO_SPRINT_JUMP,
        EXHAUSTION_RATIO_MINE,
        EXHAUSTION_RATIO_ATTACK,
    )


@BaseService.Init
class PlatinumAttributeModifierService(BaseService):
    """统一管理实体属性修饰符。"""

    def __init__(self):
        BaseService.__init__(self)
        self._modifierMap = {}  # type: dict[tuple[str, str | int], dict[str, dict]]
        self._baseValueMap = {}  # type: dict[tuple[str, str | int], float]

    def addModifier(self, entityId, attributeType, modifierId, amount, operation, operand):
        if not self._validateModifier(entityId, attributeType, modifierId, amount, operation, operand):
            return False
        key = (entityId, attributeType)
        modifiers = self._modifierMap.setdefault(key, {})
        if modifierId in modifiers:
            logging.warning("实体 {} 已存在修饰符 {}".format(Entity(entityId).Identifier, modifierId))
            return False
        modifier = self._createModifier(modifierId, amount, operation, operand)
        oldValue = self._getDebugAttributeValue(key)
        if key not in self._baseValueMap:
            baseValue = self._getBaseValue(entityId, attributeType)
            if baseValue is None:
                logging.warning("实体 {} 没有属性 {} 的基础值".format(Entity(entityId).Identifier, attributeType))
                self._removeEmptyKey(key)
                return False
            self._baseValueMap[key] = baseValue
        modifiers[modifierId] = modifier
        if self._apply(key):
            self._logModifierChange("添加", key, modifier, oldValue)
            return True
        del modifiers[modifierId]
        self._removeEmptyKey(key)
        logging.error("实体 {} 添加修饰符 {} 失败".format(Entity(entityId).Identifier, modifierId))
        return False

    def updateModifier(self, entityId, attributeType, modifierId, amount, operation, operand):
        if not self._validateModifier(entityId, attributeType, modifierId, amount, operation, operand):
            logging.warning("实体 {} 无效的修饰符 {}".format(Entity(entityId).Identifier, modifierId))
            return False
        key = (entityId, attributeType)
        modifiers = self._modifierMap.get(key)
        if not modifiers or modifierId not in modifiers:
            logging.warning("实体 {} 不存在修饰符 {}".format(Entity(entityId).Identifier, modifierId))
            return False
        oldModifier = modifiers[modifierId]
        modifier = self._createModifier(modifierId, amount, operation, operand)
        modifiers[modifierId] = modifier
        if self._apply(key):
            return True
        modifiers[modifierId] = oldModifier
        logging.error("实体 {} 更新修饰符 {} 失败".format(Entity(entityId).Identifier, modifierId))
        return False

    def removeModifier(self, entityId, attributeType, modifierId):
        if not self._validateKey(entityId, attributeType, modifierId):
            logging.warning("实体 {} 无效的修饰符 {}".format(Entity(entityId).Identifier, modifierId))
            return False
        key = (entityId, attributeType)
        modifiers = self._modifierMap.get(key)
        if not modifiers or modifierId not in modifiers:
            logging.warning("实体 {} 不存在修饰符 {}".format(Entity(entityId).Identifier, modifierId))
            return False
        oldValue = self._getDebugAttributeValue(key)
        oldModifier = modifiers.pop(modifierId)
        if self._apply(key):
            self._logModifierChange("移除", key, oldModifier, oldValue)
            self._removeEmptyKey(key)
            return True
        modifiers[modifierId] = oldModifier
        logging.error("实体 {} 移除修饰符 {} 失败".format(Entity(entityId).Identifier, modifierId))
        return False

    def hasModifier(self, entityId, attributeType, modifierId):
        if not self._validateKey(entityId, attributeType, modifierId):
            return False
        return modifierId in self._modifierMap.get((entityId, attributeType), {})

    def getAllModifiers(self, entityId, attributeType):
        if not self._validateAttribute(entityId, attributeType):
            return []
        modifiers = self._modifierMap.get((entityId, attributeType), {})
        return [dict(modifiers[modifierId]) for modifierId in sorted(modifiers)]

    @BaseService.Listen("OnNewArmorExchangeServerEvent")
    def onNewArmorExchange(self, data):
        playerId = data.get("playerId")
        if not playerId:
            return
        key = (playerId, PlatinumAttributeType.ARMOR)
        if key in self._modifierMap:
            baseValue = self._getBaseValue(playerId, PlatinumAttributeType.ARMOR)
            if baseValue is not None:
                self._baseValueMap[key] = baseValue
                self._apply(key)

    @BaseService.Listen("PlayerIntendLeaveServerEvent")
    def onPlayerIntendLeave(self, data):
        self.clearEntity(data["playerId"], True)

    @BaseService.Listen("DelServerPlayerEvent")
    def onDelServerPlayer(self, data):
        self.clearEntity(data["id"], False)

    @BaseService.Listen("EntityRemoveEvent")
    def onEntityRemove(self, data):
        self.clearEntity(data["id"], False)

    def onServiceStop(self):
        BaseService.onServiceStop(self)
        for key in self._modifierMap.keys():
            self._restore(key)
        self._modifierMap.clear()
        self._baseValueMap.clear()

    def clearEntity(self, entityId, restore):
        keys = [key for key in self._modifierMap if key[0] == entityId]
        for key in keys:
            if restore:
                self._restore(key)
            self._modifierMap.pop(key, None)
            self._baseValueMap.pop(key, None)

    # 兼容旧方法
    def clearPlayer(self, entityId, restore):
        return self.clearEntity(entityId, restore)

    @staticmethod
    def _createModifier(modifierId, amount, operation, operand):
        return {
            "modifierId": modifierId,
            "amount": float(amount),
            "operation": operation,
            "operand": operand,
        }

    @staticmethod
    def _validateAttribute(entityId, attributeType):
        return isinstance(entityId, str) and bool(entityId) and attributeType in PlatinumAttributeType.VALUES

    def _validateKey(self, entityId, attributeType, modifierId):
        return self._validateAttribute(entityId, attributeType) and isinstance(modifierId, str) and bool(modifierId)

    def _validateModifier(self, entityId, attributeType, modifierId, amount, operation, operand):
        if not self._validateKey(entityId, attributeType, modifierId):
            return False
        if isinstance(amount, bool) or not isinstance(amount, integerTypes + (float,)):
            return False
        try:
            amount = float(amount)
        except OverflowError:
            return False
        if math.isnan(amount) or math.isinf(amount):
            return False
        if isinstance(operation, bool) or not isinstance(operation, integerTypes):
            return False
        if operation not in (
            AttributeModifierOperation.OperationAddition,
            AttributeModifierOperation.OperationMultiplyBase,
            AttributeModifierOperation.OperationMultiplyTotal,
            AttributeModifierOperation.OperationCap,
        ):
            return False
        # ponytail: 自定义属性没有引擎最小/最大值接口；需要时再扩展 OperandMin/OperandMax 状态。
        return (
            not isinstance(operand, bool)
            and isinstance(operand, integerTypes)
            and operand == AttributeOperands.OperandCurrent
        )

    @staticmethod
    def _getEquippedArmorValue(entityId):
        itemComp = compFactory.CreateItem(entityId)
        if not itemComp:
            return 0.0
        if ItemPosType is None or ArmorSlotType is None:
            return 0.0
        totalArmor = 0.0
        armorSlots = (
            ArmorSlotType.HEAD,
            ArmorSlotType.BODY,
            ArmorSlotType.LEG,
            ArmorSlotType.FOOT,
        )
        for slotPos in armorSlots:
            itemDict = itemComp.GetEntityItem(ItemPosType.ARMOR, slotPos)
            if not itemDict or not isinstance(itemDict, dict):
                continue
            itemName = itemDict.get("newItemName") or itemDict.get("itemName")
            if not itemName or not isinstance(itemName, str):
                continue
            itemInfo = itemComp.GetItemBasicInfo(itemName, itemDict.get("newAuxValue", 0))
            if itemInfo and isinstance(itemInfo, dict):
                totalArmor += float(itemInfo.get("armorDefense", 0))
        return totalArmor

    def _getBaseValue(self, entityId, attributeType):
        if attributeType == PlatinumAttributeType.FLYING_ABILITY:
            value = compFactory.CreateFly(entityId).IsPlayerCanFly()
            return float(value) if isinstance(value, bool) else None
        if attributeType == PlatinumAttributeType.STEP_HEIGHT:
            value = compFactory.CreateAttr(entityId).GetStepHeight()
            return float(value) if isinstance(value, integerTypes + (float,)) and value > 0 else None
        if attributeType == PlatinumAttributeType.GRAVITY:
            gravityComp = compFactory.CreateGravity(entityId)
            value = gravityComp.GetGravity() if gravityComp else 0.0
            if isinstance(value, integerTypes + (float,)) and value != 0.0:
                return float(value)
            gameComp = compFactory.CreateGame(levelId)
            levelGravity = gameComp.GetLevelGravity() if gameComp else -0.08
            return float(levelGravity) if isinstance(levelGravity, integerTypes + (float,)) else -0.08
        if attributeType == PlatinumAttributeType.SCALE:
            return 1.0
        if attributeType == PlatinumAttributeType.ATTACK_SPEED_AMPLIFIER:
            return 1.0
        if attributeType in (
            PlatinumAttributeType.PICKUP_AREA_HORIZONTAL,
            PlatinumAttributeType.PICKUP_AREA_VERTICAL,
        ):
            return 0.0
        if attributeType == PlatinumAttributeType.ARMOR:
            return self._getEquippedArmorValue(entityId)
        if attributeType == PlatinumAttributeType.HUNGER_MAX:
            value = compFactory.CreateAttr(entityId).GetAttrMaxValue(AttrType.HUNGER)
            return float(value) if isinstance(value, integerTypes + (float,)) and value > 0 else None
        playerComp = compFactory.CreatePlayer(entityId)
        if attributeType == PlatinumAttributeType.NATURAL_REGEN:
            value = playerComp.IsPlayerNaturalRegen()
            return float(value) if isinstance(value, bool) else None
        if attributeType == PlatinumAttributeType.NATURAL_REGEN_LEVEL:
            value = playerComp.GetPlayerHealthLevel()
            if isinstance(value, bool) or not isinstance(value, integerTypes) or value < 0:
                return None
            return float(value)
        if attributeType == PlatinumAttributeType.NATURAL_REGEN_TICK:
            value = playerComp.GetPlayerHealthTick()
            if isinstance(value, bool) or not isinstance(value, integerTypes) or value < 1:
                return None
            return float(value)
        if attributeType == PlatinumAttributeType.NATURAL_STARVE:
            value = playerComp.IsPlayerNaturalStarve()
            return float(value) if isinstance(value, bool) else None
        if attributeType == PlatinumAttributeType.STARVE_LEVEL:
            value = playerComp.GetPlayerStarveLevel()
            if isinstance(value, bool) or not isinstance(value, integerTypes) or value < 0:
                return None
            return float(value)
        if attributeType == PlatinumAttributeType.STARVE_TICK:
            value = playerComp.GetPlayerStarveTick()
            if isinstance(value, bool) or not isinstance(value, integerTypes) or value < 1:
                return None
            return float(value)
        if attributeType == PlatinumAttributeType.MAX_EXHAUSTION:
            value = playerComp.GetPlayerMaxExhaustionValue()
            return float(value) if isinstance(value, integerTypes + (float,)) and value > 0 else None
        if PlayerExhauseRatioType is not None:
            ratioTypeMap = {
                PlatinumAttributeType.EXHAUSTION_RATIO_GLOBAL: PlayerExhauseRatioType.GLOBAL,
                PlatinumAttributeType.EXHAUSTION_RATIO_HEAL: PlayerExhauseRatioType.HEAL,
                PlatinumAttributeType.EXHAUSTION_RATIO_JUMP: PlayerExhauseRatioType.JUMP,
                PlatinumAttributeType.EXHAUSTION_RATIO_SPRINT_JUMP: PlayerExhauseRatioType.SPRINT_JUMP,
                PlatinumAttributeType.EXHAUSTION_RATIO_MINE: PlayerExhauseRatioType.MINE,
                PlatinumAttributeType.EXHAUSTION_RATIO_ATTACK: PlayerExhauseRatioType.ATTACK,
            }
            if attributeType in ratioTypeMap:
                value = playerComp.GetPlayerExhaustionRatioByType(ratioTypeMap[attributeType])
                return float(value) if isinstance(value, integerTypes + (float,)) and value >= 0 else None
        return None

    def _apply(self, key):
        modifiers = self._modifierMap.get(key, {})
        if not modifiers:
            return self._restore(key)
        baseValue = self._baseValueMap[key]
        value = calculateModifiedValue(baseValue, modifiers.values(), AttributeModifierOperation)
        return self._setValue(key[0], key[1], value, baseValue)

    def _restore(self, key):
        if key not in self._baseValueMap:
            return True
        baseValue = self._baseValueMap[key]
        return self._setValue(key[0], key[1], baseValue, baseValue)

    def _getCalculatedValue(self, entityId, attributeType):
        key = (entityId, attributeType)
        if key not in self._baseValueMap:
            baseValue = self._getBaseValue(entityId, attributeType)
            return float(baseValue) if baseValue is not None else 0.0
        modifiers = self._modifierMap.get(key, {})
        if not modifiers:
            return self._baseValueMap[key]
        return calculateModifiedValue(self._baseValueMap[key], modifiers.values(), AttributeModifierOperation)

    def _getDebugAttributeValue(self, key):
        if not logging.isEnabledFor("DEBUG"):
            return None
        return self._getCalculatedValue(key[0], key[1])

    def _logModifierChange(self, action, key, modifier, oldValue):
        if not logging.isEnabledFor("DEBUG"):
            return
        entityId, attributeType = key
        newValue = self._getDebugAttributeValue(key)
        logging.debug(
            "铂: {}属性修饰符 entityId={}, attributeType={}, modifierId={}, amount={}, operation={}, operand={}, "
            "属性值: {} -> {}".format(
                action,
                entityId,
                attributeType,
                modifier["modifierId"],
                modifier["amount"],
                modifier["operation"],
                modifier["operand"],
                oldValue,
                newValue,
            )
        )

    def _setValue(self, entityId, attributeType, value, baseValue=0.0):
        if math.isnan(value) or math.isinf(value):
            return False
        if attributeType == PlatinumAttributeType.FLYING_ABILITY:
            canFly = value > 0.0
            flyComp = compFactory.CreateFly(entityId)
            return flyComp.ChangePlayerFlyState(canFly, canFly and flyComp.IsPlayerFlying())
        if attributeType == PlatinumAttributeType.STEP_HEIGHT:
            return value > 0.0 and compFactory.CreateAttr(entityId).SetStepHeight(value)
        if attributeType == PlatinumAttributeType.GRAVITY:
            gravityComp = compFactory.CreateGravity(entityId)
            return bool(gravityComp and gravityComp.SetGravity(float(value)))
        if attributeType == PlatinumAttributeType.SCALE:
            if value <= 0.0:
                return False
            scaleComp = compFactory.CreateScale(entityId)
            return bool(scaleComp and scaleComp.SetEntityScale(entityId, float(value)) == 1)
        if attributeType == PlatinumAttributeType.ATTACK_SPEED_AMPLIFIER:
            if value < 0.5 or value > 2.0:
                return False
            playerComp = compFactory.CreatePlayer(entityId)
            return bool(playerComp and playerComp.SetPlayerAttackSpeedAmplifier(float(value)))
        if attributeType in (
            PlatinumAttributeType.PICKUP_AREA_HORIZONTAL,
            PlatinumAttributeType.PICKUP_AREA_VERTICAL,
        ):
            if attributeType == PlatinumAttributeType.PICKUP_AREA_HORIZONTAL:
                h = max(0.0, float(value))
                v = max(0.0, float(self._getCalculatedValue(entityId, PlatinumAttributeType.PICKUP_AREA_VERTICAL)))
            else:
                h = max(0.0, float(self._getCalculatedValue(entityId, PlatinumAttributeType.PICKUP_AREA_HORIZONTAL)))
                v = max(0.0, float(value))
            playerComp = compFactory.CreatePlayer(entityId)
            return bool(playerComp and playerComp.SetPickUpArea((h, v, h)))
        if attributeType == PlatinumAttributeType.ARMOR:
            # 装备护甲通过 _getBaseValue 参与乘算/加算，SetAttrValue 仅写入额外护甲差值（总护甲 - 装备护甲）。
            extraArmor = int(round(value - baseValue))
            if extraArmor < 0:
                extraArmor = 0
            return compFactory.CreateAttr(entityId).SetAttrValue(AttrType.ARMOR, extraArmor, 0)
        if attributeType == PlatinumAttributeType.HUNGER_MAX:
            if value <= 0.0:
                return False
            return compFactory.CreateAttr(entityId).SetAttrMaxValue(AttrType.HUNGER, float(value))
        playerComp = compFactory.CreatePlayer(entityId)
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
        if attributeType == PlatinumAttributeType.NATURAL_STARVE:
            return playerComp.SetPlayerNaturalStarve(value > 0.0)
        if attributeType == PlatinumAttributeType.STARVE_LEVEL:
            starveLevel = int(value)
            healthLevel = playerComp.GetPlayerHealthLevel()
            if starveLevel < 0 or starveLevel != value or (healthLevel >= 0 and starveLevel > healthLevel):
                return False
            return playerComp.SetPlayerStarveLevel(starveLevel)
        if attributeType == PlatinumAttributeType.STARVE_TICK:
            starveTick = int(value)
            if starveTick < 1 or starveTick != value:
                return False
            return playerComp.SetPlayerStarveTick(starveTick)
        if attributeType == PlatinumAttributeType.MAX_EXHAUSTION:
            if value <= 0.0:
                return False
            return playerComp.SetPlayerMaxExhaustionValue(float(value))
        if PlayerExhauseRatioType is not None:
            ratioTypeMap = {
                PlatinumAttributeType.EXHAUSTION_RATIO_GLOBAL: PlayerExhauseRatioType.GLOBAL,
                PlatinumAttributeType.EXHAUSTION_RATIO_HEAL: PlayerExhauseRatioType.HEAL,
                PlatinumAttributeType.EXHAUSTION_RATIO_JUMP: PlayerExhauseRatioType.JUMP,
                PlatinumAttributeType.EXHAUSTION_RATIO_SPRINT_JUMP: PlayerExhauseRatioType.SPRINT_JUMP,
                PlatinumAttributeType.EXHAUSTION_RATIO_MINE: PlayerExhauseRatioType.MINE,
                PlatinumAttributeType.EXHAUSTION_RATIO_ATTACK: PlayerExhauseRatioType.ATTACK,
            }
            if attributeType in ratioTypeMap:
                if value < 0.0:
                    return False
                return playerComp.SetPlayerExhaustionRatioByType(ratioTypeMap[attributeType], float(value))
        return False

    def _removeEmptyKey(self, key):
        if self._modifierMap.get(key):
            return
        self._modifierMap.pop(key, None)
        self._baseValueMap.pop(key, None)
