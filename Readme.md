## Platinum 铂(饰品栏) 组件使用指南

### 一、简介

本组件旨在编写一个利于联动的饰品栏模组。方便上手，开箱即用是本组件的创作宗旨。开发者无需关注组件内部的工作逻辑，只需要向指定服务端发送事件即可注册饰品，监听指定事件便可获取玩家穿脱饰品情况。

### 二、UI展示

<center><img src="https://raw.githubusercontent.com/BitterLemonn/BlogPicBed/master/otherPic/202311201724656.png" style="zoom:65%;"></center>

<center><img src="https://raw.githubusercontent.com/BitterLemonn/BlogPicBed/master/otherPic/202311201724476.png" style="zoom:65%;"></center>

<center><img src="https://raw.githubusercontent.com/BitterLemonn/BlogPicBed/master/otherPic/202312011152292.png" style="zoom:65%"></center>

<center><img src="https://raw.githubusercontent.com/BitterLemonn/BlogPicBed/master/otherPic/202312011154787.png" style="zoom:65%"></center>

### 三、基础配置文件介绍

[配置文件](behavior_pack_Platinum/Script_Platinum/commonConfig.py)内存储了所有使用到的变量以及常量，理论上开发者只需要了解其中的变量的作用即可轻松使用本组件。

其中定义了组件所使用到的事件名称以及所使用到的SystemName和NameSpace。BaubleEnum类中定义了饰品栏的槽位以及对应的信息。BaubleDict字典中定义了组件将会使用到的饰品信息。

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
            # 推荐将commonConfig.py中的常量复制到开发项目当中
            "baubleSlot": "commonConfig.py中BaubleEnum定义的常量",
            # 此处可以填入一个列表，将饰品注册到多个槽位
            # "baubleSlot": ["槽位1", "槽位2"],
            # 可选 自定义信息提示 在此处设置自定义提示将会覆盖物品Json定义文件中的customTips
            "customTips": "自定义信息提示"
        }
        # 调用注册函数
        registerSys.BaubleRegister(baubleInfoDict)
```

#### 2.监听玩家饰品穿脱事件

通过注册监听事件，开发者可以监听到玩家穿脱饰品，可以在对应的回调函数中做出相应的逻辑处理。注册监听代码如下：

```py
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

接收到的data信息如下：

```py
# coding=utf-8
# 饰品装备事件
data = {
    "playerId": "",  # 玩家ID type: str
    "itemDict": {},  # 饰品信息Dict type: dict
    "baubleSlot": "",  # 饰品槽位 type: str
    "slotIndex": 0  # 饰品槽位索引 type: int
    # 饰品槽位索引只有当饰品槽位为HAND或OTHER时会有对应的值，否则为0
}
```

#### 3.获取玩家饰品数据

通过获取服务端组件可以发送获取特定玩家饰品数据的事件。代码如下：

```python
# coding=utf-8
# 获取饰品数据
# 项目文件中获取一个与组件通信的服务端
# 如导入了commonConfig.py中的常量可将nameSpace和systemName分别改为commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER
registerSys = serverApi.GetSystem("platinum", "broadcasterServer")
registerSys.GetPlayerBaubleInfo("playerId") # 传入参数为playerId

# -------------------------------
# 在服务端中可以监听到玩家的饰品信息
# 监听饰品信息返回事件
self.ListenForEvent(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER,
                    commonConfig.BAUBLE_GET_INFO_EVENT, self, self.onBabubleGetInfo)

# 事件回调
def onBabubleGetInfo(data):
    playerId = data["playerId"]
    baubleDict = data["baubleDict"]
```

获取到的baubleDict结构如下:

```py
# coding=utf-8
# 结构为 "slotname": itemDict 的字典
baubleDict = {
    "helmet": {},
    "necklace": {},
    "armor": {},
    "back": {},
    "hand_1": {},
    "hand_2": {},
    "belt": {},
    "shoes": {},
    "other_1": {},
    "other_2": {},
    "other_3": {},
    "other_4": {}
}
'''
其中slotname为铂饰品栏槽位名称:
helmet: 头盔
necklace: 项链
armor: 胸饰
back: 背饰
hand_1: 左手饰
hand_2: 右手饰
belt: 腰带
shoes: 鞋子
other_1: 护符1
other_2: 护符2
other_3: 护符3
other_4: 护符4
'''
```

**值得注意的是，获取玩家饰品信息需在客户端事件OnLoadClientAddonScriptsAfter发生之后进行请求，否则会导致获取信息不正确**

#### 4. 设置玩家饰品信息

通过获取服务端组件调用指定的接口可以对特定玩家的全部饰品信息或特定槽位的饰品信息进行更改，示例代码如下:

``` python
# coding=utf-8
# 设置饰品数据
# 项目文件中获取一个与组件通信的服务端
# 如导入了commonConfig.py中的常量可将nameSpace和systemName分别改为commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER
registerSys = serverApi.GetSystem("platinum", "broadcasterServer")
# 修改全部饰品数据
registerSys.SetPlayerBaubleInfo("playerId", {}) # 这里填入playerId以及baubleDict
# 修改特定槽位饰品数据
registerSys.SetPlayerBaubleInfoWithSlot("playerId", {}, "slotname") # 这里填入playerId以及itemDict以及slotname(slotname可接受的值请查看 5.4 获取玩家饰品信息)
```

**需要注意的是，设置玩家饰品操作需在客户端事件OnLoadClientAddonScriptsAfter之后进行设置，否则会被客户端本地数据覆盖**

#### 5. 设置玩家饰品耐久度

通过获取服务端组件调用指定的接口可以对特定玩家的特定槽位的饰品耐久度进行更改，示例代码如下:

``` python
# coding=utf-8
# 设置饰品耐久度
# 项目文件中获取一个与组件通信的服务端
# 如导入了commonConfig.py中的常量可将nameSpace和systemName分别改为commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER
registerSys = serverApi.GetSystem("platinum", "broadcasterServer")
# 修改特定槽位饰品耐久度
registerSys.DecreaseBaubleDurability("playerId", "slotname", 1) # 这里填入playerId以及slotname以及需要减少的耐久度(默认为1)
```

**需要注意的是，设置玩家饰品操作需在客户端事件OnLoadClientAddonScriptsAfter之后进行设置，否则会被客户端本地数据覆盖**

### 六、示例代码

组件内还内置了一个腰带饰品【旅行者腰带】[服务端代码](behavior_pack_Platinum/Script_Platinum/buildInBaubleServer.py)、[客户端代码](behavior_pack_Platinum/Script_Platinum/buildInBaubleClient.py)
中详细的说明了如何进行饰品穿脱的监听以及对应功能的实现。实现了一个可以提升玩家跨越高度的饰品。

### 七、后续开发

因为本组件旨在完成一个便于联动的饰品栏模组，有任何的接口需求也可以联系我
QQ：873811906，或加入开发者交流群：575858232，尽量满足各位开发者大大的需求。但是本人也只是一个组件小白，所以需求不一定能够满足，感谢各位大佬的指点以及使用~

### 八、许可证

在遵循最终用户许可协议([EULA](behavior_pack_Platinum/Script_Platinum/EULA.txt))的前提下，本组件遵循[MIT](behavior_pack_Platinum/Script_Platinum/LICENSE)开源协议，请开发者们随意使用。