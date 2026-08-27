# coding=utf-8
import json
import math
import random
import time

try:
    integerTypes = (int, long)
    stringTypes = (str, unicode)
except NameError:
    integerTypes = (int,)
    stringTypes = (str,)

from Script_Platinum.QuModLibs.Modules.Services.Server import BaseService, QRequests
from Script_Platinum.QuModLibs.Server import Entity, System, compFactory, levelId, serverApi
from Script_Platinum.data.attributeModifier import (
    calculateModifiedValue,
    calculateProtectionMultiplier,
)
from Script_Platinum.server.attribute.fortuneManager import FortuneManager
from Script_Platinum.utils import developLogging as logging
from Script_Platinum.utils.ItemFactory import ItemFactory

minecraftEnum = serverApi.GetMinecraftEnum()
AttributeModifierOperation = minecraftEnum.AttributeModifierOperation
AttributeOperands = minecraftEnum.AttributeOperands
AttrType = minecraftEnum.AttrType
PlayerExhauseRatioType = minecraftEnum.PlayerExhauseRatioType
ItemPosType = minecraftEnum.ItemPosType
ArmorSlotType = minecraftEnum.ArmorSlotType
ActorDamageCause = minecraftEnum.ActorDamageCause
EnchantType = minecraftEnum.EnchantType
GameType = minecraftEnum.GameType

BYPASS_INVULNERABLE_CAUSES = (
    ActorDamageCause.Void,
    ActorDamageCause.Suicide,
    ActorDamageCause.SelfDestruct,
    ActorDamageCause.Override,
    ActorDamageCause.NONE,
)

BYPASS_PROTECTION_CAUSES = (
    ActorDamageCause.Suicide,
    ActorDamageCause.SelfDestruct,
    ActorDamageCause.Override,
    ActorDamageCause.NONE,
)


class PlatinumAttributeType(object):
    """实体属性修饰符类型。"""

    FLYING_ABILITY = "flying_ability"  # 创造飞行能力
    STEP_HEIGHT = "step_height"  # 台阶高度
    GRAVITY = "gravity"  # 重力
    SCALE = "scale"  # 体型缩放
    ATTACK_SPEED_AMPLIFIER = "attack_speed_amplifier"  # 攻击速度倍率
    PICKUP_AREA_HORIZONTAL = "pickup_area_horizontal"  # 水平拾取范围
    PICKUP_AREA_VERTICAL = "pickup_area_vertical"  # 垂直拾取范围
    INVULNERABLE_TIME = "invulnerable_time"  # 无敌时间(秒)
    INVULNERABILITY_TIME = INVULNERABLE_TIME  # 无敌时间别名
    LIFESTEAL_MELEE = "lifesteal_melee"  # 近战吸血比例
    LIFESTEAL_PROJECTILE = "lifesteal_projectile"  # 投射物吸血比例
    KILL_EXP_MULTIPLIER = "kill_exp_multiplier"  # 击杀生物经验倍率
    EXP_MULTIPLIER = "exp_multiplier"  # 获取经验球倍率
    INTERACT_RANGE = "interact_range"  # 交互范围/触及距离
    PICK_RANGE = INTERACT_RANGE  # 交互范围别名
    BURNING_TIME = "burning_time"  # 燃烧时间倍率
    BURN_TIME = BURNING_TIME  # 燃烧时间别名
    ARMOR = AttrType.ARMOR  # 护甲值
    MAX_AIR_SUPPLY = "max_air_supply"  # 最大氧气值(刻)
    MAX_OXYGEN = MAX_AIR_SUPPLY  # 最大氧气值别名
    RECOVER_TOTAL_AIR_SUPPLY_TIME = "recover_total_air_supply_time"  # 恢复最大氧气量时间(秒)
    NATURAL_REGEN = "natural_regen"  # 自然生命恢复开关
    NATURAL_REGEN_LEVEL = "natural_regen_level"  # 自然生命恢复饥饿门槛
    NATURAL_REGEN_TICK = "natural_regen_tick"  # 自然生命恢复间隔(刻)
    NATURAL_STARVE = "natural_starve"  # 饥饿扣血开关
    STARVE_LEVEL = "starve_level"  # 饥饿扣血门槛
    STARVE_TICK = "starve_tick"  # 饥饿扣血间隔(刻)
    MAX_EXHAUSTION = "max_exhaustion"  # 最大消耗度
    EXHAUSTION_RATIO_GLOBAL = "exhaustion_ratio_global"  # 全局饥饿消耗倍率
    EXHAUSTION_RATIO_HEAL = "exhaustion_ratio_heal"  # 回血饥饿消耗倍率
    EXHAUSTION_RATIO_JUMP = "exhaustion_ratio_jump"  # 跳跃饥饿消耗倍率
    EXHAUSTION_RATIO_SPRINT_JUMP = "exhaustion_ratio_sprint_jump"  # 疾跑跳跃饥饿消耗倍率
    EXHAUSTION_RATIO_MINE = "exhaustion_ratio_mine"  # 挖掘饥饿消耗倍率
    EXHAUSTION_RATIO_ATTACK = "exhaustion_ratio_attack"  # 攻击饥饿消耗倍率
    FORTUNE_LEVEL = "fortune_level"  # 时运等级
    FORTUNE = FORTUNE_LEVEL  # 时运等级别名
    LOOTING_LEVEL = "looting_level"  # 抢夺等级
    LOOTING = LOOTING_LEVEL  # 抢夺等级别名
    PROTECTION_ALL = "protection_all"
    PROTECTION_CONTACT = "protection_contact"
    PROTECTION_ENTITY_ATTACK = "protection_entity_attack"
    PROTECTION_PROJECTILE = "protection_projectile"
    PROTECTION_SUFFOCATION = "protection_suffocation"
    PROTECTION_FALL = "protection_fall"
    PROTECTION_FIRE = "protection_fire"
    PROTECTION_FIRE_TICK = "protection_fire_tick"
    PROTECTION_LAVA = "protection_lava"
    PROTECTION_DROWNING = "protection_drowning"
    PROTECTION_VOID = "protection_void"
    PROTECTION_BLOCK_EXPLOSION = "protection_block_explosion"
    PROTECTION_ENTITY_EXPLOSION = "protection_entity_explosion"
    PROTECTION_STARVE = "protection_starve"
    PROTECTION_ANVIL = "protection_anvil"
    PROTECTION_THORNS = "protection_thorns"
    PROTECTION_FALLING_BLOCK = "protection_falling_block"
    PROTECTION_PISTON = "protection_piston"
    PROTECTION_FLY_INTO_WALL = "protection_fly_into_wall"
    PROTECTION_MAGMA = "protection_magma"
    PROTECTION_FIREWORKS = "protection_fireworks"
    PROTECTION_LIGHTNING = "protection_lightning"
    PROTECTION_FREEZING = "protection_freezing"
    PROTECTION_STALACTITE = "protection_stalactite"
    PROTECTION_STALAGMITE = "protection_stalagmite"
    PROTECTION_RAM_ATTACK = "protection_ram_attack"
    PROTECTION_CUSTOM = "protection_custom"
    PROTECTION_SONIC_BOOM = "protection_sonic_boom"
    PROTECTION_CAMPFIRE = "protection_campfire"
    PROTECTION_SOUL_CAMPFIRE = "protection_soul_campfire"
    PROTECTION_MACE_SMASH = "protection_mace_smash"
    PROTECTION_MAGIC = "protection_magic"

    PROTECTION_DAMAGE_EVENT_TYPES = (
        PROTECTION_CONTACT,
        PROTECTION_ENTITY_ATTACK,
        PROTECTION_PROJECTILE,
        PROTECTION_SUFFOCATION,
        PROTECTION_FALL,
        PROTECTION_FIRE,
        PROTECTION_FIRE_TICK,
        PROTECTION_LAVA,
        PROTECTION_DROWNING,
        PROTECTION_VOID,
        PROTECTION_BLOCK_EXPLOSION,
        PROTECTION_ENTITY_EXPLOSION,
        PROTECTION_STARVE,
        PROTECTION_ANVIL,
        PROTECTION_THORNS,
        PROTECTION_FALLING_BLOCK,
        PROTECTION_PISTON,
        PROTECTION_FLY_INTO_WALL,
        PROTECTION_MAGMA,
        PROTECTION_FIREWORKS,
        PROTECTION_LIGHTNING,
        PROTECTION_FREEZING,
        PROTECTION_STALACTITE,
        PROTECTION_STALAGMITE,
        PROTECTION_RAM_ATTACK,
        PROTECTION_CUSTOM,
        PROTECTION_SONIC_BOOM,
        PROTECTION_CAMPFIRE,
        PROTECTION_SOUL_CAMPFIRE,
        PROTECTION_MACE_SMASH,
    )

    VALUES = (
        (
            FLYING_ABILITY,
            STEP_HEIGHT,
            GRAVITY,
            SCALE,
            ATTACK_SPEED_AMPLIFIER,
            PICKUP_AREA_HORIZONTAL,
            PICKUP_AREA_VERTICAL,
            INVULNERABLE_TIME,
            LIFESTEAL_MELEE,
            LIFESTEAL_PROJECTILE,
            KILL_EXP_MULTIPLIER,
            EXP_MULTIPLIER,
            INTERACT_RANGE,
            BURNING_TIME,
            ARMOR,
            MAX_AIR_SUPPLY,
            RECOVER_TOTAL_AIR_SUPPLY_TIME,
            NATURAL_REGEN,
            NATURAL_REGEN_LEVEL,
            NATURAL_REGEN_TICK,
            NATURAL_STARVE,
            STARVE_LEVEL,
            STARVE_TICK,
            MAX_EXHAUSTION,
            EXHAUSTION_RATIO_GLOBAL,
            EXHAUSTION_RATIO_HEAL,
            EXHAUSTION_RATIO_JUMP,
            EXHAUSTION_RATIO_SPRINT_JUMP,
            EXHAUSTION_RATIO_MINE,
            EXHAUSTION_RATIO_ATTACK,
            FORTUNE_LEVEL,
            LOOTING_LEVEL,
        )
        + PROTECTION_DAMAGE_EVENT_TYPES
        + (PROTECTION_ALL, PROTECTION_MAGIC)
    )


PROTECTION_CAUSE_ATTRIBUTE_MAP = {
    "contact": PlatinumAttributeType.PROTECTION_CONTACT,
    "entity_attack": PlatinumAttributeType.PROTECTION_ENTITY_ATTACK,
    "projectile": PlatinumAttributeType.PROTECTION_PROJECTILE,
    "suffocation": PlatinumAttributeType.PROTECTION_SUFFOCATION,
    "fall": PlatinumAttributeType.PROTECTION_FALL,
    "fire": PlatinumAttributeType.PROTECTION_FIRE,
    "fire_tick": PlatinumAttributeType.PROTECTION_FIRE_TICK,
    "lava": PlatinumAttributeType.PROTECTION_LAVA,
    "drowning": PlatinumAttributeType.PROTECTION_DROWNING,
    "void": PlatinumAttributeType.PROTECTION_VOID,
    "block_explosion": PlatinumAttributeType.PROTECTION_BLOCK_EXPLOSION,
    "entity_explosion": PlatinumAttributeType.PROTECTION_ENTITY_EXPLOSION,
    "starve": PlatinumAttributeType.PROTECTION_STARVE,
    "anvil": PlatinumAttributeType.PROTECTION_ANVIL,
    "thorns": PlatinumAttributeType.PROTECTION_THORNS,
    "falling_block": PlatinumAttributeType.PROTECTION_FALLING_BLOCK,
    "piston": PlatinumAttributeType.PROTECTION_PISTON,
    "fly_into_wall": PlatinumAttributeType.PROTECTION_FLY_INTO_WALL,
    "magma": PlatinumAttributeType.PROTECTION_MAGMA,
    "fireworks": PlatinumAttributeType.PROTECTION_FIREWORKS,
    "lightning": PlatinumAttributeType.PROTECTION_LIGHTNING,
    "freezing": PlatinumAttributeType.PROTECTION_FREEZING,
    "stalactite": PlatinumAttributeType.PROTECTION_STALACTITE,
    "stalagmite": PlatinumAttributeType.PROTECTION_STALAGMITE,
    "ram_attack": PlatinumAttributeType.PROTECTION_RAM_ATTACK,
    "custom": PlatinumAttributeType.PROTECTION_CUSTOM,
    "sonic_boom": PlatinumAttributeType.PROTECTION_SONIC_BOOM,
    "campfire": PlatinumAttributeType.PROTECTION_CAMPFIRE,
    "soul_campfire": PlatinumAttributeType.PROTECTION_SOUL_CAMPFIRE,
    "mace_smash": PlatinumAttributeType.PROTECTION_MACE_SMASH,
}


@BaseService.Init
class PlatinumAttributeModifierService(BaseService):
    """统一管理实体属性修饰符。"""

    def __init__(self):
        BaseService.__init__(self)
        self._modifierMap = {}  # type: dict[tuple[str, str | int], dict[str, dict]]
        self._baseValueMap = {}  # type: dict[tuple[str, str | int], float]
        self._invulnerableUntil = {}  # type: dict[str, float]
        self._burningMultiplier = {}  # type: dict[str, float]
        self._protectionMagicBaseMap = {}  # type: dict[str, dict | None]
        self.fortuneManager = FortuneManager()

    def addModifier(self, entityId, attributeType, *modifierArgs):
        if not self._validateModifier(entityId, attributeType, modifierArgs):
            return False
        modifierId = modifierArgs[0]
        key = (entityId, attributeType)
        modifiers = self._modifierMap.setdefault(key, {})
        if modifierId in modifiers:
            logging.warning("实体 {} 已存在修饰符 {}".format(Entity(entityId).Identifier, modifierId))
            return False
        modifier = self._createModifier(*modifierArgs)
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

    def updateModifier(self, entityId, attributeType, *modifierArgs):
        modifierId = modifierArgs[0] if modifierArgs else None
        if not self._validateModifier(entityId, attributeType, modifierArgs):
            logging.warning("实体 {} 无效的修饰符 {}".format(Entity(entityId).Identifier, modifierId))
            return False
        key = (entityId, attributeType)
        modifiers = self._modifierMap.get(key)
        if not modifiers or modifierId not in modifiers:
            logging.warning("实体 {} 不存在修饰符 {}".format(Entity(entityId).Identifier, modifierId))
            return False
        oldModifier = modifiers[modifierId]
        modifier = self._createModifier(*modifierArgs)
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

    @BaseService.Listen("DamageEvent")
    def onDamageEvent(self, data):
        entityId = data.get("entityId")
        if not entityId:
            return
        now = time.time()
        # 清理过期记录
        expired = [eid for eid, exp in self._invulnerableUntil.items() if exp <= now]
        for eid in expired:
            self._invulnerableUntil.pop(eid, None)
        # 旁路不可无敌伤害
        cause = data.get("cause")
        self._applyDamageProtection(data, entityId, cause)
        if cause in BYPASS_INVULNERABLE_CAUSES:
            return
        # 处于生效中的无敌保护期 -> 免疫伤害与击退
        if entityId in self._invulnerableUntil and now < self._invulnerableUntil[entityId]:
            data["damage"] = 0
            data["knock"] = False
            return
        # 未在保护期 -> 检查是否有无敌时间修饰符，若有则计算保护时长并激活
        key = (entityId, PlatinumAttributeType.INVULNERABLE_TIME)
        if key in self._modifierMap and self._modifierMap[key]:
            invulnerableDuration = self._getCalculatedValue(entityId, PlatinumAttributeType.INVULNERABLE_TIME)
            if invulnerableDuration > 0.0:
                self._invulnerableUntil[entityId] = now + invulnerableDuration

    def _applyDamageProtection(self, data, entityId, cause):
        if cause == "magic" or cause in BYPASS_PROTECTION_CAUSES:
            return
        attributeType = PROTECTION_CAUSE_ATTRIBUTE_MAP.get(cause)
        allKey = (entityId, PlatinumAttributeType.PROTECTION_ALL)
        typeKey = (entityId, attributeType)
        hasAllProtection = bool(self._modifierMap.get(allKey))
        hasTypeProtection = attributeType is not None and bool(self._modifierMap.get(typeKey))
        if not hasAllProtection and not hasTypeProtection:
            return
        damage = data.get("damage")
        if isinstance(damage, bool) or not isinstance(damage, integerTypes + (float,)):
            return
        multiplier = 1.0
        if hasAllProtection:
            multiplier *= calculateProtectionMultiplier(
                self._getCalculatedValue(entityId, PlatinumAttributeType.PROTECTION_ALL)
            )
        if hasTypeProtection:
            multiplier *= calculateProtectionMultiplier(self._getCalculatedValue(entityId, attributeType))
        data["damage"] = float(damage) * multiplier

    @BaseService.Listen("OnFireHurtEvent")
    def onFireHurt(self, data):
        victim = data.get("victim")
        if not victim or victim not in self._burningMultiplier:
            return
        multiplier = self._burningMultiplier[victim]
        if multiplier <= 0.0:
            data["cancel"] = True
            data["cancelIgnite"] = True
            attrComp = compFactory.CreateAttr(victim)
            if attrComp:
                attrComp.SetEntityOnFire(0)
        elif multiplier != 1.0:
            fireTime = data.get("fireTime", 0.0)
            if fireTime > 0.0:
                newFireTime = fireTime * multiplier
                attrComp = compFactory.CreateAttr(victim)
                if attrComp and attrComp.SetEntityOnFire(int(math.ceil(newFireTime))):
                    data["cancelIgnite"] = True

    @BaseService.Listen("ActuallyHurtServerEvent")
    def onActuallyHurt(self, data):
        attacker = data.get("srcId")
        if not attacker:
            return
        damage = data.get("damage", 0.0)
        if damage <= 0.0:
            return
        projectileId = data.get("projectileId")
        cause = data.get("cause")
        isProjectile = bool(projectileId) or cause == getattr(ActorDamageCause, "Projectile", "projectile")
        if isProjectile:
            rateKey = (attacker, PlatinumAttributeType.LIFESTEAL_PROJECTILE)
        else:
            rateKey = (attacker, PlatinumAttributeType.LIFESTEAL_MELEE)
        if rateKey in self._modifierMap and self._modifierMap[rateKey]:
            lifestealRate = max(0.0, self._getCalculatedValue(attacker, rateKey[1]))
            if lifestealRate > 0.0:
                healAmount = damage * lifestealRate
                attrComp = compFactory.CreateAttr(attacker)
                if attrComp:
                    currentHealth = attrComp.GetAttrValue(AttrType.HEALTH)
                    maxHealth = attrComp.GetAttrMaxValue(AttrType.HEALTH)
                    if currentHealth >= 0 and maxHealth > 0 and currentHealth < maxHealth:
                        newHealth = min(maxHealth, currentHealth + healAmount)
                        attrComp.SetAttrValue(AttrType.HEALTH, float(newHealth))

    @BaseService.Listen("ServerPlayerGetExperienceOrbEvent")
    def onServerPlayerGetExperienceOrb(self, data):
        playerId = data.get("playerId")
        if not playerId:
            return
        baseExp = data.get("experienceValue", 0)
        if baseExp <= 0:
            return
        key = (playerId, PlatinumAttributeType.EXP_MULTIPLIER)
        if key in self._modifierMap and self._modifierMap[key]:
            multiplier = max(0.0, self._getCalculatedValue(playerId, PlatinumAttributeType.EXP_MULTIPLIER))
            if abs(multiplier - 1.0) > 1e-6:
                # cancel 取消原版加经验逻辑，改由代码增加倍率后的经验值
                data["cancel"] = True
                finalExp = int(round(baseExp * multiplier))
                if finalExp > 0:
                    expComp = compFactory.CreateExp(playerId)
                    if expComp:
                        expComp.AddPlayerExperience(finalExp)

    @BaseService.Listen("MobDieEvent")
    def onMobDieExp(self, data):
        attacker = data.get("attacker")
        if not attacker:
            return
        deadEntityId = data.get("id")
        if not deadEntityId or deadEntityId in serverApi.GetPlayerList():
            return
        key = (attacker, PlatinumAttributeType.KILL_EXP_MULTIPLIER)
        if key in self._modifierMap and self._modifierMap[key]:
            multiplier = max(1.0, self._getCalculatedValue(attacker, PlatinumAttributeType.KILL_EXP_MULTIPLIER))
            extraMultiplier = multiplier - 1.0
            if extraMultiplier > 1e-6:
                # 读取原版生物经验掉落定义并生成额外经验球
                comp = compFactory.CreateEntityEvent(deadEntityId)
                components = comp.GetComponents() if comp else None
                if not isinstance(components, dict):
                    return
                rewardComp = components.get("minecraft:experience_reward")
                if not isinstance(rewardComp, dict):
                    return
                onDeath = rewardComp.get("on_death")
                if not onDeath:
                    return
                # 使用 EvalMolangExpression 计算经验奖励表达式
                baseReward = 0.0
                if isinstance(onDeath, (int, float)):
                    baseReward = float(onDeath)
                elif isinstance(onDeath, stringTypes):
                    queryComp = compFactory.CreateQueryVariable(deadEntityId)
                    if queryComp:
                        res = queryComp.EvalMolangExpression(str(onDeath))
                        if isinstance(res, dict) and "value" in res and res["value"] is not None:
                            try:
                                baseReward = float(res["value"])
                            except (ValueError, TypeError):
                                baseReward = 0.0
                if baseReward > 0.0:
                    extraExp = int(round(baseReward * extraMultiplier))
                    if extraExp > 0:
                        pos = Entity(deadEntityId).Pos
                        if pos:
                            expComp = compFactory.CreateExp(attacker)
                            if expComp:
                                expComp.CreateExperienceOrb(extraExp, pos)

    @BaseService.Listen("DestroyBlockEvent")
    def onDestroyBlock(self, data):
        if not self.fortuneManager.isRegistered(data.get("fullName", "")):
            return
        playerId = data.get("playerId")
        if not playerId:
            return
        heldFactory = self._getHeldItemFactory(playerId)
        level = self._getFortuneLevel(playerId, heldFactory)
        if self._isBlockDropHandled(playerId, heldFactory, level):
            return
        dropEntityIds = data.get("dropEntityIds")
        if not dropEntityIds:
            return
        multiplier = FortuneManager.rollFortuneMultiplier(level)
        if multiplier <= 1:
            return
        itemComp = compFactory.CreateItem(levelId)
        if not itemComp:
            return
        dimensionId = data.get("dimensionId", 0)
        pos = (data["x"] + 0.5, data["y"] + 0.5, data["z"] + 0.5)
        for itemEntityId in dropEntityIds:
            itemDict = itemComp.GetDroppedItem(itemEntityId, True)
            if not isinstance(itemDict, dict):
                continue
            count = itemDict.get("count", 0)
            if isinstance(count, bool) or not isinstance(count, integerTypes) or count <= 0:
                continue
            extraItemDict = dict(itemDict)
            extraItemDict["count"] = count * (multiplier - 1)
            System.CreateEngineItemEntity(extraItemDict, dimensionId, pos)

    @BaseService.Listen("EntityDieLoottableServerEvent")
    def onMobDieLooting(self, data):
        attacker = data.get("attacker")
        if not attacker or not Entity(attacker).IsPlayer:
            return
        heldFactory = self._getHeldItemFactory(attacker)
        level = self._getIntegerLevel(attacker, PlatinumAttributeType.LOOTING_LEVEL)
        if heldFactory:
            level += heldFactory.getEnchantLevel(EnchantType.WeaponLoot)
        if level <= 0:
            return
        deadEntityId = data.get("dieEntityId")
        if not deadEntityId or deadEntityId in serverApi.GetPlayerList():
            return
        itemList = data.get("itemList")
        if not isinstance(itemList, list):
            return
        extraItems = []
        for itemDict in itemList:
            if not isinstance(itemDict, dict):
                continue
            extraCount = random.randint(0, level)
            if extraCount <= 0:
                continue
            extraItemDict = dict(itemDict)
            extraItemDict["count"] = extraCount
            extraItems.append(extraItemDict)
        if extraItems:
            data["itemList"] = itemList + extraItems
            data["dirty"] = True

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

    @BaseService.Listen("PlayerDieEvent")
    def onPlayerDie(self, data):
        self._invulnerableUntil.pop(data.get("id"), None)

    @BaseService.Listen("MobDieEvent")
    def onMobDie(self, data):
        self._invulnerableUntil.pop(data.get("id"), None)

    def onServiceStop(self):
        BaseService.onServiceStop(self)
        for entityId in list(self._protectionMagicBaseMap.keys()):
            self._restoreProtectionMagicValue(entityId)
        for key in self._modifierMap.keys():
            if key[1] in (
                PlatinumAttributeType.PROTECTION_ALL,
                PlatinumAttributeType.PROTECTION_MAGIC,
            ):
                continue
            self._restore(key)
        self._modifierMap.clear()
        self._baseValueMap.clear()
        self._invulnerableUntil.clear()
        self._burningMultiplier.clear()
        self._protectionMagicBaseMap.clear()

    def clearEntity(self, entityId, restore):
        self._invulnerableUntil.pop(entityId, None)
        self._burningMultiplier.pop(entityId, None)
        if restore and entityId in self._protectionMagicBaseMap:
            self._restoreProtectionMagicValue(entityId)
        keys = [key for key in self._modifierMap if key[0] == entityId]
        for key in keys:
            if restore and key[1] not in (
                PlatinumAttributeType.PROTECTION_ALL,
                PlatinumAttributeType.PROTECTION_MAGIC,
            ):
                self._restore(key)
            self._modifierMap.pop(key, None)
            self._baseValueMap.pop(key, None)
        self._protectionMagicBaseMap.pop(entityId, None)

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

    def _validateModifier(self, entityId, attributeType, modifierArgs):
        if len(modifierArgs) != 4:
            return False
        modifierId, amount, operation, operand = modifierArgs
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

    def _getIntegerLevel(self, entityId, attributeType):
        """等级型修饰符：小数部分截断，负值归零。"""
        return max(0, int(self._getCalculatedValue(entityId, attributeType)))

    def _getHeldItemFactory(self, playerId):
        """获取玩家主手物品的 ItemFactory（含 userData 附魔数据），空手返回 None。"""
        itemComp = compFactory.CreateItem(playerId)
        if not itemComp:
            return None
        itemDict = itemComp.GetPlayerItem(ItemPosType.CARRIED, 0, True)
        return ItemFactory.fromDict(itemDict) if itemDict else None

    def _getProtectionMagicBaseValue(self, entityId):
        if entityId in self._protectionMagicBaseMap:
            return 0.0
        entityComp = compFactory.CreateEntityEvent(entityId)
        components = entityComp.GetComponents() if entityComp else None
        if not isinstance(components, dict):
            return None
        damageSensor = components.get("minecraft:damage_sensor")
        if damageSensor is not None and not isinstance(damageSensor, dict):
            return None
        self._protectionMagicBaseMap[entityId] = damageSensor
        return 0.0

    def _syncProtectionMagicValue(self, entityId):
        allKey = (entityId, PlatinumAttributeType.PROTECTION_ALL)
        magicKey = (entityId, PlatinumAttributeType.PROTECTION_MAGIC)
        hasAllProtection = bool(self._modifierMap.get(allKey))
        hasMagicProtection = bool(self._modifierMap.get(magicKey))
        if not hasAllProtection and not hasMagicProtection:
            return self._restoreProtectionMagicValue(entityId)
        multiplier = 1.0
        if hasAllProtection:
            multiplier *= calculateProtectionMultiplier(
                self._getCalculatedValue(entityId, PlatinumAttributeType.PROTECTION_ALL)
            )
        if hasMagicProtection:
            multiplier *= calculateProtectionMultiplier(
                self._getCalculatedValue(entityId, PlatinumAttributeType.PROTECTION_MAGIC)
            )
        return self._setProtectionMagicMultiplier(entityId, multiplier)

    def _setProtectionMagicMultiplier(self, entityId, multiplier):
        entityComp = compFactory.CreateEntityEvent(entityId)
        if not entityComp or entityId not in self._protectionMagicBaseMap:
            return False
        damageSensor = self._protectionMagicBaseMap[entityId] or {}
        if not isinstance(damageSensor, dict):
            return False
        triggers = damageSensor.get("triggers", [])
        if not isinstance(triggers, list):
            return False
        hasMagicTrigger = False
        targetTriggers = []
        for trigger in triggers:
            if not isinstance(trigger, dict):
                return False
            trigger = dict(trigger)
            if trigger.get("cause") == "magic":
                baseMultiplier = trigger.get("damage_multiplier", 1.0)
                if isinstance(baseMultiplier, bool) or not isinstance(baseMultiplier, integerTypes + (float,)):
                    return False
                trigger["damage_multiplier"] = float(baseMultiplier) * multiplier
                hasMagicTrigger = True
            targetTriggers.append(trigger)
        if not hasMagicTrigger:
            targetTriggers.append({"cause": "magic", "damage_multiplier": multiplier})
        damageSensor = dict(damageSensor)
        damageSensor["triggers"] = targetTriggers
        return bool(entityComp.AddActorComponent("minecraft:damage_sensor", json.dumps(damageSensor)))

    def _restoreProtectionMagicValue(self, entityId):
        if entityId not in self._protectionMagicBaseMap:
            return False
        entityComp = compFactory.CreateEntityEvent(entityId)
        if not entityComp:
            return False
        damageSensor = self._protectionMagicBaseMap[entityId]
        if damageSensor is None:
            success = bool(entityComp.RemoveActorComponent("minecraft:damage_sensor"))
        else:
            success = bool(entityComp.AddActorComponent("minecraft:damage_sensor", json.dumps(damageSensor)))
        if success:
            self._protectionMagicBaseMap.pop(entityId, None)
        return success

    def _getFortuneLevel(self, playerId, heldFactory):
        level = self._getIntegerLevel(playerId, PlatinumAttributeType.FORTUNE_LEVEL)
        return level + (heldFactory.getEnchantLevel(EnchantType.MiningLoot) if heldFactory else 0)

    def _isBlockDropHandled(self, playerId, heldFactory, fortuneLevel):
        """时运接管判定：无总时运等级、创造模式或手持精准采集时交回引擎处理。"""
        if fortuneLevel <= 0:
            return True
        gameComp = compFactory.CreateGame(levelId)
        if gameComp and gameComp.GetPlayerGameType(playerId) == GameType.Creative:
            return True
        if heldFactory and heldFactory.getEnchantLevel(EnchantType.MiningSilkTouch) > 0:
            return True
        return False

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
        if attributeType == PlatinumAttributeType.INVULNERABLE_TIME:
            # 原版无懈可击时间（Damage Immunity / Invulnerability Frames）为 10 游戏刻（0.5 秒）。
            return 0.5
        if attributeType in (
            PlatinumAttributeType.LIFESTEAL_MELEE,
            PlatinumAttributeType.LIFESTEAL_PROJECTILE,
        ):
            return 0.0
        if attributeType in (
            PlatinumAttributeType.FORTUNE_LEVEL,
            PlatinumAttributeType.LOOTING_LEVEL,
        ):
            # 原版无附魔时等级为 0
            return 0.0
        if attributeType in (
            PlatinumAttributeType.PROTECTION_ALL,
            PlatinumAttributeType.PROTECTION_MAGIC,
        ):
            return self._getProtectionMagicBaseValue(entityId)
        if attributeType in PlatinumAttributeType.PROTECTION_DAMAGE_EVENT_TYPES:
            return 0.0
        if attributeType in (
            PlatinumAttributeType.KILL_EXP_MULTIPLIER,
            PlatinumAttributeType.EXP_MULTIPLIER,
            PlatinumAttributeType.BURNING_TIME,
        ):
            return 1.0
        if attributeType == PlatinumAttributeType.ARMOR:
            return self._getEquippedArmorValue(entityId)
        if attributeType == PlatinumAttributeType.MAX_AIR_SUPPLY:
            breathComp = compFactory.CreateBreath(entityId)
            value = breathComp.GetMaxAirSupply() if breathComp else None
            return float(value) if isinstance(value, integerTypes) and value >= 0 else None
        if attributeType == PlatinumAttributeType.RECOVER_TOTAL_AIR_SUPPLY_TIME:
            # 原版恢复全部氧气时间基准为 0.0 秒（即出水立即按恢复率全速回满）
            return 0.0
        return self._getPlayerBaseValue(entityId, attributeType)

    @staticmethod
    def _getPlayerBaseValue(entityId, attributeType):
        playerComp = compFactory.CreatePlayer(entityId)
        if attributeType == PlatinumAttributeType.INTERACT_RANGE:
            value = playerComp.GetPlayerInteracteRange()
            return float(value) if isinstance(value, integerTypes + (float,)) and value > 0 else None
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
        if key[1] in (
            PlatinumAttributeType.PROTECTION_ALL,
            PlatinumAttributeType.PROTECTION_MAGIC,
        ):
            return self._syncProtectionMagicValue(key[0])
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
        if attributeType == PlatinumAttributeType.INVULNERABLE_TIME:
            return value >= 0.0
        if attributeType in (
            PlatinumAttributeType.LIFESTEAL_MELEE,
            PlatinumAttributeType.LIFESTEAL_PROJECTILE,
            PlatinumAttributeType.EXP_MULTIPLIER,
            PlatinumAttributeType.FORTUNE_LEVEL,
            PlatinumAttributeType.LOOTING_LEVEL,
        ):
            return value >= 0.0
        if attributeType in (
            PlatinumAttributeType.PROTECTION_ALL,
            PlatinumAttributeType.PROTECTION_MAGIC,
        ):
            return self._syncProtectionMagicValue(entityId)
        if attributeType in PlatinumAttributeType.PROTECTION_DAMAGE_EVENT_TYPES:
            return True
        if attributeType == PlatinumAttributeType.BURNING_TIME:
            if value < 0.0:
                return False
            if abs(value - 1.0) < 1e-6:
                self._burningMultiplier.pop(entityId, None)
            else:
                self._burningMultiplier[entityId] = float(value)
            return True
        if attributeType == PlatinumAttributeType.KILL_EXP_MULTIPLIER:
            return value >= 1.0
        if attributeType == PlatinumAttributeType.ARMOR:
            # 装备护甲通过 _getBaseValue 参与乘算/加算，SetAttrValue 仅写入额外护甲差值（总护甲 - 装备护甲）。
            extraArmor = int(round(value - baseValue))
            if extraArmor < 0:
                extraArmor = 0
            return compFactory.CreateAttr(entityId).SetAttrValue(AttrType.ARMOR, extraArmor, 0)
        if attributeType == PlatinumAttributeType.MAX_AIR_SUPPLY:
            if value < 0.0:
                return False
            breathComp = compFactory.CreateBreath(entityId)
            return bool(breathComp and breathComp.SetMaxAirSupply(int(round(value))))
        if attributeType == PlatinumAttributeType.RECOVER_TOTAL_AIR_SUPPLY_TIME:
            if value < 0.0:
                return False
            breathComp = compFactory.CreateBreath(entityId)
            return bool(breathComp and breathComp.SetRecoverTotalAirSupplyTime(float(value)))
        return self._setPlayerValue(entityId, attributeType, value)

    @staticmethod
    def _setPlayerValue(entityId, attributeType, value):
        playerComp = compFactory.CreatePlayer(entityId)
        if attributeType == PlatinumAttributeType.INTERACT_RANGE:
            if value <= 0.0:
                return False
            success = bool(playerComp.SetPlayerInteracteRange(float(value)))
            if success:
                BaseService().syncRequest(
                    entityId,
                    "client/attribute/syncPickRange",
                    QRequests.Args({"playerId": entityId, "pickRange": float(value)}),
                )
            return success
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
        if key[1] in (
            PlatinumAttributeType.PROTECTION_ALL,
            PlatinumAttributeType.PROTECTION_MAGIC,
        ):
            allKey = (key[0], PlatinumAttributeType.PROTECTION_ALL)
            magicKey = (key[0], PlatinumAttributeType.PROTECTION_MAGIC)
            if not self._modifierMap.get(allKey) and not self._modifierMap.get(magicKey):
                self._protectionMagicBaseMap.pop(key[0], None)
