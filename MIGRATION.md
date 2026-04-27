# Platinum 新版本注意事项与迁移指南

> 本文档适用于从旧版本 Platinum 组件迁移到新版本（reborn）的开发者。如果你是新用户，请直接阅读 [Readme.md](Readme.md)。

---

## 一、新版本注意事项

### 1. 注册事件时机变更

新版本中，饰品与槽位的注册推荐在 `LoadServerAddonScriptsAfter` 事件或执行顺序在其之后的事件中进行。如果在 `LoadServerAddonScriptsAfter` 中调用注册接口，**需要延迟一帧执行**（`AddTimer(0, callback)`），以确保组件内部的注册系统已完成初始化。

```python
# 正确做法
def onLoadServerAddonScriptsAfter(self, data):
    from Script_Platinum.utils.serverUtils import compFactory
    compFactory.CreateGame(serverApi.GetLevelId()).AddTimer(0, self._registerBauble)
```

### 2. 方法变更

以下方法发生了变更：

| 方法名 | 说明 |
|------------|------|
| `DeleteGlobalBaubleSlot` | **已不支持删除全局槽位**，调用仅输出错误日志 |

### 3. API 直接返回数据

新版本中以下方法会**直接返回数据**，无需再通过监听事件获取（但仍兼容旧版事件方式）：

- `GetPlayerBaubleInfo(playerId)` → 直接返回玩家饰品信息 dict
- `GetGlobalBaubleSlotInfo()` → 直接返回全局槽位信息 list
- `GetTargetBaubleSlotInfo(playerId)` → 直接返回特定玩家槽位信息 list

```python
# 旧版本写法（仍兼容）
registerSys.GetPlayerBaubleInfo("playerId")
self.ListenForEvent(...commonConfig.BAUBLE_GET_INFO_EVENT, self, self.onBaubleGetInfo)

# 新版本推荐写法
baubleInfo = registerSys.GetPlayerBaubleInfo("playerId")
# 直接使用 baubleInfo 即可
```

### 4. `AddGlobalBaubleSlot` 参数变更

`isDefault` 参数已废弃。通过 `AddGlobalBaubleSlot` 注册的槽位默认即为全局槽位（所有玩家自动拥有），无需再传入 `isDefault=True`。该参数仍可传入，但不再生效。

```python
# 旧版本
registerSys.AddGlobalBaubleSlot("slotId", "slotType", "名称", "贴图路径", True)  # isDefault=True

# 新版本（isDefault已废弃，可省略）
registerSys.AddGlobalBaubleSlot("slotId", "slotType", "名称", "贴图路径")
```

### 5. 事件数据 `slotIndex` 字段含义变更

饰品穿脱事件（`BaubleEquippedEvent` / `BaubleUnequippedEvent`）返回的 data 中，`slotIndex` 字段的含义已变更：

- **旧版本**：若该槽位类型 `slotType` 的可用槽位大于 1 则返回由 1 开始的 `index`, 若该槽位类型仅有一个可用槽位, 则返回 0
- **新版本**：无论该槽位类型 `slotType` 的可用槽位为多少, 始终返回槽位类型中列表的index, 即  0-x

如果你的代码依赖 `data["slotIndex"]` 进行判断，**必须修改匹配逻辑**。

```python
# 旧版本
if data["slotType"] == BaubleEnum.Other:
    slotIndex = data["slotIndex"] # 返回 1-4
if data["slotType"] == BaubleEnum.Helmet:
    slotIndex = data["slotIndex"] # 返回 0
# 新版本
if data["slotType"] == BaubleEnum.Other:
    slotIndex = data["slotIndex"] # 返回 0-3
if data["slotType"] == BaubleEnum.Helmet:
    slotIndex = data["slotIndex"] # 返回 0
```

### 6. 示例代码路径变更

内置示例代码（旅行者腰带）的文件路径已变更：

- **旧版本**：`buildInBaubleServer.py`（服务端）+ `buildInBaubleClient.py`（客户端）
- **新版本**：`server/inner/baubleServer.py`（仅服务端）

新版本中客户端的穿脱广播由组件内部自动完成，不再需要单独的客户端示例文件。

---

## 二、旧版本兼容性

新版本在以下方面保持了向后兼容：

| 兼容项 | 说明 |
|-------|------|
| 旧版槽位类型传入 | 传入 `commonConfig.BaubleEnum` 常量会自动转换为新版 slotType |
| 旧版槽位ID传入 | 传入旧版 slotName（如 `"hand_1"`、`"other_2"`）会自动转换为新版 slotId（如 `"bauble_hand0"`、`"bauble_other1"`） |
| 事件监听方式 | `GetPlayerBaubleInfo`、`GetGlobalBaubleSlotInfo`、`GetTargetBaubleSlotInfo` 仍会广播事件 |
| `BaubleRegister` 接口 | `baubleSlot` 参数兼容旧版字符串和新版列表 |

---

## 三、迁移检查清单

迁移时请按以下清单逐项检查你的代码：

- [ ] **注册事件时机**：如果在 `LoadServerAddonScriptsAfter` 事件注册信息则需延迟一帧再执行
- [ ] **事件参数`slotIndex`注意适配**：检查 `BaubleEquippedEvent` / `BaubleUnequippedEvent` 事件中是否用到了 `slotIndex` 的参数进行判断注意适配
- [ ] **`isDefault` 参数清理**：检查 `AddGlobalBaubleSlot` 调用中的 `isDefault` 参数，可安全移除
- [ ] **数据获取方式优化**：考虑将通过事件监听获取数据的方式改为直接使用方法返回值
- [ ] **示例代码引用路径**：更新引用示例代码的路径为新路径 `server/inner/baubleServer.py`

---

## 四、快速对照表

### API 方法对照

| 功能 | 方法名 | 变更情况 |
|-----|-------|---------|
| 注册饰品 | `BaubleRegister(data)` | 无变更 |
| 注册全局槽位 | `AddGlobalBaubleSlot(...)` | `isDefault` 参数已废弃 |
| 注册玩家槽位 | `AddTargetBaubleSlot(...)` | 无变更 |
| 删除全局槽位 | `DeleteGlobalBaubleSlot(...)` | ⚠️ 已不支持 |
| 获取玩家饰品信息 | `GetPlayerBaubleInfo(...)` | 新增直接返回值 |
| 获取全局槽位信息 | `GetGlobalBaubleSlotInfo()` | 新增直接返回值 |
| 获取玩家槽位信息 | `GetTargetBaubleSlotInfo(...)` | 新增函数 |
| 设置全部饰品数据 | `SetPlayerBaubleInfo(...)` | 无变更 |
| 设置槽位饰品数据 | `SetPlayerBaubleInfoWithSlot(...)` | 无变更 |
| 减少饰品耐久度 | `DecreaseBaubleDurability(...)` | 无变更 |

### 事件数据字段对照

| 字段 | 旧版本 | 新版本 |
|-----|-------|-------|
| `baubleSlotId` | 无 | 新增，槽位唯一ID如 `"bauble_helmet"` |
| `slotIndex` | 无 | 新增，同类型槽位中的索引 |
| `isFirstLoad` | 无 | 新增，是否为加入游戏自动穿戴 |