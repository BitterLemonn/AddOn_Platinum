# -*- coding: utf-8 -*-
from mod.common.mod import Mod
import mod.server.extraServerApi as serverApi
import mod.client.extraClientApi as clientApi
import traceback
from Util import SetModDirName, import_module, SystemSide
from uuid import uuid4
import IN

RandomKey = "Q"+str(uuid4()).replace("-","") # 随机钥匙

EasyModSl = [None,[],[]] # 记录实例
ModDirName = IN.ModDirName
QuModLibsPath = IN.QuModLibsPath

@Mod.Binding(name = "QuMod_"+ModDirName, version = "1.0.0")
class QUMOD_MOD_MAIN(object):
    """ 用于自动化注册Mod信息  """
    def __init__(self):
        pass

    @Mod.InitServer()
    def ServerInit(self):
        # 服务端初始化
        from Systems.Loader.Server import LoaderSystem
        IN.IsServerUser = True
        this = EasyModSl[0]         # type: EasyMod
        ServerLis = EasyModSl[1]    # type: list[SystemSide]
        this.include._insertServerList(ServerLis)
        sysPathList = []
        for _data in ServerLis:
            sysPathList.append((this.FormatPath(_data.Path), _data.SystemName))
        IN.RuntimeService._serviceSystemList = sysPathList
        if len(sysPathList) > 0:
            LoaderSystem.getSystem()
        # / =========== 自定义Function执行 ===========
        for func in this.ServerFunc:
            try:
                func()
            except Exception:
                traceback.print_exc()
        if not this: return None
        this.OnServerInit()
        # =========== 自定义Function执行 =========== /

    @Mod.DestroyServer()
    def ServerDestroy(self):
        # 服务端销毁时
        this = EasyModSl[0]
        if not this:
            return None
        from Server import SYSTEMDIC, Destroy
        Destroy() # 销毁处理方法
        for Name, Obj in SYSTEMDIC.items():
            try:
                if hasattr(Obj, "QuDestroy"):
                    Obj.QuDestroy()
                del SYSTEMDIC[Name]
            except Exception:
                traceback.print_exc()

    @Mod.InitClient()
    def ClientInit(self):
        # 客户端初始化
        from Systems.Loader.Client import LoaderSystem
        this = EasyModSl[0]         # type: EasyMod
        ClientLis = EasyModSl[2]    # type: list[SystemSide]
        this.include._insertClientList(ClientLis)
        sysPathList = []
        for _data in ClientLis:
            sysPathList.append((this.FormatPath(_data.Path), _data.SystemName))
        IN.RuntimeService._clientSystemList = sysPathList
        if len(sysPathList) > 0:
            LoaderSystem.getSystem()
        # / =========== 自定义Function执行 ===========
        for func in this.ClientFunc:
            try:
                func()
            except Exception:
                traceback.print_exc()
        if not this: return None
        this.OnClientInit()
        # =========== 自定义Function执行 =========== /

    @Mod.DestroyClient()
    def ClientDestroy(self):
        # 客户端销毁时
        this = EasyModSl[0]
        if not this:
            return None
        from Client import SYSTEMDIC, Destroy
        Destroy() # 销毁处理方法
        for Name, Obj in SYSTEMDIC.items():
            try:
                if hasattr(Obj, "QuDestroy"):
                    Obj.QuDestroy()
                del SYSTEMDIC[Name]
            except Exception:
                traceback.print_exc()

class Include:
    """ 扩展包管理 """
    def __init__(self):
        self.ctRender_v2 = False
        """ CTRender v2 资源管理系统 """
        self.attackExtend = False
        """ AC战斗机制 链攻击系统 (暂未加入)
            @依赖项:
                CTRender - 应用与全局节点同步管理
        """
    def _insertClientList(self, lis):
        # type: (list[SystemSide]) -> None
        if self.ctRender_v2:
            lis.insert(0, SystemSide(QuModLibsPath + ".Include.CT_Render.ClientApi"))
        if self.attackExtend:
            lis.insert(0, SystemSide(QuModLibsPath + ".Include.AttackExtend.Client"))

    def _insertServerList(self, lis):
        # type: (list[SystemSide]) -> None
        if self.ctRender_v2:
            lis.insert(0, SystemSide(QuModLibsPath + ".Include.CT_Render.ServerApi"))
        if self.attackExtend:
            lis.insert(0, SystemSide(QuModLibsPath + ".Include.AttackExtend.Server"))

class EasyMod(object):
    """ 创建EasyMod 模组开发的初始化入口 请确保完整的导入了整个QuMod包,否则可能不生效 """
    _MOD_NAME = "MOD_NAME"
    _VERSION = "VERSION"
    def __init__(self, ParentDir = QUMOD_MOD_MAIN.__module__.split(".")[0], **_):
        SetModDirName(ParentDir)
        self.__ParentDir = ParentDir # 所在的父路径
        self.__ServerLis = []   # 记录需要创建的服务端数据
        self.__ClientLis = []   # 记录需要创建的客户端数据
        self.ClientFunc = []
        self.ServerFunc = []
        # -- 基本的初始与注销服务端/客户端回调 --
        NullFun = lambda *_: None
        self.OnServerInit = NullFun
        self.OnClientInit = NullFun
        # -- 基本的初始与注销服务端/客户端回调 --
        
        EasyModSl[0] = self
        EasyModSl[1] = self.__ServerLis
        EasyModSl[2] = self.__ClientLis
        
        self.include = Include()
        """ 扩展包管理 可设置扩展包为True启用加载 """
        self._serverWaitTime = None
        self._clientWaitTime = None
        
    def addClientFunc(self, object):
        """ 增加客户端调用函数 自动执行 """
        self.ClientFunc.append(object)
    
    def addServerFunc(self, object):
        """ 增加服务端调用函数, 自动执行 """
        self.ServerFunc.append(object)
    
    def setServerWaitTime(self, waitTime):
        # type: (float) -> None
        """ 设置Server加载的等待时间 """
        self._serverWaitTime = waitTime

    def setClientWaitTime(self, waitTime):
        # type: (float) -> None
        """ 设置Client加载的等待时间 """
        self._clientWaitTime = waitTime

    def getModName(self):
        # type: () -> str | None
        """ 获取ModName """
        return getattr(QUMOD_MOD_MAIN, EasyMod._MOD_NAME)

    def getModVersion(self):
        # type: () -> str | None
        """ 获取ModVersion """
        return getattr(QUMOD_MOD_MAIN, EasyMod._VERSION)

    def setModName(self, _name):
        # type: (str) -> None
        """ 设置ModName """
        setattr(QUMOD_MOD_MAIN, EasyMod._MOD_NAME, _name)

    def setModVersion(self, _version):
        # type: (str) -> None
        """ 设置ModVersion """
        setattr(QUMOD_MOD_MAIN, EasyMod._VERSION, _version)

    # 格式化所在路径
    def FormatPath(self, Path):
        # type: (str) -> str
        if len(self.__ParentDir) and not Path.startswith(QuModLibsPath):
            return str(self.__ParentDir+"."+Path).replace("/",".")
        return Path.replace("/",".")
    
    def Server(self, Path, SystemName = None):
        """ 注册服务端 
            @SystemName 选填 可分配一个系统名
            ps: 系统名仅在当前作用域有效 与其他mod隔离
        """
        Obj = SystemSide(Path, SystemName = SystemName)
        self.__ServerLis.append(Obj)
        return self

    def Client(self, Path, SystemName = None):
        """ 注册客户端 
            @SystemName 选填 可分配一个系统名
            ps: 系统名仅在当前作用域有效 与其他mod隔离
        """
        Obj = SystemSide(Path, SystemName = SystemName)
        self.__ClientLis.append(Obj)
        return self