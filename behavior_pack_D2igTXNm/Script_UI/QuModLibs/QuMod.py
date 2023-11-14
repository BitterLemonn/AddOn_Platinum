# -*- coding: utf-8 -*-

from mod.common.mod import Mod
import mod.server.extraServerApi as serverApi
import mod.client.extraClientApi as clientApi
from Information import ApiVersion, Version
from Util import SetModDirName, import_module
from uuid import uuid4

RandomKey = "Q"+str(uuid4()).replace("-","") # 随机钥匙

# 创建随机UID
def RandomUid():
    return "QuMod_"+str(uuid4()).replace("-","")

class SystemSide(object):
    def __init__(self,Path,SystemName=None):
        self.SystemName = SystemName # 绑定系统
        self.Path = Path

EasyModSl = [None,[],[]] # 记录实例
ModDirName = SystemSide.__module__.split(".")[0]

@Mod.Binding(name = "QuMod_"+ModDirName, version = "1.0.0")
class modMain(object):
    ''' 用于自动化注册Mod信息  '''
    @Mod.InitServer()
    def ServerInit(self):
        # 服务端初始化
        ### ======== 设置缓存阻止补全库真正导入,仅提供补全提示 ======== ###
        # from Util import ModDirName, SetModuleCache, SetModuleAttr
        # SetModuleCache(ModDirName+'.QuModLibs.QuServerApi.extraServerApi', serverApi)
        # SetModuleAttr(
        #     ModDirName+'.QuModLibs.QuServerApi', 'extraServerApi', serverApi
        # )
        ### ======== 设置缓存阻止补全库真正导入,仅提供补全提示 ======== ###
        import IN; IN.IsServerUser = True

        # === 插件系统处理 ===
        import Server
        key = "qumod_nx_server"
        System = serverApi.GetSystem("Minecraft","game")
        if not hasattr(System, key):
            setattr(System, key, {})
        dataDic = getattr(System, key)  # type: dict
        dataDic[ModDirName] = Server
        # === 插件系统处理 ===

        this = EasyModSl[0] # type: EasyMod
        for func in this.ServerFunc:
            try:
                func()
            except Exception as e:
                print("[Error]: $"+str(e))
        
        # ServerLis = EasyModSl[1]
        if not this: return None
        this.OnServerInit()
        return
        # from Server import SER_SYSTEM_APPEND
        # for Data in ServerLis:
        #     Path = Data.Path
        #     SystemName = Data.SystemName
        #     SysObj = import_module(this.FormatPath(Path))
        #     if not SystemName: SystemName = str(uuid4()).replace("-","")
        #     SER_SYSTEM_APPEND(SystemName,SysObj)

    @Mod.DestroyServer()
    def ServerDestroy(self):
        # 服务端销毁时
        this = EasyModSl[0]
        if not this: return None
        from Server import SYSTEMDIC, Destroy
        Destroy() # 销毁处理方法
        for Name, Obj in SYSTEMDIC.items():
            if hasattr(Obj, 'QuDestroy'): Obj.QuDestroy()
            del SYSTEMDIC[Name]; del Obj

    @Mod.InitClient()
    def ClientInit(self):
        # 客户端初始化
        from Util import ModDirName
        ### ======== 设置缓存阻止补全库真正导入,仅提供补全提示 ======== ###
        # SetModuleCache(ModDirName+'.QuModLibs.QuClientApi.extraClientApi', clientApi)
        # SetModuleAttr(
        #     ModDirName+'.QuModLibs.QuClientApi', 'extraClientApi', clientApi
        # )
        # import QuModLibs.QuClientApi.ui.screenNodeEnu as screenNodeEnu
        # SetModuleCache(
        #     ModDirName+'.QuModLibs.QuClientApi.ui.screenNode',
        #     screenNodeEnu,
        # )
        ### ======== 设置缓存阻止补全库真正导入,仅提供补全提示 ======== ###

        def Load():
            # === 插件系统处理 ===
            import Client
            key = "qumod_nx_client"
            System = clientApi.GetSystem("Minecraft","game")
            if not hasattr(System, key):
                setattr(System, key, {})
            dataDic = getattr(System, key)  # type: dict
            dataDic[ModDirName] = Client
            # === 插件系统处理 ===

            this = EasyModSl[0] # type: EasyMod
            for func in this.ClientFunc:
                try:
                    func()
                except Exception as e:
                    print("[Error]: $"+str(e))
            # ClientLis = EasyModSl[2]
            if not this: return None
            this.OnClientInit()
        comp = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLevelId())
        comp.AddTimer(0.0, Load)
        return
        # from Client import CLI_SYSTEM_APPEND, EasyThread
        # def Loading():
        #     for Data in ClientLis:
        #         Path = Data.Path
        #         SystemName = Data.SystemName
        #         SysObj = import_module(this.FormatPath(Path))
        #         if not SystemName: SystemName = str(uuid4()).replace("-","")
        #         CLI_SYSTEM_APPEND(SystemName,SysObj)
        # EasyThread.NextTick(Loading)

    @Mod.DestroyClient()
    def ClientDestroy(self):
        # 客户端销毁时
        this = EasyModSl[0]
        if not this: return None
        from Client import SYSTEMDIC, Destroy
        Destroy() # 销毁处理方法
        for Name, Obj in SYSTEMDIC.items():
            if hasattr(Obj, 'QuDestroy'): Obj.QuDestroy()
            del SYSTEMDIC[Name]; del Obj
    
class QuPluginAPI(object):
    ''' QuMod 插件API '''
    def __init__(self, RePath, System):
        self.RePath = RePath
        self.Version = ApiVersion # 插件版本 : int
        self.EasyMod = System # type: EasyMod
    
    def Server(self,Path,SystemName=None):
        ''' 创建Plugin服务端 '''
        self.EasyMod.Server(self.RePath+"."+Path,SystemName)
        return self

    def Client(self,Path,SystemName=None):
        ''' 创建Plugin客户端 '''
        self.EasyMod.Client(self.RePath+"."+Path,SystemName)
        return self

# 简易Mod
class EasyMod(object):
    ''' 创建EasyMod 模组开发的初始化入口 请确保完整的导入了整个QuMod包,否则可能不生效 '''
    def __init__(self, ParentDir=modMain.__module__.split(".")[0], Plugins=[]):
        SetModDirName(ParentDir)
        self.__ParentDir = ParentDir # 所在的父路径
        self.__ServerLis = []   # 记录需要创建的服务端数据
        self.__ClientLis = []   # 记录需要创建的客户端数据
        self.ClientFunc = []
        self.ServerFunc = []
        # -- 基本的初始与注销服务端/客户端回调 --
        NullFun = lambda *_: None
        self.OnServerInit = NullFun; self.OnClientInit = NullFun
        # -- 基本的初始与注销服务端/客户端回调 --
        
        EasyModSl[0] = self; EasyModSl[1] = self.__ServerLis
        EasyModSl[2] = self.__ClientLis
        for PluginData in Plugins:
            self.__PluginsLoading(PluginData)
    
    def addClientFunc(self, object):
        """ 增加客户端调用函数 自动执行 """
        self.ClientFunc.append(object)
    
    def addServerFunc(self, object):
        """ 增加服务端调用函数, 自动执行 """
        self.ServerFunc.append(object)

    # 插件处理
    def __PluginsLoading(self, PluginData):
        return
        # try:
        #     if isinstance(PluginData,tuple):
        #         # === 带参数的处理 ===
        #         PluginPath, PluginKwar = PluginData
        #         ParameterPath = PluginPath+".Configure"
        #         ParameterObj = import_module(self.FormatPath(ParameterPath))
        #         for k, v in dict(PluginKwar).items():
        #             setattr(ParameterObj,k,v)
        #         self.__PluginsLoading(PluginPath)
        #     elif isinstance(PluginData,str):
        #         # === 无参数的处理 ===
        #         InitPath = PluginData+".__init__"
        #         InitObj = import_module(self.FormatPath(InitPath))
        #         InitDic = InitObj.__dict__ # type: dict
        #         if not (ApiVersion >= InitDic.get("MinApi",0) and ApiVersion <= InitDic.get("MaxApi", 114514)):
        #             print("[Error] %s 不匹配当前API版本,无法加载"%(PluginData))
        #             return None
        #         MainPath = PluginData+".Main"
        #         MainObj = import_module(self.FormatPath(MainPath))
        #         if hasattr(MainObj,"__Main__"):
        #             MainObj.__Main__(QuPluginAPI(PluginData.replace("/","."), self))
        #     else:
        #         print("[Error] %s 无效的参数"%(PluginData))
        # except Exception as e:
        #     print(e)


    # 格式化所在路径
    def FormatPath(self,Path):
        if len(self.__ParentDir):
            return str(self.__ParentDir+"."+Path).replace("/",".")
        else:
            return Path.replace("/",".")
    
    # 增加/设置服务端
    def Server(self,Path,SystemName=None):
        ''' [已弃用] 创建服务端 Path即所在路径(从Mod设置的父路径开始) SystemName=None 可设置分配一个系统名'''
        return
        # Obj = SystemSide(Path,SystemName=SystemName)
        # self.__ServerLis.append(Obj)
        # return self

    # 增加/设置服务端
    def Client(self,Path,SystemName=None):
        ''' [已弃用] 创建客户端 Path即所在路径(从Mod设置的父路径开始) SystemName=None 可设置分配一个系统名'''
        return
        # Obj = SystemSide(Path,SystemName=SystemName)
        # self.__ClientLis.append(Obj)
        # return self

