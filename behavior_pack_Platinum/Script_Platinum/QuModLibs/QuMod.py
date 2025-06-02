# -*- coding: utf-8 -*-
from mod.common.mod import Mod
import mod.server.extraServerApi as serverApi
import mod.client.extraClientApi as clientApi
from Util import TRY_EXEC_FUN
import IN

class _TempData:
    """ modMain临时数据储存 包含了初始化注册的一些信息 """
    _nativePyServer = []
    _nativePyClient = []
    _serverInitCall = []
    _clientInitCall = []
    _threadAnalysis = False

class Include:
    ctRender_v2 = False
    """ CTRender v2 资源管理系统 """
    attackExtend = False
    """ AC战斗机制 链攻击系统(商务纠纷暂已屏蔽) """
    glRender = False
    """ GLRender 玩家资源渲染系统 """

@Mod.Binding(name = "QuMod_"+IN.ModDirName, version = "1.0.0")
class QMain(object):
    """ QuMod MAIN入口逻辑  """
    def __init__(self):
        pass

    @Mod.InitServer()
    def serverInit(self):
        # 服务端初始化
        from Systems.Loader.Server import LoaderSystem
        IN.IsServerUser = True
        self._loadServerInclude()
        self._regNativePyServer()
        self._loadServerInitFuncs()
        if _TempData._threadAnalysis:
            from threading import current_thread
            IN.RuntimeService._serverThreadID = current_thread().ident
        if IN.RuntimeService._serverSystemList or IN.RuntimeService._serverLoadBefore:
            LoaderSystem.getSystem()    # 初始化服务端加载器

    @Mod.InitClient()
    def clientInit(self):
        from Systems.Loader.Client import LoaderSystem
        IN.RuntimeService._envPlayerId = clientApi.GetLocalPlayerId()
        self._loadClientInclude()
        self._regNativePyClient()
        self._loadClientInitFuncs()
        if _TempData._threadAnalysis:
            from threading import current_thread
            IN.RuntimeService._clientThreadID = current_thread().ident
        if IN.RuntimeService._clientSystemList or IN.RuntimeService._clientLoadBefore:
            LoaderSystem.getSystem()    # 初始化客户端加载器

    def _loadServerInclude(self):
        """ 加载服务端Include扩展项 """
        quModLibsPath = IN.QuModLibsPath
        if Include.ctRender_v2:
            REG_SERVER_MODULE(quModLibsPath + ".Include.CT_Render.ServerApi")
        if Include.attackExtend:
            REG_SERVER_MODULE(quModLibsPath + ".Include.AttackExtend.Server")
        if Include.glRender:
            REG_SERVER_MODULE(quModLibsPath + ".Include.GL_Render.Server")

    def _loadClientInclude(self):
        """ 加载客户端Include扩展项 """
        quModLibsPath = IN.QuModLibsPath
        if Include.ctRender_v2:
            REG_CLIENT_MODULE(quModLibsPath + ".Include.CT_Render.ClientApi")
        if Include.attackExtend:
            REG_CLIENT_MODULE(quModLibsPath + ".Include.AttackExtend.Client")
        if Include.glRender:
            REG_CLIENT_MODULE(quModLibsPath + ".Include.GL_Render.Client")

    def _regNativePyClient(self):
        """ 加载原版Python客户端系统注册 """
        for args in _TempData._nativePyClient:
            clientApi.RegisterSystem(*args)
        _TempData._nativePyClient = []

    def _regNativePyServer(self):
        """ 加载原版Python服务端系统注册 """
        for args in _TempData._nativePyServer:
            serverApi.RegisterSystem(*args)
        _TempData._nativePyServer = []

    def _loadServerInitFuncs(self):
        """ 加载服务端初始化函数 """
        for funObj in _TempData._serverInitCall:
            TRY_EXEC_FUN(funObj)
        _TempData._serverInitCall = []

    def _loadClientInitFuncs(self):
        """ 加载客户端初始化函数 """
        for funObj in _TempData._clientInitCall:
            TRY_EXEC_FUN(funObj)
        _TempData._clientInitCall = []

    @Mod.DestroyServer()
    def serverDestroy(self):
        pass

    @Mod.DestroyClient()
    def clientDestroy(self):
        pass

class EasyMod:
    """ 简易Mod构造器 """
    def __init__(self, modDirName=None):
        # type: (str | None) -> None
        self._modDirName = modDirName if modDirName else IN.ModDirName
        """ Mod目录名 """
        self.include = Include

    def regServer(self, relPath="", systemName=None):
        # type: (str, str | None) -> EasyMod
        """ 注册服务端(相对目录) """
        REG_SERVER_MODULE("{}.{}".format(self._modDirName, relPath), systemName)
        return self

    def Server(self, relPath="", systemName=None):
        # type: (str, str | None) -> EasyMod
        """ 便捷式服务端注册 """
        return self.regServer(relPath, systemName)

    def Client(self, relPath="", systemName=None):
        # type: (str, str | None) -> EasyMod
        """ 便捷式客户端注册 """
        return self.regClient(relPath, systemName)

    def regClient(self, relPath="", systemName=None):
        # type: (str, str | None) -> EasyMod
        """ 注册客户端(相对目录) """
        REG_CLIENT_MODULE("{}.{}".format(self._modDirName, relPath), systemName)
        return self

    def addServerInitCallFunc(self, callFunc=lambda: None):
        # type: (object) -> EasyMod
        """ 添加服务端初始化调用方法 """
        REG_SERVER_INIT_CALL(callFunc)
        return self
    
    def addClientInitCallFunc(self, callFunc=lambda: None):
        # type: (object) -> EasyMod
        """ 添加客户端初始化调用方法 """
        REG_CLIENT_INIT_CALL(callFunc)
        return self

    def regNativePyClient(self, namespace="", systemName="", relPath=""):
        # type: (str, str, str) -> EasyMod
        """ 注册原生Python客户端(相对目录) """
        CLIENT_REG_NATIVE_PY_SYSTEM(namespace, systemName, "{}.{}".format(self._modDirName, relPath))
        return self

    def regNativePyServer(self, namespace="", systemName="", relPath=""):
        # type: (str, str, str) -> EasyMod
        """ 注册原生Python服务端(相对目录) """
        SERVER_REG_NATIVE_PY_SYSTEM(namespace, systemName, "{}.{}".format(self._modDirName, relPath))
        return self

def START_THREAD_ANALYSIS():
    """ 启用线程分析 """
    _TempData._threadAnalysis = True

def STOP_THREAD_ANALYSIS():
    """ 禁用线程分析 """
    _TempData._threadAnalysis = False

def REG_SERVER_MODULE(absPath, systemName=None, _index=-1):
    # type: (str, str | None, int) -> None
    """ 注册服务端模块 (绝对路径) """
    if _index < 0:
        return IN.RuntimeService._serverSystemList.append((absPath, systemName))
    return IN.RuntimeService._serverSystemList.insert(_index, (absPath, systemName))

def REG_CLIENT_MODULE(absPath, systemName=None, _index=-1):
    # type: (str, str | None, int) -> None
    """ 注册客户端模块 (绝对路径) """
    if _index < 0:
        return IN.RuntimeService._clientSystemList.append((absPath, systemName))
    return IN.RuntimeService._clientSystemList.insert(_index, (absPath, systemName))

def REG_SERVER_INIT_CALL(func=lambda: None):
    # type: (function) -> function
    """ 注册服务端初始化调用函数 """
    _TempData._serverInitCall.append(func)
    return func

def REG_CLIENT_INIT_CALL(func=lambda: None):
    # type: (function) -> function
    """ 注册客户端初始化调用函数 """
    _TempData._clientInitCall.append(func)
    return func

def PRE_SERVER_LOADER_HOOK(func=lambda: None):
    # type: (function) -> function
    """ 注册服务端加载器处理前的前置逻辑 (此时依然可以注册文件 该功能用于前置关联的校验处理) """
    IN.RuntimeService._serverLoadBefore.append(func)
    return func

def PRE_CLIENT_LOADER_HOOK(func=lambda: None):
    # type: (function) -> function
    """ 注册客户端加载器处理前的前置逻辑 (此时依然可以注册文件 该功能用于前置关联的校验处理) """
    IN.RuntimeService._clientLoadBefore.append(func)
    return func

def SET_MOD_NAME(_name):
    # type: (str) -> None
    """ 设置modName """
    setattr(QMain, "MOD_NAME", _name)

def SET_MOD_VERSION(_version):
    # type: (str) -> None
    """ 设置modVersion """
    setattr(QMain, "VERSION", _version)

def SERVER_REG_NATIVE_PY_SYSTEM(namespace="", systemName="", absPath=""):
    """ 注册服务端原生Python System """
    _TempData._nativePyServer.append((namespace, systemName, absPath))

def CLIENT_REG_NATIVE_PY_SYSTEM(namespace="", systemName="", absPath=""):
    """ 注册客户端原生Python System """
    _TempData._nativePyClient.append((namespace, systemName, absPath))