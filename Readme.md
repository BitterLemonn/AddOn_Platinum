## Platinum 铂(饰品栏) 组件使用指南

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

饰品的**最大堆叠数量**只能为1，否则会导致饰品注册失败

当饰品物品被定义为盔甲或食物时不能通过直接交互（右键，长按屏幕）直接穿戴饰品，请开发者避免出现此类情况(除非刻意为之)

### 五、使用方法

#### 1. 饰品注册

**开发者不能将本组件作为内容导入(可能会引发模组冲突)**，本组件会同时发布在网易资源市场当中，只需要玩家同时装载即可正常使用组件。

完成饰品注册需要通过以下代码发送事件来完成：

```py
# coding=utf-8
# 推荐将commonConfig.py中的常量复制到开发项目当中,方便使用
import mod.server.extraServerApi as serverApi


# 对应的服务端中监听mod加载完成事件
class BaubleRegister(serverApi.GetServerSystemCls()):
    def __init__(self, namespace, name):
        super(BaubleRegister, self).__init__(namespace, name)
        self.listenEvent()

    # 监听mod加载完成事件
    def listenEvent(self):
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
                            'ClientLoadAddonsFinishServerEvent', self, self.onClientLoadAddonsFinishServerEvent)

    # 对应的回调函数
    def onClientLoadAddonsFinishServerEvent(self, data):
        # 项目文件中获取一个与组件通信的服务端
        # 如导入了commonConfig.py中的常量可将nameSpace和systemName分别改为commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER
        registerSys = serverApi.GetSystem("platinum", "broadcasterServer")
        # 需要注册的饰品信息Dict
        baubleInfoDict = {
            "baubleName": "命名空间:物品名称",
            # 旧commonConfig.py中的常量将会自动转化为新版本的槽位id
            # 默认的槽位id列表请查看 八、数据说明
            "baubleSlot": "已注册的槽位id",
            # 此处可以填入一个列表，将饰品注册到多个槽位
            # "baubleSlot": ["槽位1", "槽位2"],
            # 可选 自定义信息提示 在此处设置自定义提示将会覆盖物品Json定义文件中的customTips
            "customTips": "自定义信息提示"
        }
        # 调用注册函数
        registerSys.BaubleRegister(baubleInfoDict)
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
# 为所有玩家注册饰品栏位
registerSys.AddGlobalBaubleSlot(
    "test_helmet",  # 槽位id slotId
    "test_helmet",  # 槽位类型 slotType
    "测试头盔",  # 槽位名称 slotName (为已有槽位类型添加新槽位时可省略)
    "textures/ui/bauble_helmet_slot",  # 槽位贴图路径 (为已有槽位类型添加新槽位时可省略)
    True  # 是否为默认槽位
)
# 为特定玩家注册饰品栏位
registerSys.AddTargetBaubleSlot(
    "playerId",  # 玩家id
    "test_helmet",  # 槽位id slotId
    "test_helmet",  # 槽位类型 slotType
    "测试头盔",  # 槽位名称 slotName (为已有槽位类型添加新槽位时可省略)
    "textures/ui/bauble_helmet_slot"  # 槽位贴图路径 (为已有槽位类型添加新槽位时可省略)
)
```

当注册一个新的槽位类型的槽位时，须完整传入槽位的贴图路径以及槽位名称，当仅需为已存在的槽位类型添加一个新的槽位时，可以省略槽位贴图路径、槽位名称。

**值得注意的是当使用AddGlobalBaubleSlot注册槽位时，有额外参数isDefaultSlot控制该槽位是否为默认槽位，当为True时，该槽位会在玩家加入游戏后默认拥有，并且不可删除。
**

#### 3. 槽位删除

通过**服务端**发送事件删除饰品栏位，开发者可以自定义删除饰品栏位的数量以及类型。代码如下：

```python
# coding=utf-8
# ===========仅服务端可用=============
# 项目文件中获取一个与组件通信的服务端
# 如导入了commonConfig.py中的常量可将nameSpace和systemName分别改为commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER
registerSys = serverApi.GetSystem("platinum", "broadcasterServer")
# 删除所有玩家的指定饰品栏位
registerSys.RemoveGlobalBaubleSlot("test_helmet")  # 传入参数为槽位id
# 删除特定玩家的指定饰品栏位
registerSys.RemoveTargetBaubleSlot("playerId", "test_helmet")
```

**值得注意的是，默认槽位不可删除**

#### 4.获取全局/特定玩家槽位信息

通过获取服务端组件可以发送获取全局/特定玩家槽位信息的事件，可以获取到全局/特定玩家已注册的槽位信息。代码如下：

```python
# coding=utf-8
# 项目文件中获取一个与组件通信的服务端
# 如导入了commonConfig.py中的常量可将nameSpace和systemName分别改为commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER
registerSys = serverApi.GetSystem("platinum", "broadcasterServer")
# 获取全局槽位信息
registerSys.GetGlobalBaubleSlotInfo()
# 获取特定玩家槽位信息
registerSys.GetTargetBaubleSlotInfo("playerId")

# -------------------------------
# 在服务端中可以监听到槽位信息
# 监听全局槽位信息返回事件
self.ListenForEvent(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER,
                    commonConfig.BAUBLE_GET_GLOBAL_SLOT_INFO_EVENT, self, self.onGetGlobalBaubleSlotInfo)
# 监听特定玩家槽位信息返回事件
self.ListenForEvent(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER,
                    commonConfig.BAUBLE_GET_TARGET_SLOT_INFO_EVENT, self, self.onGetTargetBaubleSlotInfo)
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

通过获取服务端组件可以发送获取特定玩家饰品数据的事件。代码如下：

```python
# coding=utf-8
# 获取饰品数据
# 项目文件中获取一个与组件通信的服务端
# 如导入了commonConfig.py中的常量可将nameSpace和systemName分别改为commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER
registerSys = serverApi.GetSystem("platinum", "broadcasterServer")
registerSys.GetPlayerBaubleInfo("playerId")  # 传入参数为playerId

# -------------------------------
# 在服务端中可以监听到玩家的饰品信息
# 监听饰品信息返回事件
self.ListenForEvent(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER,
                    commonConfig.BAUBLE_GET_INFO_EVENT, self, self.onBaubleGetInfo)


# 事件回调
def onBaubleGetInfo(data):
    playerId = data["playerId"]
    baubleDict = data["baubleDict"]
```

获取到的baubleDict数据详情请查看 **八、数据说明**

**值得注意的是，获取玩家饰品信息需在客户端事件onLocalPlayerStopLoading发生之后进行请求，否则会导致获取信息不正确**

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
registerSys.SetPlayerBaubleInfoWithSlot("playerId", {},
                                        "slotName")  # 这里填入playerId以及itemDict以及slotname slotname即槽位id 具体槽位id请查看 八、数据说明
```

**需要注意的是，设置玩家饰品操作需在客户端事件onLocalPlayerStopLoading之后进行设置，否则会被客户端本地数据覆盖**

#### 8. 设置玩家饰品耐久度

通过获取服务端组件调用指定的接口可以对特定玩家的特定槽位的饰品耐久度进行更改，示例代码如下:

```python
# coding=utf-8
# 设置饰品耐久度
# 项目文件中获取一个与组件通信的服务端
# 如导入了commonConfig.py中的常量可将nameSpace和systemName分别改为commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER
registerSys = serverApi.GetSystem("platinum", "broadcasterServer")
# 修改特定槽位饰品耐久度
registerSys.DecreaseBaubleDurability("playerId", "slotName", 1)
# 这里填入playerId以及slotName(slotName即槽位id 具体槽位id请查看 八、数据说明)以及需要减少的耐久度(默认为1)
```

**需要注意的是，设置玩家饰品操作需在客户端事件onLocalPlayerStopLoading之后进行设置，否则会被客户端本地数据覆盖**

### 六、示例代码

组件内还内置了一个腰带饰品【旅行者腰带】[服务端代码](behavior_pack_Platinum/Script_Platinum/buildInBaubleServer.py)、[客户端代码](behavior_pack_Platinum/Script_Platinum/buildInBaubleClient.py)
中详细的说明了如何进行饰品穿脱的监听以及对应功能的实现。实现了一个可以提升玩家跨越高度的饰品。

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
    "baubleSlot": str,  # 槽位名称(值为旧版commonConfig.py中的常量, 新版添加的槽位值与baubleSlotId一致)
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
                "isDefaultSlot": bool
            }
        }
        # ......
    ]
}
```

### 九、许可证

在遵循最终用户许可协议([EULA](EULA.txt))
的前提下，本组件遵循[MIT](LICENSE)开源协议，请开发者们随意使用。