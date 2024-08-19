# -*- coding: utf-8 -*-
# 客户端端基本功能模块 为减缓IO开销 常用的功能均放置在该文件 其他功能按需导入使用
from Math import Vec3, Vec2
from functools import wraps
if 1 > 2:
    # 阻止补全库被真正import降低运行时开销
    import QuClientApi.extraClientApi as extraClientApi
    from QuClientApi.Events import Events as _EventsPrompt
from Util import GlobSpaceName, CallDict, ModDirName, errorPrint
from Util import Unknown, import_module, NewFun, InitOperation, _eventsRedirect
from Util import ObjectConversion as __ObjectConversion
import mod.client.extraClientApi as __extraClientApi
import IN as __IN
IsServerUser = __IN.IsServerUser
""" 客户端常量: 是否为房主 """
clientApi = __extraClientApi # type: extraClientApi
TickEvent = "OnScriptTickClient"
System = clientApi.GetSystem("Minecraft","game") # type: extraClientApi
EnSp,EnSy = clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName() # 获取事件引擎
__EveLis = []; __AppendEveLis = __EveLis.append # 记录监听的事件
levelId = clientApi.GetLevelId(); playerId = clientApi.GetLocalPlayerId() 
SYSTEMDIC = {} # 记录系统
Events = _eventsRedirect    # type: type[_EventsPrompt]

def creatTemporaryContainer():
    return type("TemporaryContainer",(object,),{})()

def _getLoaderSystem():
    """ 获取加载器系统 """
    from Systems.Loader.Client import LoaderSystem
    return LoaderSystem.getSystem()

_loaderSystem = _getLoaderSystem()

def TemporaryContainer():
    return _getLoaderSystem()

def setSystem(module, systemName=None):
    """ 设置系统 用于注册流程 """
    if systemName == None:
        from uuid import uuid4
        systemName = str(uuid4()).replace("-","")
    SYSTEMDIC[systemName] = module

def Request(Key, Args=tuple(), Kwargs={}, OnResponse=lambda *_: None):
    # type: (str, tuple, dict, object) -> bool
    """ Request 向服务端发送请求, 与Call不同的是,这是双向的,可以取得返回值 """
    from Util import RandomUid
    BackKey = RandomUid()
    Dic = getattr(_loaderSystem,CallDict)
    def BackFun(*Args, **Kwargs):
        del Dic[BackKey]
        return OnResponse(*Args, **Kwargs)
    if isinstance(Dic,dict):
        Dic[BackKey] = BackFun
    Call('__Client.Request__', playerId, Key, Args, Kwargs, BackKey)
    return True

def CallOTClient(PlayerId, Key, *Args, **Kwargs):
    """ Call其他玩家的客户端 如: 发起组队申请 """
    Call('__CALL.CLIENT__', PlayerId, Key, Args, Kwargs)
    return True

def ListenForEvent(EventName, ParentObject=None, Function=lambda:None):
    # type: (str, object, object) -> object
    """
        注册事件监听 (事件名, 父对象, 函数|方法|可执行对象)
    """
    EventName = EventName if isinstance(EventName, str) else EventName.__name__
    FunctionName = Function.__name__
    if not ParentObject:
        ParentObject = TemporaryContainer()
    newFuncName = "ListenForEvent_{}_{}".format(id(ParentObject), FunctionName)
    newFunc = lambda *args, **kwargs: Function(*args, **kwargs)
    newFunc.__name__ = newFuncName
    lSystem = _getLoaderSystem()
    @_loaderSystem.proxyRegister
    def Reg():
        setattr(lSystem, newFuncName, newFunc)
        lSystem.ListenForEvent(EnSp,EnSy,EventName,lSystem,getattr(lSystem, newFuncName))
        return Unknown
    regObj = Reg()
    regObj._uid = newFuncName
    return regObj

def UnListenForEvent(EventName, ParentObject=None, Function=lambda:None):
    # type: (str, object, object) -> bool
    """
        反注册事件监听 (事件名, 父对象, 函数|方法|可执行对象)
    """
    EventName = EventName if isinstance(EventName, str) else EventName.__name__
    FunctionName = Function.__name__
    if not ParentObject:
        ParentObject = TemporaryContainer()
    newFuncName = "ListenForEvent_{}_{}".format(id(ParentObject), FunctionName)
    lSystem = _getLoaderSystem()
    if hasattr(lSystem, newFuncName):
        lSystem.UnListenForEvent(EnSp,EnSy,EventName,lSystem,getattr(lSystem, newFuncName))
        delattr(lSystem, newFuncName)
    else:
        lSystem.removeCallObjByUid(newFuncName)
    return True

def Destroy():
    __OnEnd() # 反注销监听
    QuDataStorage.saveData()

def CLI_SYSTEM_APPEND(SystemName, Obj):
    SYSTEMDIC[SystemName] = Obj

# 获取本地创建的系统端
def GetSystem(SystemName):
    """ 
        获取本地创建的系统端,EasyMod(..).Server|Client(Path,SystemName="")
        需在创建服务|客户端时分配系统名
    """
    return SYSTEMDIC.get(SystemName)

# 监听事件
def Listen(__Event):
    """ 
        [装饰器] @Listen(事件名)
        用于监听游戏事件 游戏结束后自动回收 (以函数名称作为存储键位 多个同类监听请修改函数名称区分)
    """
    LSystem = _getLoaderSystem()
    Event = __Event if isinstance(__Event, str) else __Event.__name__
    def SetListen(Fun):
        # 判断先前有无注册过同函数的同事件监听
        NowPath = Fun.__module__+"."+Fun.__name__
        for LEvent, LFun, LTc, Path in __EveLis:
            if Path == NowPath:
                LSystem.UnListenForEvent(EnSp,EnSy,Event,LTc,LFun)
                __EveLis.remove((LEvent, LFun, LTc, Path))
                print("[%s] 热重载监听: %s"%(Event, NowPath))
                break
        @_loaderSystem.proxyRegister
        def setListen():
            TC = TemporaryContainer()
            setattr(TC,Fun.__name__,Fun)
            __AppendEveLis((Event,Fun,TC, NowPath))
            LSystem.ListenForEvent(EnSp,EnSy,Event,TC,getattr(LSystem, Fun.__name__))
        setListen()
        return Fun
    return SetListen

# 该系统端结束时触发
def __OnEnd():
    LSystem = _getLoaderSystem()
    for Event, Fun, TC, _ in __EveLis:
        LSystem.UnListenForEvent(EnSp,EnSy,Event,TC,Fun)

# -- 在系统端中建立监听事件完成交互的实现 --
if not hasattr(_loaderSystem,GlobSpaceName):
    setattr(_loaderSystem, GlobSpaceName, True)
    setattr(_loaderSystem, CallDict, {})

# Call的回调处理
def __OnCall(args):
    Key = args["Key"]
    Args = args["Args"]
    Kwargs = args["Kwargs"]
    Dic = getattr(_loaderSystem, CallDict)
    Fun = Dic.get(Key, None)
    if not Fun:
        if not (Key.startswith("__") and Key.endswith("__")):
            print("[Error]: '%s' 无效的请求,请检查是否遗漏相关装饰注册"%(Key))
        return None
    try:
        Fun(*Args, **Kwargs)
    except Exception:
        import traceback
        traceback.print_exc()

TC = TemporaryContainer()
setattr(TC,__OnCall.__name__,__OnCall)
System.ListenForEvent(_loaderSystem.namespace, _loaderSystem.systemName,
    CallDict, TC, getattr(TC, __OnCall.__name__)
)

# -- 在系统端中建立监听事件完成交互的实现 --

# 触发指定服务端函数
def Call(Key, *Args, **Kwargs):
    """ 
        向指服务端发起通信 执行特定的功能
    """
    Data = {"Key":Key,"Args":Args,"Kwargs":Kwargs}
    _loaderSystem.NotifyToServer(CallDict, Data)

# 设置回调键用的装饰器
def CallBackKey(Key):
    """ [装饰器] 用于给指定函数标记任意key值 以便被Call索引 """
    def Set(Fun):
        Dic = getattr(_loaderSystem,CallDict)
        if isinstance(Dic,dict):
            Dic[Key] = Fun
        return Fun
    return Set
 
def AllowCall(Fun):
    """ 允许调用 同等于CallBackKey 自动以当前函数名字设置参数 """
    Key=Fun.__name__
    Key2=Fun.__module__+"."+Key
    Key3 = Key2.split(ModDirName+".",1)[1]
    Dic = getattr(_loaderSystem,CallDict)
    if isinstance(Dic,dict):
        Dic[Key] = Fun
        Dic[Key2] = Fun
        Dic[Key3] = Fun
    return Fun

def LocalCall(Fun,*Args,**Kwargs):
    """ 本地调用 执行当前端@AllowCall|@CallBackKey("...")的方法 """
    Dic = getattr(_loaderSystem,CallDict)
    if isinstance(Dic,dict):
        return Dic[Fun](*Args,**Kwargs)

class EntityCompCls(object):
    """ QuMod提供的实体组件类 开发者可以继承并开发实体组件功能"""
    # UserList 用作记录使用者Id,防止同组件复用现象
    UserList = {} # type: dict[str,EntityCompCls]
    @classmethod
    def GetComp(cls, entityId):
        # type: (str) -> EntityCompCls|None
        """ 
                [静态方法] 获取指定实体的组件实例
                直接调用 cls.GetComp(xxx) 即可
                cls表示类 而不是 实例化的数据对象
        """
        if cls.UserList is EntityCompCls.UserList:
            cls.UserList = {}
        try:
            return cls.UserList[entityId]
        except Exception:
            return None
        
    def __new__(cls, entityId, *Args, **Kwargs):
        if cls.UserList is EntityCompCls.UserList:
            cls.UserList = {}
        if entityId in cls.UserList:
            return None
        Obj = object.__new__(cls, entityId, *Args, **Kwargs)
        cls.UserList[entityId] = Obj
        Obj.entityId = entityId
        ListenForEvent("OnScriptTickClient", Obj, Obj.OnTick)
        ListenForEvent("RemoveEntityClientEvent", Obj, Obj.WhenEntityRemove)
        return Obj
    
    def __init__(self,entityId):
        """ [可覆写] 初始化 需要确保第一个参数为实体id """
        self.entityId = entityId

    def OnRemove(self):
        """ [可覆写] 组件移除后自动执行 """
        pass
    
    def OnTick(self,Args={}):
        """ [可覆写] Tick 一秒30次 如有需要可以覆写此方法 """
        pass
    
    def RemoveComp(self):
        """ 删除组件方法,可以手动调用 生物死亡后也会自动调用 """
        try:
            del self.__class__.UserList[self.entityId]
            UnListenForEvent("OnScriptTickClient", self, self.OnTick)
            UnListenForEvent("RemoveEntityClientEvent", self, self.WhenEntityRemove)
            self.OnRemove()
        except Exception:
            pass

    def WhenEntityRemove(self, Args):
        """
                判断被Remove的实体是否为自己
                并调用 OnRemove 方法 进行回收处理
        """
        if Args["id"] == self.entityId:
            self.RemoveComp()


class EasyThread:
    """ QuMod提供的简易多线程 """
    from Util import ThreadLock
    @classmethod
    def IsThread(cls, *Args, **Kwargs):
        """ 用于将函数装饰为多线程下执行的函数 @IsThread 无参数"""
        from Util import IsThread
        return IsThread(*Args, **Kwargs)
    
    @classmethod
    def NextTick(cls, Fun, Args=tuple(), Kwargs={}, WaitReturn=False):
        """ 
                添加函数到下一游戏Tick运行 用于解决线程下无法使用API的现象
                选填参数 WaitReturn=False(默认值) 设置为True后将会等待返回结果后再执行后续代码
                Args=tuple(),Kwargs={} 可传参
        """
        cls.ThreadLock.acquire() # 上锁
        Back = []
        Obj = EasyThread()
        def Tick(_={}):
            UnListenForEvent(TickEvent, Obj, Tick)
            RunBack = Fun(*Args,**Kwargs)
            Back.append(RunBack)
            
        ListenForEvent(TickEvent, Obj, Tick)
        cls.ThreadLock.release() # 释放锁
        # 返回值处理
        if WaitReturn:
            while not len(Back):
                pass
            return Back[0]

class __PublicData: # 该 class存在异常问题, 现已临时停用
    @classmethod
    def Receive(cls,Name="Default"):
        """ 
                接收信息 默认参数 (Name="Default")
                PS: 你可以在你的类中添加静态方法: UpDate, 在数据更新时自动回调 (无参数)
        """
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

    class Type:
        PLAYER = "minecraft:player"

    class HealthComp(object):
        """ 生命值组件 """
        def __init__(self,entityId):
            # type: (str) -> None
            self.entityId = entityId
            self.PropertySettingsDic = {
            }
        def __setattr__(self, Name, Value):
            """ 属性设置处理 """
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
        """ 属性设置处理 """
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
        """ 实体生命值属性 """
        Cls = self.__class__
        return Cls.HealthComp(self.entityId)
    
    @property
    def Pos(self):
        # type: () -> tuple[float,float,float] | None
        return clientApi.GetEngineCompFactory().CreatePos(self.entityId).GetPos()

    @property
    def Vec3Pos(self):
        # type: () -> Vec3 | None
        pos = self.Pos
        if pos == None:
            return None
        return Vec3.tupleToVec(pos)

    @property
    def Vec3FootPos(self):
        # type: () -> Vec3 | None
        pos = self.FootPos
        if pos == None:
            return None
        return Vec3.tupleToVec(pos)

    @property
    def FootPos(self):
        # type: () -> tuple[float,float,float] | None
        return clientApi.GetEngineCompFactory().CreatePos(self.entityId).GetFootPos()

    @property
    def Vec2Rot(self):
        # type: () -> Vec2 | None
        rot = self.Rot
        if rot == None:
            return None
        return Vec2.tupleToVec(rot)

    @property
    def Rot(self):
        # type: () -> tuple[float,float] | None
        return clientApi.GetEngineCompFactory().CreateRot(self.entityId).GetRot()
    
    @property
    def DirFromRot(self):
        # type: () -> tuple[float,float,float] | None
        return clientApi.GetDirFromRot(self.Rot)

    @property
    def Vec3DirFromRot(self):
        # type: () -> Vec3 | None
        rot = self.DirFromRot
        if round == None:
            return None
        return Vec3.tupleToVec(rot)

    @property
    def Identifier(self):
        # type: () -> str
        return clientApi.GetEngineCompFactory().CreateEngineType(self.entityId).GetEngineTypeStr()
    
    def GetMoLang(self, Query):
        # type: (str) -> float
        """ 获取 实体节点(仅支持原版Molang) """
        comp = clientApi.GetEngineCompFactory().CreateQueryVariable(self.entityId)
        return comp.GetMolangValue(Query)
    
    def GetQuery(self, Query):
        # type: (str) -> float
        """ 获取实体Query节点 支持原版Molang和自定义Query """
        if Query.lower().startswith("query.mod."):
            return clientApi.GetEngineCompFactory().CreateQueryVariable(self.entityId).Get(Query)
        else:
            return self.GetMoLang(Query)
    
    def SetQuery(self, Query, Value):
        # type: (str,float) -> bool
        """ 设置实体Query节点 仅支持自定义Query """
        comp = clientApi.GetEngineCompFactory().CreateQueryVariable(self.entityId)
        return comp.Set(Query, Value)


# ---- QuMod提供的一些基于原版API的组件 ----
@CallBackKey('__DelCallBackKey__')
def __DelCallBackKey(Key):
    Dic = getattr(System,CallDict)
    if Key in Dic: del Dic[Key]

class QuObjectConversion(__ObjectConversion):
    @staticmethod
    def getClsWithPath(path):
        # type: (str) -> object
        lastPos = path.rfind(".")
        impObj = clientApi.ImportModule((path[:lastPos]))
        return getattr(impObj, path[lastPos+1:])

class QuDataStorage:
    """ Qu数据储存管理 """
    _versionKey = "__version__"
    _dataKey = "__data__"
    _isGlobal = "__isGlobal__"
    _autoMap = {}   # type: dict[type, dict]

    @staticmethod
    def formatStrType(typ):
        # type: (str) -> str
        """ 格式化字符串类型 """
        if typ in ("float", "int"):
            return "number"
        elif typ in ("str", "unicode"):
            return "baseString"
        return typ

    @staticmethod
    def loadData(clsObj, data):
        # type: (type, dict) -> None
        """ 加载数据 """
        for k, v in data.items():
            try:
                newObj = QuObjectConversion.loadDumpsObject(v)
                oldType = QuDataStorage.formatStrType(QuObjectConversion.getType(getattr(clsObj, k)))
                newType = QuDataStorage.formatStrType(QuObjectConversion.getType(newObj))
                if oldType != newType:
                    print("[QuDataStorage] 新旧数据类型不一已被放弃 ('{}' != '{}')".format(newType, oldType))
                    continue
                setattr(clsObj, k, newObj)
            except Exception as e:
                print(e)
    
    @staticmethod
    def dumpsData(clsObj):
        # type: (type) -> dict
        """ 获取序列化数据 """
        return {
            k : QuObjectConversion.dumpsObject(getattr(clsObj, k)) for k in dir(clsObj) if not k.startswith("__")
        }

    @staticmethod
    def AutoSave(version = 1, isGlobal = False):
        """ 自动保存装饰器
            @version 版本控制 当版本号不同时将会抛弃当前存档数据该用新版数据 一般用于大型数据变动
            @isGlobal 是否为全局配置 False视为仅当前存档
        """
        def _autoSave(cls):
            path = QuObjectConversion.getClsPathWithClass(cls)
            comp = clientApi.GetEngineCompFactory().CreateConfigClient(clientApi.GetLevelId())
            configDict = comp.GetConfigData(path, isGlobal)
            if configDict == None:
                configDict = {}
            if configDict.get(QuDataStorage._versionKey, version) == version:
                QuDataStorage.loadData(cls, configDict.get(QuDataStorage._dataKey, {}))
            configDict[QuDataStorage._versionKey] = version
            configDict[QuDataStorage._isGlobal] = isGlobal
            if not path in QuDataStorage._autoMap:
                QuDataStorage._autoMap[path] = configDict
            return cls
        return _autoSave
    
    @staticmethod
    def saveData():
        """ 保存存档数据 """
        levelcomp = clientApi.GetEngineCompFactory().CreateConfigClient(levelId)
        for k, v in QuDataStorage._autoMap.items():
            try:
                cls = QuObjectConversion.getClsWithPath(k)
                v[QuDataStorage._dataKey] = QuDataStorage.dumpsData(cls)
                levelcomp.SetConfigData(k, v, v.get(QuDataStorage._isGlobal, False))
            except Exception as e:
                print(e)

@CallBackKey("__calls__")
def QUMOD_CLIENT_CALLS_(datLis):
    # type: (list[tuple]) -> None
    """ 内置的多callData处理请求 """
    for key, args, kwargs in datLis:
        try:
            LocalCall(key, *args, **kwargs)
        except Exception as e:
            errorPrint("CALL发生异常 KEY值 '{}' >> {}".format(key, e))
            import traceback
            traceback.print_exc()

def EventHandler(key):
    """ 注册EventHandler 可搭配QuPresteTool完成代码分析并建立关联(开源版本暂不支持此功能) """
    def _EventHandler(fun):
        return fun
    return _EventHandler

def Emit(eventHandler, *args, **kwargs):
    """ 发送消息 执行特定eventHandler(开源版本暂不支持此功能) """
    pass