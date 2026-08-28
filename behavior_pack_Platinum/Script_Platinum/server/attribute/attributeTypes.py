# coding=utf-8
from mod.server import extraServerApi as serverApi

AttrType = serverApi.GetMinecraftEnum().AttrType


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
    PROTECTION_ALL = "protection_all"  # 全类型减伤，与其他分类保护叠乘
    PROTECTION_ENTITY_ATTACK = "protection_entity_attack"  # 实体近战攻击
    PROTECTION_PROJECTILE = "protection_projectile"  # 箭/三叉戟等投射物
    PROTECTION_FALL = "protection_fall"  # 摔落/鞘翅飞行撞墙
    PROTECTION_FIRE = "protection_fire"  # 火焰系：站立火/着火/岩浆/岩浆块/营火/灵魂营火
    PROTECTION_EXPLOSION = "protection_explosion"  # 爆炸系：方块爆炸/实体爆炸/烟花火箭
    PROTECTION_LIGHTNING = "protection_lightning"  # 雷击
    PROTECTION_VOID = "protection_void"  # 虚空
    PROTECTION_ENVIRONMENT = "protection_environment"  # 环境杂项：窒息/溺水/细雪/铁砧/钟乳石等其余来源
    PROTECTION_MAGIC = "protection_magic"  # 魔法伤害（药水/瞬间伤害等）

    # ponytail: 未列出的伤害来源（窒息/溺水/铁砧等）统一走 PROTECTION_ENVIRONMENT 兜底；
    # 需要单独拆分某来源时再在此加一行映射。
    PROTECTION_CAUSE_ATTRIBUTE_MAP = {
        "entity_attack": PROTECTION_ENTITY_ATTACK,
        "projectile": PROTECTION_PROJECTILE,
        "fall": PROTECTION_FALL,
        "fly_into_wall": PROTECTION_FALL,
        "fire": PROTECTION_FIRE,
        "fire_tick": PROTECTION_FIRE,
        "lava": PROTECTION_FIRE,
        "magma": PROTECTION_FIRE,
        "campfire": PROTECTION_FIRE,
        "soul_campfire": PROTECTION_FIRE,
        "block_explosion": PROTECTION_EXPLOSION,
        "entity_explosion": PROTECTION_EXPLOSION,
        "fireworks": PROTECTION_EXPLOSION,
        "lightning": PROTECTION_LIGHTNING,
        "void": PROTECTION_VOID,
    }
    PROTECTION_DAMAGE_EVENT_TYPES = tuple(
        set(PROTECTION_CAUSE_ATTRIBUTE_MAP.values()) | {PROTECTION_ENVIRONMENT}
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
