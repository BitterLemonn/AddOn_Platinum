# -*- coding: utf-8 -*-
from functools import wraps
from threading import Thread,Lock
from Information import Version
from types import FunctionType

def import_module(*args):
    """ [已废弃] 导入模块 """
    return {}

class UniversalObject(object):
    """ 万用对象 """
    def __init__(self):
        pass

    def __getattribute__(self, __name):
        print("{}: GET {}".format(str(self), str(__name)))
        return self

    def __call__(self, *args, **kwds):
        print("{}: {} {}".format(str(self), str(args), str(kwds)))
        return self

class EventsData(object):
    """ 事件Data """
    def __init__(self, json):
        self._quJson = json

    def __getattribute__(self, __name):
        return object.__getattribute__(self, "_quJson")[__name]

class EventsRedirect(object):
    """ 事件重定向 """
    def __getattribute__(self, __name):
        return type(__name, (EventsData,), {})
    
_eventsRedirect = EventsRedirect()

class SystemSide(object):
    def __init__(self, Path, SystemName = None):
        self.SystemName = SystemName # 绑定系统
        self.Path = Path

buil = UniversalObject()
ModDirName = "None"
GlobSpaceName = "QuModForMc"
CallDict = GlobSpaceName+"_DicForCall"
# 未知类 用于通过网易静态代码检测器 部分场景可代替None
Unknown = type("Unknown",(object,),{})
ThreadLock = Lock()

def ParameterType(*Args, **Kwargs):
    """ 函数类型校验装饰器 可以使用列表/元组代表多个类型 """
    def __ParameterType(Func):
        ArgsType = Args+tuple(Kwargs.values())
        KwargsType = Kwargs
        @wraps(Func)
        def newFun(*__Args, **__Kwargs):
            # Args参数类型校验
            for i, data in enumerate(__Args):
                if i>=len(ArgsType): continue       # 类型限制外 通过
                typ = ArgsType[i]
                TypeList = [typ] if not isinstance(typ, list) and not isinstance(typ, tuple) else typ
                if any((isinstance(data, Type) for Type in TypeList)):
                    continue                        # 符合其中的任意类型 通过
                Error = "类型异常({name}) {data} 不是 {args}".format(name=Func.__name__, data=data,
                    args=TypeList[0] if len(TypeList) == 1 else " | ".join((str(x) for x in TypeList))
                )
                raise TypeError(Error)
            # Kwargs参数类型校验
            for Key, Data in __Kwargs.items():
                if not Key in KwargsType: continue
                typ = KwargsType[Key]
                TypeList = [typ] if not isinstance(typ, list) and not isinstance(typ, tuple) else typ
                if any((isinstance(Data, Type) for Type in TypeList)):
                    continue                        # 符合其中的任意类型 通过
                Error = "类型异常({name}) {Key} = {data} 不是 {args}".format(
                    Key = Key,
                    name=Func.__name__, 
                    data=Data,
                    args=TypeList[0] if len(TypeList) == 1 else " | ".join((str(x) for x in TypeList))
                )
                raise TypeError(Error)
            return Func(*__Args, **__Kwargs)
        return newFun
    return __ParameterType

# 创建随机UID
def RandomUid():
    from uuid import uuid4
    return "QuMod_"+str(uuid4()).replace("-","")

@ParameterType(String = str)
def Base64(String = 'String'):
    """将string值进行加密"""
    from base64 import b64encode
    String = str(String)
    BasText = str(b64encode(String.encode()))
    if len(BasText) > 16:
        BasText = BasText[:16]
    return BasText

@ParameterType(Value = str)
def SetModDirName(Value=""):
    global ModDirName
    global GlobSpaceName
    global CallDict
    ModDirName = str(Value)
    GlobSpaceName = "QuMod_"+str(ModDirName)
    CallDict = GlobSpaceName+"_DicForCall"
SetModDirName()

@ParameterType(str, Value=object)
def SetModuleCache(Key, Value=buil):
    # from sys import modules
    # try:
    #     modules[Key] = Value
    # except Exception as e:
    #     print('[Error] '+str(e))
    #     return False
    # return True
    return False

@ParameterType(object, str, Value=object)
def SetModuleAttr(Module, Key, Value=buil):
    """ 设置模块Attr """
    try:
        setattr(import_module(Module), Key, Value)
    except Exception as e:
        print('[Error] '+str(e))
        return False
    return True

def ExceptionHandling(errorFun=lambda: None, output=False):
    """ 异常处理装饰器 当函数抛出异常时将会返回预定值 """
    def exceptionHandling(func):
        @wraps(func)
        def newFun(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if output:
                    print("[Error]: 异常捕获 {}".format(str(e)))
                return errorFun()
        return newFun
    return exceptionHandling

def IsThread(Fun):
    """ [装饰器] 是多线程的 @IsThread 使得该函数在独立新线程工作 """
    @wraps(Fun)
    def newFun(*Args,**Kwargs):
        Xc = Thread(target=Fun,args=tuple(Args),kwargs=dict(Kwargs)); Xc.start()
        return Xc
    return newFun

def InitOperation(fun):
    """ 初始化运行 装饰器 @InitOperation 函数将会自动执行一次 不支持传参 """
    try:
        fun()
    except Exception as e:
        print("[Error] " + str(e))
    return fun

def PyCompile(*Args, **Kwagrs):
    return buil.compile(*Args, **Kwagrs)


def NewFun(String, Globals={}, FunctionName = "Function"):
    # type: (str, dict, str) -> FunctionType
    """ 
        [已废弃] 动态创建一个函数, 如: 
            NewFun('''
                Define (Args):
                    print(666)
            ''', globals())
    """
    Key = 'Define' #  关键词
    Indent = 0   # 缩进级
    NewStrCo = []; Append = NewStrCo.append;  # 存储新字符串
    for Line in String.split('\n'):
        if Line.count(Key) == 1:
            Indent = Line.find(Key)
            Line = Line.replace(Key, 'def '+FunctionName, 1)
        Append(Line[Indent:])
    CodeStr = '\n'.join(NewStrCo)
    Code = PyCompile(CodeStr,'','exec')
    Function = FunctionType(Code.co_consts[0], Globals)
    return Function


class Math:
    """ QuMod提供的数学运算类 """
    @staticmethod
    def pointDistance(point1, point2):
        # type: (tuple, tuple) -> float
        """ 两点距离计算 """
        x1, y1, z1 = point1
        x2, y2, z2 = point2
        result = ((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)**0.5
        return result

    @staticmethod
    def getUnitVector(vector):
        # type: (tuple[int|float]) -> tuple[int|float]
        """ 获取向量的单位向量 """
        length = (sum(i ** 2 for i in vector))**0.5
        if length == 0:
            return vector
        unitVector = tuple((i / length) for i in vector)
        return unitVector

class ObjectConversion:
    """ 对象转换工具类 By Zero123
        此工具类用于解决自定义数据对象的序列化与反序列化加载 用于持久化储存数据/传输数据
    """

    baseType = set([
        "str", "list", "float", "int", "bool", "dict", "unicode"
    ])

    _typeKey = "__type__"
    _valueKey = "__value__"

    @staticmethod
    def getClsPathWithClass(clsObj):
        return clsObj.__module__ + "." + clsObj.__name__

    @staticmethod
    def getClsWithPath(path):
        # type: (str) -> object
        lastPos = path.rfind(".")
        impObj = import_module(path[:lastPos])
        return getattr(impObj, path[lastPos+1:])

    @staticmethod
    def getClsPath(data):
        return data.__class__.__module__ + "." + data.__class__.__name__

    @staticmethod
    def dumpsObject(data):
        # type: (object) -> dict
        """ 序列化对象 """
        if data == None:
            return data
        elif type(data).__name__ in ObjectConversion.baseType:
            if isinstance(data, list):
                return [ObjectConversion.dumpsObject(v) for v in data]
            elif isinstance(data, dict):
                return {str(k):ObjectConversion.dumpsObject(v) for k, v in data.items()}
            return data
        value = {
            k: ObjectConversion.dumpsObject(getattr(data, k))
            for k in dir(data) if not k.startswith("__") and not hasattr(getattr(data, k), "__call__")
        }
        return {
            ObjectConversion._typeKey: ObjectConversion.getClsPath(data),
            ObjectConversion._valueKey: value
        }

    @staticmethod
    def getType(data):
        # type: (object) -> str | None
        if data == None:
            return None
        if isinstance(data, dict) and ObjectConversion._typeKey in data and ObjectConversion._valueKey in data:
            return data[ObjectConversion._typeKey]
        return type(data).__name__

    @classmethod
    def loadDumpsObject(cls, data):
        # type: (object) -> object | dict
        """ 加载序列化对象 (当类匹配失败/构造失败将会抛出异常) """
        dataType = cls.getType(data)
        if dataType == None:
            return None
        if dataType in cls.baseType:
            # 原生数据类型
            if isinstance(data, list):
                return [cls.loadDumpsObject(v) for v in data]
            elif isinstance(data, dict):
                return {str(k):cls.loadDumpsObject(v) for k, v in data.items()}
            return data
        dataCls = cls.getClsWithPath(data[cls._typeKey])
        value = data[cls._valueKey]
        createKey = "create"
        if hasattr(dataCls, createKey):
            # 使用静态构造方法
            obj = getattr(dataCls, createKey)()
            for k, v in cls.loadDumpsObject(value).items():
                setattr(obj, k, v)
            return obj
        return dataCls(**cls.loadDumpsObject(value))

class QuFreeObject(object):
    def free(self):
        print("[Qu.FREE] 资源释放 {}".format(self))

def errorPrint(charPtr):
    """ 异常输出 """
    print("[Error] "+str(charPtr))