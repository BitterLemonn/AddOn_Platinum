# -*- coding: utf-8 -*-

from functools import wraps
from Util import Unknown, import_module, NewFun
if 1 > 2:
    # 看什么看 我知道你一脸懵逼 但先听我说 这个东西是补全库 这句话是阻止补全库被真正import的
    import QuServerApi.extraServerApi as extraServerApi
from Util import GlobSpaceName, CallDict, ModDirName
from QuServerApi.Events import Events
import IN as __IN; __IN.IsServerUser = True
import mod.server.extraServerApi as __extraServerApi
serverApi = __extraServerApi # type: extraServerApi
TickEvent = "OnScriptTickServer"; levelId = serverApi.GetLevelId()
System = serverApi.GetSystem("Minecraft","game") # type: extraServerApi
DestroyEntity = System.DestroyEntity # 实体注销接口
EnSp,EnSy = serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName() # 获取事件引擎
__EveLis = [] ; __AppendEveLis = __EveLis.append # 记录监听的事件
TemporaryContainer = type("TemporaryContainer",(object,),{}); SYSTEMDIC = {} # 记录系统
from time import time

def setSystem(module, systemName=None):
    """ 设置系统 用于注册流程 """
    if systemName == None:
        from uuid import uuid4
        systemName = str(uuid4()).replace("-","")
    SYSTEMDIC[systemName] = module

def ListenForEvent(EventName, ParentObject=None, Function=lambda:None):
    # type: (str, object, object) -> object
    '''
            注册事件监听 (事件名, 父对象, 函数|方法|可执行对象)
    '''
    EventName = EventName if isinstance(EventName, str) else EventName.__name__
    FunctionName = Function.__name__
    if not ParentObject:
        ParentObject = TemporaryContainer()
        setattr(ParentObject, FunctionName, Function)
    System.ListenForEvent(EnSp,EnSy,EventName,ParentObject,Function)
    return ParentObject

def UnListenForEvent(EventName, ParentObject=None, Function=lambda:None):
    # type: (str, object, object) -> bool
    '''
            反注册事件监听 (事件名, 父对象, 函数|方法|可执行对象)
    '''
    EventName = EventName if isinstance(EventName, str) else EventName.__name__
    FunctionName = Function.__name__
    if not ParentObject:
        ParentObject = TemporaryContainer()
        setattr(ParentObject, FunctionName, Function)
    System.UnListenForEvent(EnSp,EnSy,EventName,ParentObject,Function)
    return True

def SER_SYSTEM_APPEND(SystemName, Obj):
    SYSTEMDIC[SystemName] = Obj

def Destroy():
    __OnEnd() # 反注销监听

# 获取本地创建的系统端
def GetSystem(SystemName):
    ''' 
            获取本地创建的系统端,EasyMod(..).Server|Client(Path,SystemName="")
            需在创建服务|客户端时分配系统名
    '''
    return SYSTEMDIC.get(SystemName)

# 监听事件
def Listen(__Event):
    ''' 
            [装饰器] @Listen(事件名:str)
            用于监听游戏事件
            
            /** 注意事项:使用该方法监听游戏事件不支持手动
            取消监听,直到游戏结束时自动取消,如需手动管理
            可使用System中的ListenForEvent **/
    '''
    Event = __Event if isinstance(__Event, str) else __Event.__name__
    def SetListen(Fun):
        # 判断先前有无注册过同函数的同事件监听
        NowPath = Fun.__module__+"."+Fun.__name__
        for LEvent, LFun, LTc, Path in __EveLis:
            if Path == NowPath:
                System.UnListenForEvent(EnSp,EnSy,Event,LTc,LFun)
                __EveLis.remove((LEvent, LFun, LTc, Path))
                print("[%s] 热重载监听: %s"%(Event, NowPath))
                break
        TC = TemporaryContainer()
        setattr(TC,Fun.__name__,Fun)
        __AppendEveLis((Event,Fun,TC, NowPath))
        System.ListenForEvent(EnSp,EnSy,Event,TC,Fun)
        return Fun
    return SetListen

# 该系统端结束时触发
def __OnEnd():
    System.UnDefineEvent(GlobSpaceName)
    for Event, Fun, TC, _ in __EveLis:
        System.UnListenForEvent(EnSp,EnSy,Event,TC,Fun)

# -- 在系统端中建立监听事件完成交互的实现 --

if not hasattr(System,GlobSpaceName):
    setattr(System,GlobSpaceName,True)
    setattr(System,CallDict,{})
    System.DefineEvent(CallDict) # 注册事件

# Call的回调处理
def __OnCall(args):
    Key = args["Key"]
    Args = args["Args"]
    Kwargs = args["Kwargs"]
    Dic = getattr(System,CallDict)
    Fun = Dic.get(Key,None)
    if not Fun:
        if not (Key.startswith("__") and Key.endswith("__")):
            print("[Error]: '%s' 无效的请求,请检查是否遗漏相关装饰注册"%(Key))
        return None
    try:
        Fun(*Args, **Kwargs)
    except Exception as e:
        print("[Error]: "+str(e)+"  >> "+Fun.__name__)


TC = TemporaryContainer()
setattr(TC,__OnCall.__name__,__OnCall)
System.ListenForEvent("Minecraft","game",CallDict,TC,__OnCall)

# -- 在系统端中建立监听事件完成交互的实现 --


# 触发指定玩家的客户端函数
def Call(PlayerId, Key, *Args, **Kwargs):
    ''' 
            用于 服务端与客户端(反之同理) 的交互
            需要在被调用的函数上使用CallBackKey|AllowCall装饰器
            Call方法用于调用对立端的指定函数
            如 Call("-913702423", "Test", ....)
            第一,二个参数为 (玩家id, Key值) ,随后任意参数量 依函数形参量决定
            如果[玩家ID]填写 "*" 则表示全体玩家
            /** 注意事项: Call方法只调用对方端的函数,不调用本端函数 **/
    '''
    Data = {"Key":Key,"Args":Args,"Kwargs":Kwargs}
    if PlayerId == "*":
        System.BroadcastToAllClient(CallDict, Data)
        return None
    System.NotifyToClient(PlayerId, CallDict, Data)


# 设置回调键用的装饰器
def CallBackKey(Key):
    '''
            [装饰器] 用于给指定函数标记任意Key:str值,方便使用Call方法跨端交互
            例如: @CallBackKey("Test")
    '''
    def Set(Fun):
        Dic = getattr(System,CallDict)
        if isinstance(Dic,dict):
            Dic[Key] = Fun
        return Fun
    return Set

def AllowCall(Fun):
    """
            允许调用(跨端交互), 同等于CallBackKey区别是自动以当前函数名字设置参数, 无需手动配置
    """
    Key=Fun.__name__
    Key2=Fun.__module__+"."+Key
    Key3 = Key2.split(ModDirName+".",1)[1]
    Dic = getattr(System,CallDict)
    if isinstance(Dic,dict):
        Dic[Key] = Fun
        Dic[Key2] = Fun
        Dic[Key3] = Fun
    return Fun

def LocalCall(Fun,*Args,**Kwargs):
    ''' 本地调用 执行当前端@AllowCall|@CallBackKey("...")的方法 '''
    Dic = getattr(System,CallDict)
    if isinstance(Dic,dict):
        return Dic[Fun](*Args,**Kwargs)

class EasyThread:
    ''' QuMod提供的简易多线程 '''
    from Util import ThreadLock
    @classmethod
    def IsThread(cls, *Args, **Kwargs):
        ''' 用于将函数装饰为多线程下执行的函数 @IsThread 无参数'''
        from Util import IsThread
        return IsThread(*Args, **Kwargs)
    
    @classmethod
    def NextTick(cls, Fun, Args=tuple(), Kwargs={}, WaitReturn=False):
        ''' 
            添加函数到下一游戏Tick运行 用于解决线程下无法使用API的现象
            选填参数 WaitReturn=False(默认值) 设置为True后将会等待返回结果后再执行后续代码
            Args=tuple(),Kwargs={} 可传参
        '''
        cls.ThreadLock.acquire() # 上锁
        TC = TemporaryContainer()
        Back = []
        def Tick(_Args={}):
            System.UnListenForEvent(EnSp,EnSy,TickEvent,TC,Tick)
            RunBack = Fun(*Args,**Kwargs)
            Back.append(RunBack)
            
        setattr(TC,Tick.__name__,Tick)
        System.ListenForEvent(EnSp,EnSy,TickEvent,TC,Tick)
        cls.ThreadLock.release() # 释放锁
        # 返回值处理
        if WaitReturn:
            while not len(Back):
                pass
            return Back[0]


class EntityCompController:
    """ 实体组件控制器 用来处理全局Tick循环以及死亡判定 """
    class QuEventASData(object):
        """ 关于自我的事件数据 """
        def __init__(self, eventName, parent, callBack):
            self.eventName = eventName
            """ 事件名称 """
            self.parent = parent    # type: EntityCompCls
            """ 父节点 即注册者self实例 """
            self.callBack = callBack
            """ 回调方法 """
    
    class QuEvent(object):
        """ 事件组 """
        def __init__(self, eventName, callBack):
            self.eventName = eventName
            """ 事件名字 """
            self.callBack = callBack
            """ 回调方法 """
            ListenForEvent(eventName, self, self.Run)
        
        def Run(self, args):
            return self.callBack(args)
        
        def Remove(self):
            UnListenForEvent(self.eventName, self, self.Run)

    RunState = False
    """ 运行状态 """
    LastTickTime = 0
    """ 上一次Tick时间 """
    EntityCompDic = {
    }   # type: dict[str,list[EntityCompCls]]
    """ 实体组件映射表 """
    EntityCompSleepDic = {
    }   # type: dict[str,list[SuperEntityCompCls]]
    """ 实体组件休眠表 """
    GlobalEventsDic = {
    }   # type: dict[EntityCompController.QuEvent, list[EntityCompController.QuEventASData]]
    """ 全局事件响应字典 """
    CachePlayerList = []    # type: list[str]
    """ 玩家缓存列表(如处于传送状态的玩家) """
    StopRender = False
    """ 停止渲染 """

    @staticmethod
    def GetPlayerDmDict():
        # type: () -> dict[str,list[str]]
        """ 获取玩家维度字典 """
        playerList = serverApi.GetPlayerList()
        dmDict = {} # type: dict[str,list[str]]
        for playerId in playerList:
            dm = str(Entity(playerId).Dm)
            lis = dmDict.get(dm, [])
            lis.append(playerId)
            dmDict[dm] = lis
        return dmDict
    
    @staticmethod
    def CanEntityRender(comp, playerDmDict):
        # type: (EntityCompCls, list[str]) -> bool
        """ 用于计算实体是否可以渲染 """
        entityId = comp.entityId
        if entityId == levelId or comp.persistentWork: # 持久化工作
            return True
        if EntityCompController.StopRender:
            return False
        dm = str(Entity(entityId).Dm)
        if dm != "0" and not dm in playerDmDict:
            comp.RemoveComp()
            return False
        try:
            if serverApi.GetEngineCompFactory().CreatePlayer(entityId).GetRelevantPlayer(EntityCompController.CachePlayerList):
                return True
        except:
            pass
        return False

    @staticmethod
    def PointDistance(point1, point2):
        # type: (tuple, tuple) -> float
        """ 两点测距 """
        x1, y1, z1 = point1
        x2, y2, z2 = point2
        result = ((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)**0.5
        return result

    @staticmethod
    def QuListenForEventAboutSelf(data):
        # type: (EntityCompController.QuEventASData) -> bool
        """ 注册事件监听 """
        eventName = data.eventName
        for Obj, Lis in EntityCompController.GlobalEventsDic.items():
            if Obj.eventName == eventName:
                # 已找到事件组 归入数据
                Lis.append(data)
                return True
        # 未找到事件组 初始化数据
        eventDataList = [ data ]    # type: list[EntityCompController.QuEventASData]
        def OnEvent(args):
            if not (args and isinstance(args, dict)):
                return
            KeyEntityIdList = args.values()
            for ASData in eventDataList:
                if ASData.parent.entityId in KeyEntityIdList:
                    EntityCompController.TryExec(ASData.callBack, args)
        EntityCompController.GlobalEventsDic[
            EntityCompController.QuEvent(eventName, OnEvent)
        ] = eventDataList
        return True
    
    @staticmethod
    def QuDelAllEventASData(SELF):
        # type: (EntityCompCls) -> bool
        """ 清空所有相关事件监听基于实例 """
        DelEventList = [] # type: list[EntityCompController.QuEvent]
        """ 待清理的事件组 """
        for QEvent, EventList in EntityCompController.GlobalEventsDic.items():
            for QEventData in EventList[::]:
                if QEventData.parent == SELF:
                    # 删除事件数据
                    EventList.remove(QEventData)
            if len(EventList) == 0:
                # 该事件组无数据 销毁事件组
                DelEventList.append(QEvent)
        for QEvent in DelEventList:
            QEvent.Remove()
            del EntityCompController.GlobalEventsDic[QEvent]
        return True

    @staticmethod
    def TryExec(Fun, *Args, **Kwargs):
        """ 尝试执行函数 """
        try:
            Fun(*Args, **Kwargs)
        except Exception as e:
            print("[Error]: {Name} >> {Doc}".format(Name=Fun.__name__ if "__name__" in dir(Fun) else str(Fun), Doc=str(e)))

    @staticmethod
    def AddEntityComp(entityId, comp):
        # type: (str, EntityCompCls) -> bool
        """ 添加实体组件 """
        if entityId == None: return False
        if not entityId in EntityCompController.EntityCompDic:
            EntityCompController.EntityCompDic[entityId] = [] # 初始化数据
        List = EntityCompController.EntityCompDic[entityId]
        if comp in List: return False
        List.append(comp)
        return False

    @staticmethod
    def RemoveEntityComp(entityId, comp):
        # type: (str, EntityCompCls) -> bool
        """ 移除实体组件 如果存在 """
        if entityId == None: return False
        if entityId in EntityCompController.EntityCompDic:
            List = EntityCompController.EntityCompDic[entityId]
            if comp in List:
                if comp.QuAddToEventEngine:
                    EntityCompController.TryExec(
                        EntityCompController.QuDelAllEventASData, comp
                    )
                List.remove(comp)
                return True
        return False

    @staticmethod
    def RemoveEntityAllComps(entityId):
        # type: (str) -> bool
        """ 移除实体所有组件 """
        if entityId == None: return False
        if entityId in EntityCompController.EntityCompDic:
            for Comp in EntityCompController.EntityCompDic[entityId][::]:
                EntityCompController.TryExec(Comp.RemoveComp)
            try:
                del EntityCompController.EntityCompDic[entityId]
            except Exception as e:
                print("[Error]: "+str(e))
        return False

    @staticmethod
    def OnScriptTickServer(_={}):
        """ 建立全局循环 """
        nowTime = time()
        if nowTime >= EntityCompController.LastTickTime+1/30.0/2.0:
            # 执行组件tick
            playerDmDict = EntityCompController.GetPlayerDmDict()
            for _, compList in EntityCompController.EntityCompDic.items():
                for comp in compList[::]:
                    if not EntityCompController.CanEntityRender(comp, playerDmDict):
                        comp.compIsWorking = False
                        continue
                    comp.compIsWorking = True
                    EntityCompController.TryExec(comp.OnTick)
        EntityCompController.LastTickTime = nowTime
    
    @staticmethod
    def EntityRemoveEvent(args):
        """ 实体删除事件 """
        entityId = args["id"]
        if entityId in EntityCompController.EntityCompDic:
            EntityCompController.RemoveEntityAllComps(entityId)
        if entityId in EntityCompController.EntityCompSleepDic:
            EntityCompController.RemoveSleepComp(entityId)
    
    @staticmethod
    def RemoveSleepComp(entityId):
        # type: (str) -> bool
        """ 删除休眠组件 """
        try:
            compList = EntityCompController.EntityCompSleepDic[entityId]    # 休眠组件列表
            for comp in compList:
                del comp.__class__.UserList[entityId]                       # 从用户组件清单移除
                EntityCompController.TryExec(comp.OnRemove)
            del EntityCompController.EntityCompSleepDic[entityId]
        except:
            return False
        return True
    
    @staticmethod
    def DimensionChangeServerEvent(args):
        """ 玩家开始切换维度 """
        data = Events.DimensionChangeServerEvent(args)
        EntityCompController.CachePlayerList.append(data.playerId)
        if len(serverApi.GetPlayerList()) <= 1:
            EntityCompController.StopRender = True

    @staticmethod
    def DimensionChangeFinishServerEvent(args):
        """ 玩家切换维度完毕 """
        data = Events.DimensionChangeFinishServerEvent(args)
        cacheList = EntityCompController.CachePlayerList
        if data.playerId in cacheList:
            cacheList.remove(data.playerId)
        EntityCompController.StopRender = False

    @staticmethod
    def Run():
        """ 运行服务 """
        if not EntityCompController.RunState:
            EntityCompController.RunState = True
            ListenForEvent(Events.OnScriptTickServer, EntityCompController, EntityCompController.OnScriptTickServer)
            ListenForEvent(Events.EntityRemoveEvent, EntityCompController, EntityCompController.EntityRemoveEvent)
            ListenForEvent(Events.DimensionChangeServerEvent, EntityCompController, EntityCompController.DimensionChangeServerEvent)
            ListenForEvent(Events.DimensionChangeFinishServerEvent, EntityCompController, EntityCompController.DimensionChangeFinishServerEvent)


class EntityCompCls(object):
    """ QuMod提供的实体组件类 开发者可以继承并开发实体组件功能 """
    # UserList 用作记录使用者Id,防止同组件复用现象
    UserList = {}  # type: dict[str,EntityCompCls]
    @classmethod
    def GetUserList(cls):
        # type: () -> dict[str, EntityCompCls]
        if cls.UserList is EntityCompCls.UserList:
            cls.UserList = {}
        return cls.UserList

    @classmethod
    def GetComp(cls, entityId):
        # type: (str) -> EntityCompCls | None
        """ 
            [静态方法] 获取指定实体的组件实例
            直接调用 cls.GetComp(xxx) 即可
            cls表示类 而不是 实例化的数据对象
        """
        try:
            return cls.UserList[entityId]
        except Exception:
            return None
        
    def __init__(self, entityId):
        self.entityId = entityId
        self.InitState = True
        """ 初始化状态 """
        self.persistentWork = False # type: bool
        """ 持久化工作

        设置为True时组件将不会计算渲染范围并且不会因为当前维度丢失玩家客户端而主动销毁组件
        除非生物销毁/主动销毁组件, 此外levelId全局组件不受该属性影响
        """
        self.compIsWorking = False
        """ 组件是否在工作 由引擎直接设置 """

        cls = self.__class__
        if cls.UserList is EntityCompCls.UserList:
            cls.UserList = {}
        if entityId in cls.UserList:
            self.InitState = False
            return None
        self.QuAddToEventEngine = False
        """ (不建议改动) 是否被添加到事件引擎 使用QuListenForEventAboutSelf方法后即被登记将在组件销毁时识别处理 """
        EntityCompController.Run()
        EntityCompController.AddEntityComp(self.entityId, self)
        cls.UserList[entityId] = self

    def OnRemove(self):
        """ [可覆写] 组件移除后自动执行 不建议在此处再次移除实体 """
        pass
    
    def OnTick(self):
        """ [可覆写] Tick 一秒30次 如有需要可以覆写此方法 """
        pass

    def QuListenForEventAboutSelf(self, eventName, callback):
        # type: (str | object, object) -> bool
        """
            监听有关与自我的事件
            与直接注册监听不同, 该方法由QuMod实体组件全局事件引擎处理
            仅当指定事件的返回参数中涉及到当前实体时回调
            在实体死亡/组件销毁时自动结束监听
        """
        eventName = eventName if eventName and isinstance(eventName, str) else eventName.__name__
        self.QuAddToEventEngine = True
        return EntityCompController.QuListenForEventAboutSelf(
            EntityCompController.QuEventASData(
                eventName, self, callback
            )
        )
    
    def RemoveComp(self):
        """ 删除组件方法,可以手动调用 生物死亡后也会自动调用 """
        try:
            cls = self.__class__
            del cls.UserList[self.entityId]
            EntityCompController.RemoveEntityComp(self.entityId, self)
            self.OnRemove()
            return True
        except:
            pass
        return False


class SuperEntityCompCls(EntityCompCls):
    """ 超级实体组件类
    
        基于EntityCompCls实现的增强版组件类, 相较于EntityCompCls它具有定时器管理,休眠策略等功能
        使用SuperEntityCompCls时需确保重新实现时正确调用父类方法, 否则可能导致功能无效
    """
    class Timer(object):
        """ 定时器 允许传递参数亦或者设置循环 """
        def __init__(self, callObject, argsTuple=tuple(), kwargsDict=dict(), time=0.0, loop=False):
            # type: (object, tuple, dict, float, bool) -> None
            self.callObject = callObject
            self.argsTuple = argsTuple
            self.kwargsDict = kwargsDict
            self.loop = loop
            self.setTime = time
            self.valueTime = time
        
        def call(self):
            try:
                self.callObject(*self.argsTuple, **self.kwargsDict)
            except Exception as e:
                print("[Error]: "+str(e))
        
        def copy(self):
            # type: () -> SuperEntityCompCls.Timer
            """ 拷贝定时器 """
            return self.__class__(self.callObject, self.argsTuple, self.kwargsDict, self.setTime, self.loop)

    @classmethod
    def creat(cls, entityId, *args, **kwargs):
        # type: (str, tuple, dict) -> bool
        """ 创建组件 如果已存在则返回False """
        comp = cls.GetComp(entityId)    # type: SuperEntityCompCls | None
        if comp != None:
            return False
        cls(entityId, *args, **kwargs)
        return True

    def __init__(self, entityId):
        EntityCompCls.__init__(self, entityId)
        self.__timerList = []   # type: list[SuperEntityCompCls.Timer]
        self.__sleepState = False
        self.__isDelComp = False

    def addTimer(self, timer):
        # type: (Timer) -> bool
        """ 添加定时器 (同一份定时器不允许多次添加,如有需要可使用定时器的copy方法) """
        if timer in self.__timerList:
            return False
        self.__timerList.append(timer)
        return True
    
    def removeTimer(self, timer):
        # type: (Timer) -> bool
        """ 删除定时器 """
        if not timer in self.__timerList:
            return False
        self.__timerList.remove(timer)
        return True

    def OnTick(self):
        EntityCompCls.OnTick(self)
        # timer定时器处理
        delTimerList = []  # type: list[SuperEntityCompCls.Timer]
        tickTime = 1.0/30.0
        for timer in self.__timerList:
            timer.valueTime -= tickTime
            if timer.valueTime <= 0.0:
                timer.call()
                if timer.loop == False:
                    # 标记删除定时器
                    delTimerList.append(timer)
                else:
                    # 重置定时器
                    timer.valueTime = timer.setTime
        for timer in delTimerList:
            self.removeTimer(timer)

    def callEvent(self, eventName):
        """ 执行自身的json event """
        comp = serverApi.GetEngineCompFactory().CreateEntityEvent(self.entityId)
        return comp.TriggerCustomEvent(self.entityId, eventName)
    
    def setSleepState(self, state):
        # type: (bool) -> bool
        """ 设置休眠状态

            处于休眠状态下的组件实例依旧存在 但不会被组件管理器驱动工作
            不会进入Tick更新, 生物死亡后不会智能回收
            可以被查询与获取
        """
        if self.__sleepState == state:
            return False
        self.__sleepState = state
        if state == True:
            try:
                # 从组件管理器中移除自己的存档 此时将不会被tick驱动/智能回收
                EntityCompController.RemoveEntityComp(self.entityId, self)
                sleepCompList = EntityCompController.EntityCompSleepDic.get(self.entityId, [])
                sleepCompList.append(self)
                EntityCompController.EntityCompSleepDic[self.entityId] = sleepCompList
            except:
                return False
            EntityCompController.TryExec(self.onSleep)
        else:
            try:
                # 在组件管理器中添加自己的存档
                EntityCompController.AddEntityComp(self.entityId, self)
                sleepCompList = EntityCompController.EntityCompSleepDic.get(self.entityId, [])
                if self in sleepCompList:
                    sleepCompList.remove(self)
            except:
                return False
            if self.__isDelComp: return True
            EntityCompController.TryExec(self.onUnSleep)
        return True
    
    def getSleepState(self):
        # type: () -> bool
        """ 获取休眠状态 """
        return self.__sleepState

    def tryRemoveComp(self, compCls):
        # type: (type[EntityCompCls]) -> bool
        """ 尝试删除当前实体的指定组件 """
        comp = compCls.GetComp(self.entityId)    # type: EntityCompCls
        if comp:
            comp.RemoveComp()
            return True
        return False

    def onSleep(self):
        """ 休眠回调方法 可覆写 """

    def onUnSleep(self):
        """ 结束休眠回调方法 可覆写 """

    def RemoveComp(self):
        self.__isDelComp = True
        if self.getSleepState():
            self.setSleepState(False)
        return EntityCompCls.RemoveComp(self)

# CustomGoalCls = serverApi.GetCustomGoalCls()
# class CustomJsonCompCls(SuperEntityCompCls, CustomGoalCls):
#     """ 自定义JSON组件类

#         方法 CanUse CanContinueToUse CanBeInterrupted OnStart OnStop OnCompTick 均需要重新实现
#         与原生 CustomGoalCls 不同, 该组件类同时继承了QuMod的SuperEntityCompCls并重新实现了组件生命周期管理

#         OnCompTick 与 OnTick 前者为网易原生CustomGoalCls提供的组件更新回调, 后者为SuperEntityCompCls的回调
#         两者均可使用。
#     """
#     def __init__(self, entityId, **kwargs):
#         SuperEntityCompCls.__init__(self, entityId)
#         CustomGoalCls.__init__(self, entityId, kwargs)

#     def CanUse(self):
#         # type: () -> bool
#         """ 行为能否使用, 行为未被执行时, 引擎每帧调用。返回True时, 若没有其他低优先级值的冲突行为且正在执行的高优先级值行为能被打断时, 则开始执行此行为, 调用Start函数 """
#         return True

#     def CanContinueToUse(self):
#         # type: () -> bool
#         """ 行为能否被继续使用, 行为被执行时, 每帧判断. 是行为是否能继续使用的判断条件之一 """
#         return True

#     def CanBeInterrupted(self):
#         # type: () -> bool
#         """ 行为能否被其他行为打断, 行为在执行状态时, 引擎每帧调用。运行时不能动态修改返回值, 必须一直返回True或False """
#         return True
    
#     def OnStart(self):
#         """ 行为开始时执行的函数 """

#     def OnStop(self):
#         """ 行为停止时执行的函数 """
    
#     def OnTick(self):
#         """ 组件更新时 每秒至多30次 """
#         return SuperEntityCompCls.OnTick(self)
    
#     def OnCompTick(self):
#         """ 行为执行状态下, 每秒执行最多20次, 机器性能差时会降频 """

#     def Start(self):
#         self.setSleepState(False)   # 恢复工作
#         return self.OnStart()

#     def Stop(self):
#         self.setSleepState(True)    # 组件休眠
#         return self.OnStop()

#     def Tick(self):
#         return self.OnCompTick()

# ---- QuMod提供的一些基于原版API的组件 ----

class Entity(object):
    __slots__ = ("entityId","PropertySettingsDic",)
    ErrorSet = "[Error]: 不支持的属性设置"
    class HealthComp(object):
        ''' 生命值组件 '''
        def __init__(self,entityId):
            # type: (str) -> None
            self.entityId = entityId
            self.PropertySettingsDic = {
                "Value":self.SetValue,
                "Max":self.SetMax
            }
        def __setattr__(self, Name, Value):
            ''' 属性设置处理 '''
            if Name in Entity.__slots__:
                return object.__setattr__(self, Name, Value)
            elif Name in self.PropertySettingsDic:
                Fun = self.PropertySettingsDic[Name]
                return Fun(Value)
            else:
                print(Entity.ErrorSet)
                return None
        def SetValue(self,Value):
            ''' 设置Value值 '''
            comp = serverApi.GetEngineCompFactory().CreateAttr(self.entityId)
            return comp.SetAttrValue(0,Value)
        def SetMax(self,Value):
            ''' 设置Max值 '''
            comp = serverApi.GetEngineCompFactory().CreateAttr(self.entityId)
            return comp.SetAttrMaxValue(0,Value)
        @property
        def Value(self):
            # type: () -> int
            comp = serverApi.GetEngineCompFactory().CreateAttr(self.entityId)
            return comp.GetAttrValue(0)
        @property
        def Max(self):
            # type: () -> int
            comp = serverApi.GetEngineCompFactory().CreateAttr(self.entityId)
            return comp.GetAttrMaxValue(0)
    
    def __init__(self, __entityId):
        # type: (str) -> None
        self.entityId = __entityId
        self.PropertySettingsDic = {
            "Pos":self.__SetPos,
            "FootPos":self.__SetPos,
            "Rot":self.__SetRot,
        }

    def __setattr__(self, Name, Value):
        ''' 属性设置处理 '''
        if Name in Entity.__slots__:
            return object.__setattr__(self, Name, Value)
        elif Name in self.PropertySettingsDic:
            Fun = self.PropertySettingsDic[Name]
            return Fun(Value)
        else:
            print(Entity.ErrorSet)
            return None

    # ---  可查询/设置属性 ---
    @property
    def Health(self):
        # type: () -> Entity.HealthComp
        ''' 实体生命值属性 '''
        Cls = self.__class__
        return Cls.HealthComp(self.entityId)
    
    @property
    def Pos(self):
        # type: () -> tuple[float,float,float]
        return serverApi.GetEngineCompFactory().CreatePos(self.entityId).GetPos()

    @property
    def FootPos(self):
        # type: () -> tuple[float,float,float]
        return serverApi.GetEngineCompFactory().CreatePos(self.entityId).GetFootPos()

    @property
    def Rot(self):
        # type: () -> tuple[float,float]
        return serverApi.GetEngineCompFactory().CreateRot(self.entityId).GetRot()

    @property
    def Identifier(self):
        # type: () -> str
        return serverApi.GetEngineCompFactory().CreateEngineType(self.entityId).GetEngineTypeStr()

    @property
    def Dm(self):
        # type: () -> int
        return serverApi.GetEngineCompFactory().CreateDimension(self.entityId).GetEntityDimensionId()
    
    @property
    def DirFromRot(self):
        # type: () -> tuple[float,float,float]
        return serverApi.GetDirFromRot(self.Rot)
    
    @property
    def DimensionId(self):
        # type: () -> int
        return self.Dm
    # ---  可查询/设置属性 ---
    
    # ----- 后处理 设置属性 ----
    def __SetPos(self,Value):
        # type: (tuple[float,float,float]) -> bool
        return serverApi.GetEngineCompFactory().CreatePos(self.entityId).SetPos(Value)

    def __SetRot(self,Value):
        # type: (tuple[float,float]) -> bool
        return serverApi.GetEngineCompFactory().CreateRot(self.entityId).SetRot(Value)
    # ----- 后处理 设置属性 ----
    
    def Destroy(self):
        # 销毁实体
        return DestroyEntity(self.entityId)
    
    def Kill(self):
        # 杀死实体
        return serverApi.GetEngineCompFactory().CreateGame(levelId).KillEntity(self.entityId)
    
# ---- QuMod提供的一些基于原版API的组件 ----

@CallBackKey('__Client.Request__')
def __ClientRequest(PlayerId, Key, Args, Kwargs, BackKey):
    try:
        BackData = LocalCall(Key, *Args, **Kwargs)
    except Exception as e:
        Call(PlayerId, '__DelCallBackKey__', Key)
        raise e
    Call(PlayerId, BackKey, BackData)
    

@CallBackKey('__CALL.CLIENT__')
def __CallCLIENT(PlayerId, Key, Args, Kwargs):
    Call(PlayerId, Key, *Args, **Kwargs)