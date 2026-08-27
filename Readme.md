## Platinum 铂(饰品栏) 组件使用指南

> 📋 **如果你是从旧版本(Platinum)迁移，请先阅读 [新版本注意事项与迁移指南](MIGRATION.md)**

### 一、简介

本组件旨在编写一个利于联动的饰品栏模组。方便上手，开箱即用是本组件的创作宗旨。开发者无需关注组件内部的工作逻辑，只需要向指定服务端发送事件即可注册饰品，监听指定事件便可获取玩家穿脱饰品情况。

### 二、UI展示



<center><img src="https://raw.githubusercontent.com/BitterLemonn/BlogPicBed/master/otherPic/20250121151025698.png" style="zoom:65%;"></center>

<center><img src="https://raw.githubusercontent.com/BitterLemonn/BlogPicBed/master/otherPic/20250121151113113.png" style="zoom:65%;"></center>

<center><img src="https://raw.githubusercontent.com/BitterLemonn/BlogPicBed/master/otherPic/20250121151517324.png" style="zoom:55%"></center>

### 三、基础配置文件介绍

[配置文件](behavior_pack_Platinum/Script_Platinum/commonConfig.py)内存储了所有使用到的变量以及常量，理论上开发者只需要了解其中的变量的作用即可轻松使用本组件。

其中定义了组件所使用到的事件名称以及所使用到的SystemName和NameSpace。

### 四、饰品定义的限制

**由于组件实现方式的特殊，饰品有以下限制：**

- 饰品的**最大堆叠数量**只能为1，否则会导致饰品注册失败

- 当饰品物品被定义为盔甲或食物时不能通过直接交互（右键，长按屏幕）直接穿戴饰品，请开发者避免出现此类情况(除非刻意为之)

### 五、使用方法

#### 1. 饰品注册

**开发者不能将本组件作为内容导入(可能会引发模组冲突)**，本组件会同时发布在网易资源市场当中，只需要玩家同时装载即可正常使用组件。

推荐监听铂服务端广播的 `PlatinumSystemInitFinished` 事件，并在回调中完成饰品注册。该事件触发时，铂的注册系统已经初始化完成：

```py
# coding=utf-8
# 推荐将commonConfig.py中的常量复制到开发项目当中,方便使用
import mod.server.extraServerApi as serverApi

PLATINUM_NAMESPACE = "platinum"
PLATINUM_BROADCAST_SERVER = "broadcasterServer"
PLATINUM_SYSTEM_INIT_FINISHED_EVENT = "PlatinumSystemInitFinished"

# 在开发项目的服务端System中监听铂系统初始化完成事件
class BaubleRegister(serverApi.GetServerSystemCls()):
    def __init__(self, namespace, name):
        super(BaubleRegister, self).__init__(namespace, name)
        self.listenEvent()

    def listenEvent(self):
        self.ListenForEvent(
            PLATINUM_NAMESPACE,
            PLATINUM_BROADCAST_SERVER,
            PLATINUM_SYSTEM_INIT_FINISHED_EVENT,
            self,
            self.onPlatinumSystemInitFinished,
        )

    def onPlatinumSystemInitFinished(self, data):
        self._registerBauble()

    def _registerBauble(self):
        # 项目文件中获取一个与组件通信的服务端
        registerSys = serverApi.GetSystem(PLATINUM_NAMESPACE, PLATINUM_BROADCAST_SERVER)
        # 需要注册的饰品信息Dict
        baubleInfoDict = {
            "baubleName": "命名空间:物品名称",
            # 旧commonConfig.py中的常量将会自动转化为新版本的槽位类型
            # 此处应传入已注册的槽位类型(slotType), 如"helmet"、"belt"等, 具体槽位类型请查看 八、数据说明
            "baubleSlot": "已注册的槽位类型",
            # 此处可以填入一个列表，将饰品注册到多个槽位类型
            # "baubleSlot": ["槽位类型1", "槽位类型2"],
            # 可选 自定义信息提示 在此处设置自定义提示将会覆盖物品Json定义文件中的customTips
            "customTips": "自定义信息提示"
        }
        # 调用注册函数
        registerSys.BaubleRegister(baubleInfoDict)
```

如果项目仍使用引擎事件 `LoadServerAddonScriptsAfter`，必须在事件回调中延迟一帧再注册。该事件触发时，铂的注册系统可能尚未完成初始化，不能直接调用 `BaubleRegister`。保留上例的 `_registerBauble` 方法，仅将 `listenEvent` 和回调替换为：

```py
    def listenEvent(self):
        self.ListenForEvent(
            serverApi.GetEngineNamespace(),
            serverApi.GetEngineSystemName(),
            "LoadServerAddonScriptsAfter",
            self,
            self.onLoadServerAddonScriptsAfter,
        )

    def onLoadServerAddonScriptsAfter(self, data):
        # AddTimer(0, ...) 将注册延迟到下一帧执行
        gameComp = serverApi.GetEngineCompFactory().CreateGame(serverApi.GetLevelId())
        gameComp.AddTimer(0, self._registerBauble)
```

如果需要注册一个自定义槽位的饰品，需要在注册槽位之后再注册饰品，注册槽位方法请查看 **(五.2.槽位注册)**

#### 2.槽位注册

通过**服务端**发送事件注册饰品栏位，开发者可以自定义饰品栏位的数量以及类型。代码如下：

```python
# coding=utf-8
# ===========仅服务端可用=============

# 项目文件中获取一个与组件通信的服务端
# 如导入了commonConfig.py中的常量可将nameSpace和systemName分别改为commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER
registerSys = serverApi.GetSystem("platinum", "broadcasterServer")

# 为所有玩家注册全局饰品栏位(注册后所有玩家默认拥有该槽位)
# 当注册一个新的槽位类型时，须完整传入槽位贴图路径以及槽位名称
registerSys.AddGlobalBaubleSlot(
    "test_helmet",  # 槽位id slotId
    "test_helmet",  # 槽位类型 slotType
    "测试头盔",  # 槽位名称 slotName (为已有槽位类型添加新槽位时可省略)
    "textures/ui/bauble_helmet_slot",  # 槽位贴图路径 (为已有槽位类型添加新槽位时可省略)
)

# ⚠️注意: 新版本中AddGlobalBaubleSlot的isDefault参数已废弃, 通过此方法注册的槽位默认即为全局槽位
# 旧版本中传入isDefault=True的方式仍然兼容, 但不再生效

# 为特定玩家注册饰品栏位
# 方式一: 传入已注册的槽位id(推荐), 此方式会自动从槽位注册表中获取槽位信息
registerSys.AddTargetBaubleSlot(
    "playerId",  # 玩家id
    "test_helmet",  # 槽位id slotId
    "helmet" # 槽位类型 slotType
)
# 方式二: 直接传入完整的槽位信息
registerSys.AddTargetBaubleSlot(
    "playerId",  # 玩家id
    "test_helmet",  # 槽位id slotId
    "test_helmet",  # 槽位类型 slotType
    "测试头盔",  # 槽位名称 slotName (为已有槽位类型添加新槽位时可省略)
    "textures/ui/bauble_helmet_slot"  # 槽位贴图路径 (为已有槽位类型添加新槽位时可省略)
)
```

当注册一个新的槽位类型的槽位时，须完整传入槽位的贴图路径以及槽位名称，当仅需为已存在的槽位类型添加一个新的槽位时，可以省略槽位贴图路径、槽位名称。

#### 3. 槽位删除

通过**服务端**发送事件删除饰品栏位。代码如下：

```python
# coding=utf-8
# ===========仅服务端可用=============
# 项目文件中获取一个与组件通信的服务端
# 如导入了commonConfig.py中的常量可将nameSpace和systemName分别改为commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER
registerSys = serverApi.GetSystem("platinum", "broadcasterServer")

# 删除特定玩家的指定饰品栏位
registerSys.DeleteTargetBaubleSlot("playerId", "test_helmet")
```

**值得注意的是：**

- **默认槽位不可删除**（组件内置的默认槽位无法通过API删除）
- **`DeleteGlobalBaubleSlot`方法在新版本中已不支持**，调用时仅会输出错误日志，不会执行删除操作。如需删除槽位，请使用`DeleteTargetBaubleSlot`对特定玩家进行删除

#### 4.获取全局/特定玩家槽位信息

通过获取服务端组件可以获取全局/特定玩家已注册的槽位信息。这些方法会**直接返回数据**，同时也会通过广播事件发送数据（兼容旧版本）。代码如下：

```python
# coding=utf-8
# 项目文件中获取一个与组件通信的服务端
# 如导入了commonConfig.py中的常量可将nameSpace和systemName分别改为commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER
registerSys = serverApi.GetSystem("platinum", "broadcasterServer")

# 获取全局槽位信息(直接返回数据)
globalSlotInfo = registerSys.GetGlobalBaubleSlotInfo()

# 获取特定玩家槽位信息(直接返回数据)
targetSlotInfo = registerSys.GetTargetBaubleSlotInfo("playerId")

# -------------------------------
# ⚠️注意: 新版本中上述方法会直接返回数据, 无需再通过监听事件获取
# 但仍可通过监听以下事件获取(兼容旧版本):
# 监听全局槽位信息返回事件
self.ListenForEvent(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER,
                    commonConfig.BAUBLE_GET_GLOBAL_INFO_EVENT, self, self.onGetGlobalBaubleSlotInfo)
# 监听特定玩家槽位信息返回事件
self.ListenForEvent(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER,
                    commonConfig.BAUBLE_GET_TARGET_INFO_EVENT, self, self.onGetTargetBaubleSlotInfo)
# 返回值数据结构请查看 八、数据说明
```

#### 5.监听玩家饰品穿脱事件

通过注册监听事件，开发者可以监听到玩家穿脱饰品，可以在对应的回调函数中做出相应的逻辑处理。注册监听代码如下：

```python
# coding=utf-8
# commonConfig为组件配置文件
# 服务端监听事件
# 监听饰品装备事件
self.ListenForEvent(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER,
                    commonConfig.BAUBLE_EQUIPPED_EVENT, self, self.onBaubleEquipped)
# 监听饰品卸下事件
self.ListenForEvent(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER,
                    commonConfig.BAUBLE_UNEQUIPPED_EVENT, self, self.onBaubleUnequipped)
# ---------------------
# 客户端监听事件
# 监听饰品装备事件
self.ListenForEvent(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_CLIENT,
                    commonConfig.BAUBLE_EQUIPPED_EVENT, self, self.onBaubleEquipped)
# 监听饰品卸下事件
self.ListenForEvent(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_CLIENT,
                    commonConfig.BAUBLE_UNEQUIPPED_EVENT, self, self.onBaubleUnequipped)
```

接收到的data信息请查看 **八、数据说明**

#### 6.获取玩家饰品数据

通过获取服务端组件可以获取特定玩家饰品数据。该方法会**直接返回数据**，同时也会通过广播事件发送数据（兼容旧版本）。代码如下：

```python
# coding=utf-8
# 获取饰品数据
# 项目文件中获取一个与组件通信的服务端
# 如导入了commonConfig.py中的常量可将nameSpace和systemName分别改为commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER
registerSys = serverApi.GetSystem("platinum", "broadcasterServer")

# 新版本中直接返回玩家饰品信息dict
baubleInfo = registerSys.GetPlayerBaubleInfo("playerId")  # 传入参数为playerId

# -------------------------------
# ⚠️注意: 新版本中GetPlayerBaubleInfo会直接返回数据, 无需再通过监听事件获取
# 但仍可通过监听以下事件获取(兼容旧版本):
self.ListenForEvent(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER,
                    commonConfig.BAUBLE_GET_INFO_EVENT, self, self.onBaubleGetInfo)

# 事件回调
def onBaubleGetInfo(data):
    playerId = data["playerId"]
    baubleDict = data["baubleDict"]
```

获取到的baubleDict数据详情请查看 **八、数据说明**

**值得注意的是，获取玩家饰品信息需在客户端事件OnLocalPlayerStopLoading发生之后进行请求，否则会导致获取信息不正确**

#### 7. 设置玩家饰品信息

通过获取服务端组件调用指定的接口可以对特定玩家的全部饰品信息或特定槽位的饰品信息进行更改，示例代码如下:

```python
# coding=utf-8
# 设置饰品数据
# 项目文件中获取一个与组件通信的服务端
# 如导入了commonConfig.py中的常量可将nameSpace和systemName分别改为commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER
registerSys = serverApi.GetSystem("platinum", "broadcasterServer")
# 修改全部饰品数据
registerSys.SetPlayerBaubleInfo("playerId", {})  # 这里填入playerId以及baubleDict baubleDict的格式请查看 八、数据说明
# 修改特定槽位饰品数据
registerSys.SetPlayerBaubleInfoWithSlot("playerId", {}, "slotId")  # 这里填入playerId以及itemDict以及slotId(即槽位id) 具体槽位id请查看 八、数据说明
```

**需要注意的是，设置玩家饰品操作需在客户端事件OnLocalPlayerStopLoading之后进行设置，否则会被客户端本地数据覆盖**

#### 8. 设置玩家饰品耐久度

通过获取服务端组件调用指定的接口可以对特定玩家的特定槽位的饰品耐久度进行更改，示例代码如下:

```python
# coding=utf-8
# 设置饰品耐久度
# 项目文件中获取一个与组件通信的服务端
# 如导入了commonConfig.py中的常量可将nameSpace和systemName分别改为commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER
registerSys = serverApi.GetSystem("platinum", "broadcasterServer")
# 修改特定槽位饰品耐久度
registerSys.DecreaseBaubleDurability("playerId", "slotId", 1)
# 这里填入playerId以及slotId(具体slotId请查看 八、数据说明)以及需要减少的耐久度(默认为1)
```

**需要注意的是，设置玩家饰品操作需在客户端事件OnLocalPlayerStopLoading之后进行设置，否则会被客户端本地数据覆盖**

**⚠️注意: 当饰品耐久度降为0或更低时，饰品会自动从槽位中移除并触发饰品卸下事件**

#### 9. 非玩家生物穿戴饰品及掉落

非玩家生物没有饰品栏界面，通过服务端接口穿戴、卸下和查询饰品，支持设置饰品掉落几率（默认为 1.0 即 100%）：

```python
# coding=utf-8
import mod.server.extraServerApi as serverApi

registerSys = serverApi.GetSystem("platinum", "broadcasterServer")

# 穿戴指定槽位并设置掉落几率（dropProbability 默认为 1.0，即 100% 掉落；0.0 为不掉落）。
registerSys.SetEntityBaubleInfoWithSlot(entityId, itemDict, "slotId", dropProbability=1.0)

# 卸下指定槽位。
registerSys.SetEntityBaubleInfoWithSlot(entityId, None, "slotId")

# 批量设置饰品（支持 dropProbability 传入 float 或 dict 指定各槽位概率）、查询、减少耐久度。
registerSys.SetEntityBaubleInfo(entityId, {"slotId": itemDict}, dropProbability=1.0)
entityBaubleInfo = registerSys.GetEntityBaubleInfo(entityId)
registerSys.DecreaseEntityBaubleDurability(entityId, "slotId", 1)
```

非玩家生物使用独立服务端穿脱事件：`EntityBaubleEquipped` 和 `EntityBaubleUnequipped`，事件参数使用 `entityId`。非玩家饰品不会同步饰品栏 UI，也不会写入世界存档；实体触发 `EntityRemoveEvent` 时自动卸下并清理。

##### 生物死亡掉落事件与拦截注意

当非玩家生物死亡（引擎触发 `MobDieEvent`）时，组件会根据各槽位设定的掉落概率计算出掉落物品列表，并广播服务端自定义事件 `EntityBaubleDrop`（常量 `commonConfig.ENTITY_BAUBLE_DROP_EVENT`），并在**下一帧**生成掉落物实体。

`EntityBaubleDrop` 事件参数格式：
```python
{
    "entityId": str,      # 死亡生物实体ID
    "itemList": list,     # 本次计算掉落的物品dict列表，开发者可就地修改增删
    "cancel": bool        # 是否取消掉落，开发者在监听回调中将 data["cancel"] = True 即可拦截掉落
}
```

监听示例：
```python
self.ListenForEvent("platinum", "broadcasterServer", "EntityBaubleDrop", self, self.onEntityBaubleDrop)

def onEntityBaubleDrop(self, data):
    entityId = data["entityId"]
    itemList = data["itemList"]
    # 可在此处修改 itemList 或设置 data["cancel"] = True 取消掉落
```

**⚠️重要注意: 若你的模组拦截了生物死亡逻辑（如用于制作尸体、自定义死亡倒地动画等未触发原生引擎 MobDieEvent 的情况），需要开发者自行模拟原生引擎向服务端发送一次 MobDieEvent 事件（参数至少包含 `{"id": entityId}`），以确保饰品掉落事件能够正常计算与触发。**

模拟发送事件示例：
```python
# coding=utf-8
import mod.server.extraServerApi as serverApi

# 在你拦截死亡的自定义逻辑处（如生物血量归零进入假死/倒地阶段）：
engineSystem = serverApi.GetSystem(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName())
engineSystem.BroadcastEvent("MobDieEvent", {"id": entityId})
```

#### 10. 特殊属性修饰符

组件为飞行能力、台阶高度、盔甲值、饥饿值和自然回血提供服务端修饰符接口。接口允许玩家或非玩家实体使用，参数和操作枚举与网易引擎属性修饰符保持一致：

```python
# coding=utf-8
import mod.server.extraServerApi as serverApi

modifierSystem = serverApi.GetSystem("platinum", "broadcasterServer")

modifierSystem.AddModifier(
    entityId,
    modifierSystem.AttrType.STEP_HEIGHT,
    "example:step_height",
    0.5,
    modifierSystem.AttributeModifierOperation.OperationAddition,
    modifierSystem.AttributeOperands.OperandCurrent,
)

# 更新、查询和移除使用相同的 entityId、属性类型与 modifierId。
modifierSystem.UpdateModifier(
    entityId,
    modifierSystem.AttrType.STEP_HEIGHT,
    "example:step_height",
    1.0,
    modifierSystem.AttributeModifierOperation.OperationAddition,
    modifierSystem.AttributeOperands.OperandCurrent,
)
modifierSystem.HasModifier(
    entityId, modifierSystem.AttrType.STEP_HEIGHT, "example:step_height"
)
modifierSystem.GetAllModifiers(entityId, modifierSystem.AttrType.STEP_HEIGHT)
modifierSystem.RemoveModifier(
    entityId, modifierSystem.AttrType.STEP_HEIGHT, "example:step_height"
)
```

支持的属性类型：

- `modifierSystem.AttrType.FLYING_ABILITY`：计算结果大于 `0` 时允许飞行（仅玩家生效）。
- `modifierSystem.AttrType.STEP_HEIGHT`：无需跳跃最大跨越高度，计算结果必须大于 `0`（仅玩家生效）。
- `modifierSystem.AttrType.GRAVITY`：实体重力因子（负数，表示每帧向下的速度；为 `0` 时取世界重力因子，默认 `-0.08`）。
- `modifierSystem.AttrType.SCALE`：实体模型放缩比例（基准值 `1.0`，结果必须大于 `0`）。
- `modifierSystem.AttrType.ATTACK_SPEED_AMPLIFIER`：玩家攻击速度倍率（仅玩家生效，基准值 `1.0`，有效范围 `[0.5, 2.0]`，`0.8` 表示提速 20%）。
- `modifierSystem.AttrType.PICKUP_AREA_HORIZONTAL`：玩家水平方向拾取物品增加距离（仅玩家生效，基准值 `0.0`，对应 X/Z 轴额外范围，结果不能为负数）。
- `modifierSystem.AttrType.PICKUP_AREA_VERTICAL`：玩家纵向/垂直方向拾取物品增加距离（仅玩家生效，基准值 `0.0`，对应 Y 轴额外范围，结果不能为负数）。
- `modifierSystem.AttrType.INVULNERABLE_TIME`（别名 `INVULNERABILITY_TIME`）：实体受击后获得的无敌保护时长（单位：秒，基准值 `0.5` 即原版 10 游戏刻，结果不能为负数；生效期内免疫后续伤害与击退，虚空/自杀/override除外）。
- `modifierSystem.AttrType.LIFESTEAL_MELEE`：近战攻击吸血比例（基准值 `0.0`，即 0%；如 `0.2` 表示近战造成伤害后为攻击者恢复实际造成伤害 20% 的生命值，不超过生命上限）。
- `modifierSystem.AttrType.LIFESTEAL_PROJECTILE`：投射物/远程攻击吸血比例（基准值 `0.0`，即 0%；如 `0.15` 表示远程造成伤害后为攻击者恢复实际造成伤害 15% 的生命值，不超过生命上限）。
- `modifierSystem.AttrType.KILL_EXP_MULTIPLIER`：击杀生物经验倍率（基准值 `1.0`，结果必须大于等于 `1.0`；通过额外掉落经验球实现，如 `1.5` 表示额外掉落相当于原版经验 50% 的经验球）。
- `modifierSystem.AttrType.EXP_MULTIPLIER`：拾取经验球倍率（仅玩家生效，基准值 `1.0`，结果不能为负数；如 `2.0` 表示拾取经验球时最终获得 2 倍经验，不影响其他方式直接增加的经验）。
- `modifierSystem.AttrType.INTERACT_RANGE`（别名 `PICK_RANGE`）：玩家交互范围/触及距离（单位：格，仅玩家生效，结果必须大于 `0`；服务端修改 `SetPlayerInteracteRange` 并自动向客户端同步更新 `SetPickRange`）。
- `modifierSystem.AttrType.BURNING_TIME`（别名 `BURN_TIME`）：实体受到点燃/火焰伤害时的燃烧时间倍率（基准值 `1.0`，结果不能为负数；为 `0.0` 时免疫火焰伤害与点燃效果，小于 `1.0` 时按比例缩短着火持续时间）。
- `modifierSystem.AttrType.ARMOR`：复用网易 `AttrType.ARMOR`，将实体当前身上穿戴装备的总护甲作为基数（baseValue）参与加算与乘算修饰，计算出的总护甲与装备护甲的差值作为额外护甲写入引擎；玩家换装时自动重新计算。
- `modifierSystem.AttrType.MAX_AIR_SUPPLY`（别名 `MAX_OXYGEN`）：实体最大氧气储备值（单位：游戏刻，原版基准值通常为 `300` 刻即 15 秒，结果不能为负数）。
- `modifierSystem.AttrType.RECOVER_TOTAL_AIR_SUPPLY_TIME`：实体恢复最大氧气量所需时间（单位：秒，基准值 `0.0` 秒，结果不能为负数）。
- `modifierSystem.AttrType.MAX_EXHAUSTION`：玩家最大消耗度（`foodExhaustionLevel` 归零阈值，默认 `4.0`，仅玩家生效），结果必须大于 `0`。
- `modifierSystem.AttrType.EXHAUSTION_RATIO_GLOBAL`：全局饥饿消耗倍率（仅玩家生效），结果必须大于等于 `0`。
- `modifierSystem.AttrType.EXHAUSTION_RATIO_HEAL`：自然回血饥饿消耗倍率（仅玩家生效），结果必须大于等于 `0`。
- `modifierSystem.AttrType.EXHAUSTION_RATIO_JUMP`：跳跃饥饿消耗倍率（仅玩家生效），结果必须大于等于 `0`。
- `modifierSystem.AttrType.EXHAUSTION_RATIO_SPRINT_JUMP`：疾跑跳跃饥饿消耗倍率（仅玩家生效），结果必须大于等于 `0`。
- `modifierSystem.AttrType.EXHAUSTION_RATIO_MINE`：挖掘方块饥饿消耗倍率（仅玩家生效），结果必须大于等于 `0`。
- `modifierSystem.AttrType.EXHAUSTION_RATIO_ATTACK`：攻击饥饿消耗倍率（仅玩家生效），结果必须大于等于 `0`。
- `modifierSystem.AttrType.FORTUNE_LEVEL`（别名 `FORTUNE`）：时运等级（基准值 `0`，小数截断，结果不能为负数）。玩家带时运等级破坏已注册方块时取消引擎掉落，改用引擎模拟挖掘接口（`SpawnResources` 的 `bonusLootLevel`）按原版掉落表带时运等级重新生成掉落。仅对通过时运管理器注册的方块生效；创造模式或手持精准采集时交回引擎处理。管理器默认预注册原版吃时运的矿石（煤/钻石/绿宝石/青金石/红石/铜矿石及深板岩变种、下界金矿/石英矿；铁矿与主世界金矿掉落本体不吃时运，不在默认表内）。扩展注册方式（只注册方块名，掉落物由引擎掉落表决定）：
  ```python
  from Script_Platinum.server.attribute.attributeModifier import PlatinumAttributeModifierService

  manager = PlatinumAttributeModifierService.access().fortuneManager
  manager.registerBlock("custom:ore_block")
  manager.unregisterBlock("minecraft:diamond_ore")
  ```
- `modifierSystem.AttrType.LOOTING_LEVEL`（别名 `LOOTING`）：抢夺等级（仅玩家击杀者生效，基准值 `0`，小数截断，结果不能为负数）。击杀生物时按原版抢夺算法对生物掉落表模拟出的每种物品额外掉落 `0~等级` 个（抢夺 III 即等级 `3` 时每种额外 0~3 个）。不影响引擎自身掉落，与武器抢夺附魔效果叠加。
- `modifierSystem.AttrType.NATURAL_REGEN`：计算结果大于 `0` 时开启自然回血（仅玩家生效）。
- `modifierSystem.AttrType.NATURAL_REGEN_LEVEL`：自然回血饥饿值阈值（仅玩家生效），结果必须为非负整数，且不能低于当前饥饿掉血阈值。
- `modifierSystem.AttrType.NATURAL_REGEN_TICK`：每次自然回血的间隔（仅玩家生效），单位为游戏刻，结果必须为大于等于 `1` 的整数。
- `modifierSystem.AttrType.NATURAL_STARVE`：计算结果大于 `0` 时开启饥饿掉血（仅玩家生效）。
- `modifierSystem.AttrType.STARVE_LEVEL`：饥饿掉血阈值（仅玩家生效），结果必须为非负整数，且不能高于当前自然回血阈值。
- `modifierSystem.AttrType.STARVE_TICK`：每次饥饿掉血的间隔（仅玩家生效），单位为游戏刻，结果必须为大于等于 `1` 的整数。

特殊属性修饰符统一仅支持 `OperandCurrent`。自定义属性修饰符按 `OperationAddition`、`OperationMultiplyBase`、`OperationMultiplyTotal`、`OperationCap` 顺序计算。`AddModifier` 遇到重复 `modifierId` 返回 `False`，已有修饰符必须使用 `UpdateModifier`。修饰符只保存在当前服务端运行期；实体或玩家数据加载、饰品恢复时应重新添加。自定义属性存在修饰符期间，不要绕过本接口直接修改同一属性。

**⚠️注意: 使用特殊属性修饰符进行的属性不存盘，所有修饰的属性将会在系统关闭、玩家退出或实体移除后自动清理，建议在穿脱饰品事件中使用保持正常的生命周期**

### 六、示例代码

组件内还内置了一个腰带饰品【旅行者腰带】，[服务端代码](behavior_pack_Platinum/Script_Platinum/server/inner/baubleServer.py)中详细的说明了如何进行饰品穿脱的监听以及对应功能的实现。实现了一个可以提升玩家跨越高度的饰品。

**⚠️注意: 与旧版本不同，示例代码已整合为单一的服务端文件，不再提供单独的客户端示例文件。饰品穿脱事件的监听仅需在服务端进行即可，客户端的穿脱广播由组件内部自动完成。**

示例代码关键部分说明：

```python
# 监听饰品穿脱事件仅需在服务端进行
self.ListenForEvent(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER,
                    commonConfig.BAUBLE_EQUIPPED_EVENT, self, self.onBaubleEquipped)
self.ListenForEvent(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER,
                    commonConfig.BAUBLE_UNEQUIPPED_EVENT, self, self.onBaubleUnequipped)

# 在回调中通过判断饰品名称来执行对应的逻辑
def onBaubleEquipped(self, data):
    playerId = data["playerId"]
    bauble = data["itemDict"]
    slotId = data["baubleSlotId"]  # 新版本使用baubleSlotId获取槽位id
    if bauble["newItemName"] == "lemon_platinum:traveler_belt":
        # 执行饰品装备逻辑
        pass
```

### 七、后续开发

因为本组件旨在完成一个便于联动的饰品栏模组，有任何的接口需求也可以联系我
QQ：873811906，或加入开发者交流群：575858232，尽量满足各位开发者大大的需求。但是本人也只是一个组件小白，所以需求不一定能够满足，感谢各位大佬的指点以及使用~

### 八、数据说明

#### 1. 默认饰品槽位id列表

默认注册的新版槽位id列表(slotId/slotName)对应关系如下：

| 槽位      | v1槽位ID(slotId)  | v1槽位类型(slotType) | v1槽位名称(slotName) |
|---------|-----------------|------------------|------------------|
| 头盔      | bauble_helmet   | helmet           | 头盔               |
| 项链      | bauble_necklace | necklace         | 项链               |
| 背饰      | bauble_back     | back             | 背饰               |
| 胸饰      | bauble_armor    | armor            | 胸饰               |
| 手环(槽位1) | bauble_hand0    | hand             | 手环               |
| 手环(槽位2) | bauble_hand1    | hand             | 手环               |
| 腰带      | bauble_belt     | belt             | 腰带               |
| 鞋子      | bauble_shoes    | shoes            | 鞋子               |
| 护符(槽位1) | bauble_other0   | other            | 护符               |
| 护符(槽位2) | bauble_other1   | other            | 护符               |
| 护符(槽位3) | bauble_other2   | other            | 护符               |
| 护符(槽位4) | bauble_other3   | other            | 护符               |

#### 2. 旧版本饰品常量与新版本slotType对应关系

| commonConfig.py常量   | 新版v1 slotType |
|---------------------|---------------|
| BaubleEnum.HELMET   | helmet        |
| BaubleEnum.NECKLACE | necklace      |
| BaubleEnum.BACK     | back          |
| BaubleEnum.ARMOR    | armor         |
| BaubleEnum.HAND     | hand          |
| BaubleEnum.BELT     | belt          |
| BaubleEnum.SHOES    | shoes         |
| BaubleEnum.OTHER    | other         |

#### 3. 旧版本slotName与新版本slotId对应关系

| 旧版slotName | 新版v1 slotId     |
|------------|-----------------|
| helmet     | bauble_helmet   |
| necklace   | bauble_necklace |
| back       | bauble_back     |
| armor      | bauble_armor    |
| hand_1     | bauble_hand0    |
| hand_2     | bauble_hand1    |
| belt       | bauble_belt     |
| shoes      | bauble_shoes    |
| other_1    | bauble_other0   |
| other_2    | bauble_other1   |
| other_3    | bauble_other2   |
| other_4    | bauble_other3   |

#### 3. 饰品穿脱事件返回值

使用BaubleEquippedEvent和BaubleUnequippedEvent接口获取玩家饰品穿脱事件返回值

BaubleEquippedEvent和BaubleUnequippedEvent返回值结构如下:

```python
# coding=utf-8
data = {
    "slotIndex": int,  # 槽位索引(仅当槽位类型中存在多个槽位时>0否则为0)
    "playerId": str,  # 玩家id
    "isFirstLoad": bool,  # 是否为加入游戏自动穿戴
    "baubleSlot": str,  # 槽位类型(值为commonConfig.py的常量, 新版添加的槽位值与baubleSlotId一致)
    "baubleSlotId": str,  # 槽位id
    "itemDict": dict  # 饰品信息
}
```

#### 4. 饰品信息返回值

使用GetPlayerBaubleInfo接口获取玩家饰品信息返回值

BaubleDict结构如下:

```python
# coding=utf-8
baubleDict = {
    "playerId": "playerId",
    "baubleDict": {
        "槽位id": itemDict,
        # ......
    }
}
```

#### 5. 饰品栏信息返回值

使用GetGlobalBaubleSlotInfo和GetTargetBaubleSlotInfo接口获取已注册饰品栏信息返回值

BaubleSlotInfo结构如下:

```python
# coding=utf-8
baubleSlotInfo = {
    "playerId": "playerId",  # 仅在GetTargetBaubleSlotInfo中存在
    "baubleSlotList": [
        {
            "槽位id": {
                "slotId": "槽位id",
                "slotType": "槽位类型",
                "slotName": "槽位名称",
                "isDefault": bool
            }
        }
        # ......
    ]
}
```

### 九、许可证

在遵循最终用户许可协议([EULA](EULA.txt))
的前提下，本组件遵循[MIT](LICENSE)开源协议，请开发者们随意使用。
