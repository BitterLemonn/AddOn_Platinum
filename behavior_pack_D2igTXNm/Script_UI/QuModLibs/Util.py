# -*- coding: utf-8 -*-
from functools import wraps
from threading import Thread,Lock
from Information import Version
from types import FunctionType

def import_module(*args):
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
    

buil = UniversalObject()
ModDirName = "None"
GlobSpaceName = "QuModForMc"
CallDict = GlobSpaceName+"_DicForCall"
# 未知类 用于通过网易静态代码检测器 部分场景可代替None
Unknown = type("Unknown",(object,),{}); ThreadLock = Lock()

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
    ''' 设置模块缓存 '''
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
    ''' 设置模块Attr '''
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
    ''' [装饰器] 是多线程的 @IsThread 使得该函数在独立新线程工作 '''
    @wraps(Fun)
    def newFun(*Args,**Kwargs):
        Xc = Thread(target=Fun,args=tuple(Args),kwargs=dict(Kwargs)); Xc.start()
        return Xc
    return newFun

def PyCompile(*Args, **Kwagrs):
    return buil.compile(*Args, **Kwagrs)


def NewFun(String, Globals={}, FunctionName = "Function"):
    # type: (str, dict, str) -> FunctionType
    ''' 
            动态创建一个函数, 如: 
            NewFun("""
                Define (Args):
                    print(666)
            """, globals())
    '''
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