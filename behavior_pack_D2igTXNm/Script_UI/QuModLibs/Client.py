# -*- coding: utf-8 -*-
from functools import wraps
if 1 > 2:
    # 看什么看 我知道你一脸懵逼 但先听我说 这个东西是补全库 这句话是阻止补全库被真正import的
    import QuClientApi.extraClientApi as extraClientApi
from Util import GlobSpaceName, CallDict, ModDirName
from Util import Unknown, import_module, NewFun
import mod.client.extraClientApi as __extraClientApi
from QuClientApi.Events import Events
import IN as __IN
IsServerUser = __IN.IsServerUser
""" 客户端常量: 是否为房主 """

clientApi = __extraClientApi # type: extraClientApi

TickEvent = "OnScriptTickClient"
System = clientApi.GetSystem("Minecraft","game") # type: extraClientApi
EnSp,EnSy = clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName() # 获取事件引擎
__EveLis = []; __AppendEveLis = __EveLis.append # 记录监听的事件
levelId = clientApi.GetLevelId(); playerId = clientApi.GetLocalPlayerId() 
TemporaryContainer = type("TemporaryContainer",(object,),{}); SYSTEMDIC = {} # 记录系统


def setSystem(module, systemName=None):
    """ 设置系统 用于注册流程 """
    if systemName == None:
        from uuid import uuid4
        systemName = str(uuid4()).replace("-","")
    SYSTEMDIC[systemName] = module


def Request(Key, Args=tuple(), Kwargs={}, OnResponse=lambda *_: None):
    # type: (str, tuple, dict, object) -> bool
    ''' Request 向服务端发送请求, 与Call不同的是,这是双向的,可以取得返回值 '''
    from Util import RandomUid
    BackKey = RandomUid()
    Dic = getattr(System,CallDict)
    def BackFun(*Args, **Kwargs):
        del Dic[BackKey]
        return OnResponse(*Args, **Kwargs)
    if isinstance(Dic,dict):
        Dic[BackKey] = BackFun
    Call('__Client.Request__', playerId, Key, Args, Kwargs, BackKey)
    return True

def CallOTClient(PlayerId, Key, *Args, **Kwargs):
    ''' Call其他玩家的客户端 如: 发起组队申请 '''
    Call('__CALL.CLIENT__', PlayerId, Key, Args, Kwargs)
    return True

def ListenForEvent(EventName, ParentObject=None, Function=lambda:None):
    # type: (str, object, object) -> bool
    '''
            注册事件监听 (事件名, 父对象, 函数|方法|可执行对象)
    '''
    EventName = EventName if isinstance(EventName, str) else EventName.__name__
    FunctionName = Function.__name__
    if not ParentObject:
        ParentObject = TemporaryContainer()
        setattr(ParentObject, FunctionName, Function)
    System.ListenForEvent(EnSp,EnSy,EventName,ParentObject,Function)
    return True

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

def Destroy():
    __OnEnd() # 反注销监听

def CLI_SYSTEM_APPEND(SystemName, Obj):
    SYSTEMDIC[SystemName] = Obj

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
    Fun(*Args, **Kwargs)

TC = TemporaryContainer()
setattr(TC,__OnCall.__name__,__OnCall)
System.ListenForEvent("Minecraft","game",CallDict,TC,__OnCall)

# -- 在系统端中建立监听事件完成交互的实现 --

# 触发指定服务端函数
def Call(Key, *Args, **Kwargs):
    ''' 
            用于 服务端与客户端(反之同理) 的交互
            需要在被调用的函数上使用CallBackKey|AllowCall装饰器
            Call方法用于调用对立端的指定函数
            如 Call("Test", ....)
            第一个参数为Key值,随后任意参数量 依函数形参量决定
            
            /** 注意事项: Call方法只调用对方端的函数,不调用本端函数 **/
    '''
    Data = {"Key":Key,"Args":Args,"Kwargs":Kwargs}
    System.NotifyToServer(CallDict, Data)


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
            允许调用（跨端交互），同等于CallBackKey区别是自动以当前函数名字设置参数，无需手动配置
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

class EntityCompCls(object):
    ''' QuMod提供的实体组件类 开发者可以继承并开发实体组件功能'''
    # UserList 用作记录使用者Id,防止同组件复用现象
    UserList = {} # type: dict[str,EntityCompCls]
    @classmethod
    def GetComp(cls, entityId):
        # type: (str) -> EntityCompCls|None
        ''' 
                [静态方法] 获取指定实体的组件实例
                直接调用 cls.GetComp(xxx) 即可
                cls表示类 而不是 实例化的数据对象
        '''
        try:
            return cls.UserList[entityId]
        except Exception:
            return None
        
    def __new__(cls, entityId, *Args, **Kwargs):
        if entityId in cls.UserList:
            return None
        Obj = object.__new__(cls, entityId, *Args, **Kwargs)
        cls.UserList[entityId] = Obj
        Obj.entityId = entityId
        System.ListenForEvent(EnSp, EnSy, 'OnScriptTickClient', Obj, Obj.OnTick)
        System.ListenForEvent(EnSp, EnSy, 'RemoveEntityClientEvent', Obj, Obj.WhenEntityRemove)
        return Obj
    
    def __init__(self,entityId):
        ''' [可覆写] 初始化 需要确保第一个参数为实体id '''
        self.entityId = entityId

    def OnRemove(self):
        ''' [可覆写] 组件移除后自动执行 '''
        pass
    
    def OnTick(self,Args={}):
        ''' [可覆写] Tick 一秒30次 如有需要可以覆写此方法 '''
        pass
    
    def RemoveComp(self):
        ''' 删除组件方法,可以手动调用 生物死亡后也会自动调用 '''
        try:
            del self.__class__.UserList[self.entityId]
            System.UnListenForEvent(EnSp, EnSy, 'OnScriptTickClient', self, self.OnTick)
            System.UnListenForEvent(EnSp, EnSy, 'RemoveEntityClientEvent', self, self.WhenEntityRemove)
            self.OnRemove()
        except Exception:
            pass

    def WhenEntityRemove(self, Args):
        '''
                判断被Remove的实体是否为自己
                并调用 OnRemove 方法 进行回收处理
        '''
        if Args["id"] == self.entityId:
            self.RemoveComp()

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

class __PublicData: # 该 class存在异常问题, 现已临时停用
    @classmethod
    def Receive(cls,Name="Default"):
        ''' 
                接收信息 默认参数 (Name="Default")
                PS: 你可以在你的类中添加静态方法: UpDate, 在数据更新时自动回调 (无参数)
        '''
        def Decorator(Clss):
            KeyName = "__%s.%s__"%(cls.__name__, Name)
            def UpDate_(Dic):
                for k,v in Dic.items():
                    setattr(Clss, k, v)
                if hasattr(Clss,"UpDate"):
                    Clss.UpDate()
            CallBackKey(KeyName)(UpDate_)
            return Clss
        return Decorator


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
        @property
        def Value(self):
            # type: () -> int
            comp = clientApi.GetEngineCompFactory().CreateAttr(self.entityId)
            return comp.GetAttrValue(0)
        @property
        def Max(self):
            # type: () -> int
            comp = clientApi.GetEngineCompFactory().CreateAttr(self.entityId)
            return comp.GetAttrMaxValue(0)
        

    def __init__(self, entityId):
        # type: (str) -> None
        self.entityId = entityId
        self.PropertySettingsDic = {
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
        return clientApi.GetEngineCompFactory().CreatePos(self.entityId).GetPos()

    @property
    def FootPos(self):
        # type: () -> tuple[float,float,float]
        return clientApi.GetEngineCompFactory().CreatePos(self.entityId).GetFootPos()

    @property
    def Rot(self):
        # type: () -> tuple[float,float]
        return clientApi.GetEngineCompFactory().CreateRot(self.entityId).GetRot()
    
    @property
    def DirFromRot(self):
        # type: () -> tuple[float,float,float]
        return clientApi.GetDirFromRot(self.Rot)

    @property
    def Identifier(self):
        # type: () -> str
        return clientApi.GetEngineCompFactory().CreateEngineType(self.entityId).GetEngineTypeStr()
    
    def GetMoLang(self, Query):
        # type: (str) -> float
        ''' 获取 实体节点(仅支持原版Molang) '''
        comp = clientApi.GetEngineCompFactory().CreateQueryVariable(self.entityId)
        return comp.GetMolangValue(Query)
    
    def GetQuery(self, Query):
        # type: (str) -> float
        ''' 获取实体Query节点 支持原版Molang和自定义Query '''
        if Query.lower().startswith("query.mod."):
            return clientApi.GetEngineCompFactory().CreateQueryVariable(self.entityId).Get(Query)
        else:
            return self.GetMoLang(Query)
    
    def SetQuery(self, Query, Value):
        # type: (str,float) -> bool
        ''' 设置实体Query节点 仅支持自定义Query '''
        comp = clientApi.GetEngineCompFactory().CreateQueryVariable(self.entityId)
        return comp.Set(Query, Value)


# ---- QuMod提供的一些基于原版API的组件 ----
@CallBackKey('__DelCallBackKey__')
def __DelCallBackKey(Key):
    Dic = getattr(System,CallDict)
    if Key in Dic: del Dic[Key]