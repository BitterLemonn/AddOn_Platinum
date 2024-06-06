# -*- coding: utf-8 -*-
from uuid import uuid4
from ...IN import RuntimeService, ModDirName
from ...Util import errorPrint
import mod.server.extraServerApi as serverApi
ServerSystem = serverApi.GetServerSystemCls()

def serverImportModule(filePath):
    """ 服务端文件导入 """
    return serverApi.ImportModule(filePath)

class CallObjData:
    def __init__(self, callObj, args = tuple(), kwargs = {}):
        self.callObj = callObj
        self.args = args
        self.kwargs = kwargs
        self._uid = None

class LoaderSystem(ServerSystem):
    """ QuMod加载器系统
        加载器承担了系统文件的加载以及事件监听 系统通信
    """
    namespace = "Qu_" + ModDirName
    systemName = "loader_system_" + ModDirName

    @staticmethod
    def getSystem():
        # type: () -> LoaderSystem
        """ 获取加载器系统 如果未注册将会自动注册并返回 """
        system = serverApi.GetSystem(LoaderSystem.namespace, LoaderSystem.systemName)
        if system:
            return system
        return serverApi.RegisterSystem(LoaderSystem.namespace, LoaderSystem.systemName, LoaderSystem.__module__ + "." + LoaderSystem.__name__)

    def __init__(self, namespace, systemName):
        ServerSystem.__init__(self, namespace, systemName)
        self.namespace = namespace
        self.systemName = systemName
        self._systemList = RuntimeService._serviceSystemList[::]
        self._initState = False
        self._regInitState = False
        self._waitTime = 0.0
        self._callQueue = []    # type: list[CallObjData]
        self.systemInit()
    
    def getSystemList(self):
        # type: () -> list[tuple[str, str | None]]
        return self._systemList
    
    def removeCallObjByUid(self, _uid = ""):
        """ 尝试移除特定uid的callObj 如果存在 """
        for i, obj in enumerate(self._callQueue):
            if obj._uid == _uid:
                del self._callQueue[i]
                break
    
    def proxyRegister(self, funcObj):
        """ 代理注册 """
        from functools import wraps
        @wraps(funcObj)
        def newFun(*args, **kwargs):
            callObj = CallObjData(funcObj, args, kwargs)
            self._callQueue.append(callObj)
            return callObj
        return newFun

    def unsafeUpdate(self, callObjData):
        # type: (CallObjData) -> bool
        """ 不安全的强制刷新 """
        if callObjData in self._callQueue:
            self._callQueue.remove(callObjData)
            callObjData.callObj(*callObjData.args, **callObjData.kwargs)
            return True
        return False

    def Update(self):
        self.regSystemInit()
        if len(self._callQueue) > 0:
            for obj in self._callQueue:
                try:
                    obj.callObj(*obj.args, **obj.kwargs)
                except Exception as e:
                    errorPrint("{} call执行异常 {}".format(obj.callObj, e))
                    import traceback
                    traceback.print_exc()
            self._callQueue = []
        return ServerSystem.Update(self)

    def systemInit(self):
        self._initState = True

    def regSystemInit(self):
        """ 系统信息注册初始化 """
        if self._regInitState:
            return
        from ...Server import SER_SYSTEM_APPEND
        for path, systemName in self._systemList:
            sysObj = None
            try:
                sysObj = serverImportModule(path)
                if sysObj == None:
                    errorPrint("[服务端] 系统文件加载失败(API异常): {}".format(path))
                    continue
            except Exception as e:
                errorPrint("[服务端] 系统文件错误: {} ({})".format(path, e))
                import traceback
                traceback.print_exc()
                continue
            if not systemName: systemName = str(uuid4()).replace("-","")
            SER_SYSTEM_APPEND(systemName, sysObj)
        self._regInitState = True