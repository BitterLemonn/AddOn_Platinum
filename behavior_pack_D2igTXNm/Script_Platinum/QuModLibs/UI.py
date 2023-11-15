# -*- coding: utf-8 -*-
from QuClientApi.ui.screenNode import ScreenNode as BaseScreenNode
from mod.client.ui.screenNode import ScreenNode
import mod.client.extraClientApi as clientApi
from Util import ModDirName, RandomUid, ExceptionHandling
from types import MethodType
from functools import wraps

__all__ = [
    "EasyScreenNodeCls", "ESNC", "QuScreenAnimation"
]

class QuGridObject(object):
    """ 网格对象 """
    def __init__(self, uiNode, Path, IsScrollGrid=False, DelayUpdate=False):
        # type: (EasyScreenNodeCls, str, bool, bool) -> None
        self.uiNode = uiNode        # type: EasyScreenNodeCls
        self.Path = Path            # type: str
        self.IsScrollGrid = IsScrollGrid
        self.RenderChildList = [] # type: list
        """ 子控件渲染列表 """
        self.__FLoadE = True
        self.RenItemPanelName = ""   # 渲染项目的画布名
        self.DelayUpdate = DelayUpdate
        """ 是否启用延迟界面更新 """
        self.ViewRenderCount = {
        }       # 视图渲染次数
    
    def GridUpDate(self, CallBack=lambda *_:None, ChildPathList=None):
        """ 网格更新处理 """
        if self.DelayUpdate:
            self.uiNode.UpdateScreen(False)
        ChildPathList = ChildPathList if ChildPathList else self.uiNode.GetAllChildrenPath(self.Path)  # type: list[str]
        Key = "/"   # 路径关键字
        for ConPath in ChildPathList:
            ABSConPath = ConPath[len(self.Path):]
            if ABSConPath.count(Key) == 1:
                # 是渲染项目中的Parent
                if self.__FLoadE:
                    self.RenItemPanelName = ABSConPath[:-1]
                    self.__FLoadE = False
                try:
                    Pos = int(ABSConPath[len(self.RenItemPanelName):])-1
                except Exception as e:
                    print(e)
                    continue
                ViewPath = "{0}{1}{2}".format(self.Path, self.RenItemPanelName, Pos+1)
                self.ViewRenderCount[ViewPath] = self.ViewRenderCount.get(ViewPath, 0) + 1
                CallBack(ViewPath, Pos)
        if self.DelayUpdate:
            self.uiNode.UpdateScreen(True)

class QuBaseAnimation(object):
    """ 基本动画类 """
    def Start(self):
        """ 开始播放时 """
        pass

    def OnEnd(self):
        """ 结束播放时 """
        pass

    def OnTick(self):
        pass

class QuScreenAnimation(object):
    """ 界面动画类 """
    class MoveAnimation(QuBaseAnimation):
        """ 移动动画 """
        def __init__(self, Length=0.0, StartPos=(0,0), EndPos=(0,0)):
            # type: (float, tuple, tuple) -> None
            from Util import Unknown
            self.Length = Length                        # 时长
            self.StartPos = StartPos                    # 开始位置
            self.EndPos = EndPos                        # 结束位置
            self.Time = 0.0                             # 播放时长
            self.CallBack = lambda *_:None              # 播放完毕的回调
            self.ConText = Unknown    # 界面上下文
            self.ConPath = ""                           # 控件目标

        def Start(self, ConText, ConPath, OnEnd=lambda *_:None):
            # type: (EasyScreenNodeCls, str, object) -> None
            """ 开始播放时 """
            from Client import ListenForEvent, TickEvent
            ListenForEvent(TickEvent, self, self.OnTick)
            self.IsRun = True
            self.CallBack = OnEnd
            self.ConText = ConText
            self.ConPath = ConPath
        
        def CurvilinearParabola(self, Value, M=2):
            """ 抛物线曲线 """
            # j = min(Value/2.0, 1.0)
            j = Value
            j *= M
            result = -(j**2)/(M**2) + (2*j)/M
            return result

        def OnTick(self):
            if self.Time<=self.Length:
                self.Time += 1/30.0
                Time = min(self.Time, self.Length)
                Proportion = self.CurvilinearParabola(Time/self.Length)        # 进度占比
                self.ConText.GetBaseUIControl(self.ConPath).SetPosition(
                    tuple(self.StartPos[i]+(self.EndPos[i]-self.StartPos[i])*Proportion for i in range(2))
                )                                                              # 设置位置
                return None
            self.OnEnd()
    
        def OnEnd(self):
            """ 结束播放时 """
            from Client import UnListenForEvent, TickEvent
            UnListenForEvent(TickEvent, self, self.OnTick)
            self.Time = 0.0
            self.CallBack()
    
    @staticmethod
    def Play(ConText, ConPath, Animation, OnEnd=lambda *_:None):
        # type: (EasyScreenNodeCls, str, QuBaseAnimation, object) -> None
        """ 播放动画 """
        from copy import copy
        copy(Animation).Start(ConText, ConPath, OnEnd)
    
    @staticmethod
    def CreatControlEffect(ConText, ConPath, Anim, OnEnd=lambda *_:None, Layer=1000):
        # type: (EasyScreenNodeCls, str, QuBaseAnimation, object, int) -> None
        """ 创建控件效果 创建新控件再播放 结束后自动销毁 """
        RandomName = RandomUid()
        Parent = "/"
        NewConPath = Parent+RandomName
        ConText.Clone(ConPath, Parent, RandomName)
        def END():
            OnEnd()
            ConText.RemoveComponent(NewConPath, Parent)
        ConText.GetBaseUIControl(NewConPath).SetLayer(Layer)
        QuScreenAnimation.Play(
            ConText, NewConPath, Anim, OnEnd=END
        )

class EasyScreenNodeCls(BaseScreenNode):
    ''' 简易界面类 可继承并开发 '''
    UiName = "Ui_"+RandomUid() # Ui名字 默认随机
    UiDef = None # 用来标识json ui的命名空间和界面名 如 zeroui.main
    ParamDict = {"isHud" : 1} # 界面参数字典
    CreateParams = None # 堆栈管理的界面参数
    IsPushScreen = False # 是 PushScreen 界面?
    RandomSc = "Sc"+RandomUid()
    UiInitListen = {}
    DeBugMode = 0 # 调试模式
    @classmethod
    def GetUi(cls, Ui=None):
        # type: (object|EasyScreenNodeCls) -> EasyScreenNodeCls | None
        ''' 获取Ui 参数为UiName或继承EasyScreenNodeCls的子类 '''
        if isinstance(Ui,str):
            return clientApi.GetUI(ModDirName, Ui)
        elif Ui == None:
            return cls.GetUi(cls)
        elif issubclass(Ui,EasyScreenNodeCls):
            return clientApi.GetUI(ModDirName, Ui.UiName)

    @classmethod
    def RemoveUi(cls):
        ''' [静态] 删除Ui节点 '''
        UiNode = cls.GetUi() # type: EasyScreenNodeCls
        if UiNode:
            UiNode.SetRemove()

    @staticmethod
    def GridRenderAdapter(ConPath, IsScrollGrid=False, DelayUpdate=False):
        """ 网格渲染适配器 支持列表网格 PS:注册的方法名不能和当前静态方法一致否则无效 """
        def __Do(Met):
            Key = "__OnGridRender__"
            if not hasattr(Met,Key):setattr(Met,Key,[])
            List = getattr(Met,Key) # type: list[tuple[str,str]]
            List.append((ConPath, IsScrollGrid, DelayUpdate))
            return Met
        return __Do

    @staticmethod
    def OnClick(ConPath,isSwallow=True):
        ''' 
            [装饰器] 注册按钮点击回调 参数: Button控件路径, (选填) isSwallow=True # False为点击穿透
            回调参数: 无
        '''
        def __OnClick(Met):
            OnClickKey = "__OnClick__"
            if not hasattr(Met,OnClickKey):setattr(Met,OnClickKey,[])
            List = getattr(Met,OnClickKey) # type: list[tuple[str,str]]
            List.append((ConPath,isSwallow,))
            return Met
        return __OnClick

    @staticmethod
    def OnTouch(ConPath,isSwallow=True):
        ''' 
            [装饰器] 注册按钮Touch回调 参数: Button控件路径, (选填) isSwallow=True # False为点击穿透
            回调参数: Args:Dict 详细描述触碰信息
        '''
        def __OnTouch(Met):
            OnTouchKey = "__OnTouch__"
            if not hasattr(Met,OnTouchKey):setattr(Met,OnTouchKey,[])
            List = getattr(Met,OnTouchKey) # type: list[tuple[str,str]]
            List.append((ConPath,isSwallow,))
            return Met
        return __OnTouch

    @staticmethod
    def Listen(__Event):
        ''' 
            [装饰器] 注册UI界面的事件监听,并在UI销毁时自动结束监听
            参数: Event:str  回调参数:Args:dict|无
        '''
        Event = __Event if isinstance(__Event, str) else __Event.__name__
        def __Listen(Met):
            ListenKey = "__ListenEvents__"
            if not hasattr(Met,ListenKey):setattr(Met,ListenKey,[])
            List = getattr(Met,ListenKey) # type: list[str]
            List.append(Event)
            return Met
        return __Listen

    @staticmethod
    def Binding(
            UiDef=None,
            ParamDict={"isHud" : 1},
            UiName= None, 
            CreateParams=None,
            IsPushScreen=False
        ):
        UiName = UiName if UiName else RandomUid()
        from Client import System,EnSp,EnSy,TemporaryContainer
        ''' 
            [装饰器] 用于绑定界面类与UI.json文件的操作
            大多数情况下只要设置 UiDef="xxx.main"即可 由于UiDef是第一个参数，也可以不使用Key=Value
            UiName不指定即为随机 ParamDict不指定则为 {"isHud" : 1}
            例: @EasyScreenNodeCls.Binding("test.main")
        '''
        def NewCls(Cls):
            NowPath = Cls.__module__+"."+Cls.__name__
            Cls.UiName = UiName
            Cls.UiDef = UiDef
            Cls.ParamDict = ParamDict
            Cls.CreateParams = CreateParams
            Cls.IsPushScreen = IsPushScreen   
            def Register(Args={}):
                ScreenNodeClsPath = ModDirName+".QuModLibs.UIExchange."+Cls.RandomSc
                clientApi.RegisterUI(ModDirName, Cls.UiName, ScreenNodeClsPath, Cls.UiDef)

            if NowPath in EasyScreenNodeCls.UiInitListen:
                Data=EasyScreenNodeCls.UiInitListen[NowPath]
                System.UnListenForEvent(EnSp,EnSy,"UiInitFinished", Data[0], Data[1])
                print("[%s] 重载注册: %s"%(Cls.__name__,NowPath))
                Register()

            TC = TemporaryContainer()
            TC.Register = Register
            System.ListenForEvent(EnSp,EnSy,"UiInitFinished",TC, Register)
            EasyScreenNodeCls.UiInitListen[NowPath] = (TC, Register)
            return Cls
        return NewCls

    class ScreenNodeCls(ScreenNode):
        def __init__(self, namespace, name, param):
            ScreenNode.__init__(self, namespace, name, param)
            self.QUGRIDRENDER = [] # type: list[tuple[str, str, QuGridObject]]

        def Create(self):
            pass

        def Destroy(self):
            pass

        def QuGetScrollGridObject(self, path):
            # type: (str) -> QuScrollGrid
            return QuScrollGrid(self, path)

        def QuSetButtonCallback(self, buttonCont, callBack):
            # type: (str, object) -> bool
            def creatFun(func):
                def newFun(*_):
                    return func()
                return newFun
            baseUIControl = self.GetBaseUIControl(buttonCont)
            baseUIControl.SetTouchEnable(True)
            buttonUIControl = baseUIControl.asButton()
            buttonUIControl.AddTouchEventParams({"isSwallow":True})
            buttonUIControl.SetButtonTouchUpCallback(creatFun(callBack))

        def QuUpdateMeshRendering(self):
            RenderCall = self.QUGRIDRENDER
            for GridPath, MetName, GridObject in RenderCall:
                def Do(GridPath, ChilList=None):
                    GridObject.Path = GridPath
                    ChilList = GridObject.RenderChildList if not ChilList else ChilList
                    GridObject.GridUpDate(CallBack=getattr(self, MetName), ChildPathList=ChilList)
                if GridObject.IsScrollGrid:   # 是网格列表
                    scrollViewUIControl = self.GetBaseUIControl(GridPath).asScrollView()
                    Path = scrollViewUIControl.GetScrollViewContentPath()
                    CHIL = self.GetAllChildrenPath(Path)
                    Do(Path, CHIL)
                    continue
                Do(GridPath)
        
        def QuGetControlABSPos(self, Path):
            # type: (str) -> tuple[float,float]
            x, y = 0.0, 0.0
            while Path:
                xp, yp = self.GetBaseUIControl(Path).GetPosition()
                x+=xp; y+=yp
                Path = Path[:Path.rfind("/")]
            return (x, y)
        
        def QuGetGridRenderObj(self, GridPath="/"):
            # type: (str) -> None | QuGridObject
            for __GridPath, _, Obj in self.QUGRIDRENDER:
                if GridPath == __GridPath:
                    return Obj
            return None
        
        def QuGetGridViewRenderCount(self, GridViewPath="/"):
            ParentPath = GridViewPath[:GridViewPath.rfind("/")]
            Obj = self.QuGetGridRenderObj(ParentPath)
            if not Obj: return 0
            return Obj.ViewRenderCount.get(GridViewPath, 0)

    def QuGetGridRenderObj(self, GridPath="/"):
        # type: (str) -> None | QuGridObject
        """ 获取网格渲染对象 """
        pass
    
    def QuGetScrollGridObject(self, path):
        # type: (str) -> QuScrollGrid
        """ 获取Qu网格管理对象 """
        pass


    def QuSetButtonCallback(self, buttonCont, callBack):
        # type: (str, object) -> bool
        """ 快捷设置按钮点击回调 """
        pass
    
    def QuGetGridViewRenderCount(self, GridViewPath="/"):
        # type: (str) -> int
        """ 获取网格视图渲染次数 可以用来判断是否为第一次渲染 """
        pass


    def QuUpdateMeshRendering(self):
        """ 更新当前界面的网格渲染 """
        pass

    def QuGetControlABSPos(self, __Path):
        # type: (str) -> tuple[float,float]
        """ 获取控件绝对位置信息 """
        pass

    @staticmethod
    def __CREAT__(uiNode,Data):
        # type: (EasyScreenNodeCls, dict) -> None
        # ======= 界面创建完毕后自动执行 ========
        from Client import System,EnSp,EnSy
        uiNode.QUGRIDRENDER = []
        OnClick = Data["OnClick"] # type: dict
        OnTouch = Data["OnTouch"] # type: dict
        ListenEvents = Data["ListenEvents"] # type: list
        OnGridRender = Data["OnGridRender"] # type: dict
        # ===== Click处理 =====
        def creatFun(func):
            def newFun(*_):
                return func()
            return newFun
        for FunName, DataLis in OnClick.items():
            Func = getattr(uiNode,FunName) # 回调方法
            newFun = creatFun(Func)
            for ButtonPath, isSwallow in DataLis:
                baseUIControl = uiNode.GetBaseUIControl(ButtonPath)
                baseUIControl.SetTouchEnable(True)
                buttonUIControl = baseUIControl.asButton()
                buttonUIControl.AddTouchEventParams({"isSwallow":isSwallow})
                buttonUIControl.SetButtonTouchUpCallback(newFun)
        # ===== Touch处理 =====
        for FunName, DataLis in OnTouch.items():
            Func = getattr(uiNode,FunName) # 回调方法
            for ButtonPath, isSwallow in DataLis:
                baseUIControl = uiNode.GetBaseUIControl(ButtonPath)
                baseUIControl.SetTouchEnable(True)
                buttonUIControl = baseUIControl.asButton()
                buttonUIControl.AddTouchEventParams({"isSwallow":isSwallow})
                buttonUIControl.SetButtonTouchDownCallback(Func)
                buttonUIControl.SetButtonTouchUpCallback(Func)
                buttonUIControl.SetButtonTouchCancelCallback(Func)
                buttonUIControl.SetButtonTouchMoveCallback(Func)
                buttonUIControl.SetButtonTouchMoveInCallback(Func)
                buttonUIControl.SetButtonTouchMoveOutCallback(Func)
                buttonUIControl.SetButtonScreenExitCallback(Func)
        
        # ===== 监听事件处理 ======
        for EventName,FunName in ListenEvents:
            System.ListenForEvent(EnSp,EnSy,EventName,uiNode,getattr(uiNode,FunName))
        
        # ===== GridRender处理 =====
        if len(OnGridRender):
            # 渲染回调信息列表
            RenderCall = []     # type: list[tuple[str, str, QuGridObject]]
            for FunName, DataLis in OnGridRender.items():
                for GridPath, IsScrollGrid, DelayUpdate in DataLis:
                    # GridPath 网格路径
                    RenderCall.append((GridPath, FunName, QuGridObject(uiNode, GridPath, IsScrollGrid, DelayUpdate)))
            uiNode.QUGRIDRENDER = RenderCall
            def __OnGridRender(uiNode):
                # type: (EasyScreenNodeCls) -> None
                """ 网格更新事件 """
                for GridPath, MetName, GridObject in RenderCall:
                    def Do(GridPath, ChilList=None):
                        GridObject.Path = GridPath
                        ChilList = ChilList if ChilList else uiNode.GetAllChildrenPath(GridPath)
                        if GridObject.RenderChildList != ChilList:
                            # UpDate 网格渲染更新
                            GridObject.RenderChildList = ChilList
                            GridObject.GridUpDate(CallBack=getattr(uiNode, MetName), ChildPathList=ChilList)
                    if GridObject.IsScrollGrid:   # 是网格列表
                        scrollViewUIControl = uiNode.GetBaseUIControl(GridPath).asScrollView()
                        Path = scrollViewUIControl.GetScrollViewContentPath()
                        CHIL = uiNode.GetAllChildrenPath(Path)
                        if CHIL:    # 有子节点 更新绘制
                            Do(Path, CHIL)
                        continue
                    Do(GridPath)
            RanDomName = "QuSystemGridComponentSizeChangedClientEvent"
            newFun = creatFun(lambda: __OnGridRender(uiNode))
            def QuSystemGridComponentSizeChangedClientEvent(args={}):
                return __OnGridRender(uiNode)
            EventName = "GridComponentSizeChangedClientEvent"
            setattr(uiNode, RanDomName, QuSystemGridComponentSizeChangedClientEvent)
            System.ListenForEvent(EnSp, EnSy, EventName,uiNode, getattr(uiNode,RanDomName))
            ListenEvents.append((EventName, RanDomName))

        # ==== 注册界面销毁监听 ====    
        def NewDestroy(Met):
            @wraps(Met)
            def __Destroy(*Args,**Kwargs):
                EasyScreenNodeCls.__DESTROY__(uiNode,Data)
                return Met(*Args,**Kwargs)
            return __Destroy
        uiNode.Destroy = NewDestroy(uiNode.Destroy)

    @staticmethod
    def __DESTROY__(uiNode,Data):
        # ======= 界面销毁后自动执行 ========
        from Client import System,EnSp,EnSy
        ListenEvents = Data["ListenEvents"] # type: list
        for EventName,FunName in ListenEvents:
            System.UnListenForEvent(EnSp,EnSy,EventName,uiNode,getattr(uiNode,FunName))

    def __new__(cls, *Args, **Kwargs):
        if not cls.UiDef:
            print("[Error] (Class.%s) 你不能创建一个未绑定的界面 !!"%(cls.__name__))
            return None
        GetUi = cls.GetUi()
        if not GetUi:
            from copy import deepcopy
            import UIExchange
            NewCls = deepcopy(cls.ScreenNodeCls)
            setattr(UIExchange, cls.RandomSc, NewCls)
            # 创建UI界面
            if cls.IsPushScreen:
                uiNode = clientApi.PushScreen(ModDirName, cls.UiName, cls.CreateParams)
            else:
                uiNode = clientApi.CreateUI(ModDirName, cls.UiName, cls.ParamDict)
                if not uiNode:
                    ScreenNodeClsPath = ModDirName+".QuModLibs.UIExchange."+cls.RandomSc
                    clientApi.RegisterUI(ModDirName, cls.UiName, ScreenNodeClsPath, cls.UiDef)
                    uiNode = clientApi.CreateUI(ModDirName, cls.UiName, cls.ParamDict)
            # ==== 添加后处理数据信息 ====
            PostProcessing = {
                "OnClick":{},
                "OnTouch":{},
                "OnGridRender": {},
                "ListenEvents":[],
            }
            OnClick = PostProcessing["OnClick"] # type: dict
            OnGridRender = PostProcessing["OnGridRender"] # type: dict
            OnTouch = PostProcessing["OnTouch"] # type: dict
            ListenEvents = PostProcessing["ListenEvents"] # type: list
            for FunName, Fun in (
                (x,y) for x,y in cls.__dict__.items()
                if not hasattr(EasyScreenNodeCls,x) or x in ['__init__','Create','OnActive','OnDeactive','Destroy']
            ):
                if not hasattr(Fun, "__call__"): continue
                setattr(uiNode, FunName,
                    MethodType(Fun, uiNode)
                ) # 动态添加方法到Ui实例对象
                
                if hasattr(Fun,'__OnClick__'):
                    __FunName = Fun.__name__
                    OnClick[__FunName] = getattr(Fun,'__OnClick__')
                    
                if hasattr(Fun,'__OnGridRender__'):
                    __FunName = Fun.__name__
                    OnGridRender[__FunName] = getattr(Fun,'__OnGridRender__')

                if hasattr(Fun,'__OnTouch__'):
                    __FunName = Fun.__name__
                    OnTouch[__FunName] = getattr(Fun,'__OnTouch__')
                        
                if hasattr(Fun,'__ListenEvents__'):
                    __FunName = Fun.__name__
                    Append = ListenEvents.append
                    for Event in getattr(Fun,'__ListenEvents__'):
                        Append((Event, __FunName))

            EasyScreenNodeCls.__CREAT__(uiNode,PostProcessing)
            uiNode.__init__(*Args, **Kwargs)
            if hasattr(cls,"Creat"):
                uiNode.Creat()
            return uiNode
        return GetUi

    def __init__(self):
        self.QUGRIDRENDER = [] # type: list[tuple[str, str, QuGridObject]]
    
    def Destroy(self):
        pass

    def Create(self):
        pass

    def __AddTouchEventHandler(self, ConPath, Fun, Data):
        ''' [已废弃] 设置按钮点击事件 Data一般写{"isSwallow":True} '''
        pass

class QuScrollGrid(object):
    """ 滚动网格 """
    def __init__(self, uiNode, path):
        self.uiNode = uiNode # type: EasyScreenNodeCls
        self.path = path
    
    @ExceptionHandling(lambda: False)
    def redrawLayoutSize(self, baseX=1, baseY=2, count=2):
        # type: (int, int, int) -> bool
        """ 重绘布局大小
            baseX: 基准宽度大小 即宽度可填充数量
            baseY: 基准高度大小 以一整页高度为准的可填充数量
            count: 需要绘制的数量 (不代表真实绘制容量,基于网格特性一定会绘制: n*baseX*baseY 个, 多余内容需自行控制隐藏)
        """
        scrollView = self.uiNode.GetBaseUIControl(self.path)
        size1, size2 = scrollView.GetSize()
        viewPath = scrollView.asScrollView().GetScrollViewContentPath()
        grid = self.uiNode.GetBaseUIControl(viewPath)
        yCount = count // baseX + (1 if count % baseX else 0)
        itemH = size2/baseY     # 每行分配的高度
        grid.asGrid().SetGridDimension((baseX, yCount))
        grid.SetSize((size1, itemH*yCount), True)


ESNC = EasyScreenNodeCls # EasyScreenNodeCls的缩写