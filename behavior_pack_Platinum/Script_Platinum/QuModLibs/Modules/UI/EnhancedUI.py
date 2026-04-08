# -*- coding: utf-8 -*-
from ...UI import ScreenNodeWrapper
from ..Services.Globals import (
    TimerLoader,
    AnnotationLoader,
    LifecycleBind,
    LoopTimerData,
    ContextNode
)
from ...Client import ListenForEvent, UnListenForEvent
from ...Util import QRAIIDelayed, QBaseRAIIEnv
from .Client import QUICanvas, QUIControlFuntion
lambda: "增强版UI模块, 提供更为高阶的UI管理逻辑"

class UIEventListener(QRAIIDelayed):
    """ UI事件监听器(RAII) """
    class Binder(LifecycleBind):
        """ 事件绑定器 """
        def __init__(self, eventName=""):
            LifecycleBind.__init__(self)
            self.eventName = eventName

        def onLoad(self, nodeSelf):
            # type: (ContextNode) -> None
            ListenForEvent(self.eventName, nodeSelf.contextNode, nodeSelf.funObj)

        def onUnLoad(self, nodeSelf):
            # type: (ContextNode) -> None
            UnListenForEvent(self.eventName, nodeSelf.contextNode, nodeSelf.funObj)

    def __init__(self, uiNode, eventName, callback):
        """ 创建UI事件监听器
            - uiNode: UI节点
            - eventName: 事件名称
            - callback: 回调函数
        """
        self.uiNode = uiNode
        self.eventName = eventName
        self.callBack = callback
        if isinstance(uiNode, QBaseRAIIEnv):
            uiNode.addRAIIRes(self)

    def _loadResource(self):
        QRAIIDelayed._loadResource(self)
        ListenForEvent(self.eventName, self.uiNode, self.callBack)

    def _cleanup(self):
        QRAIIDelayed._cleanup(self)
        UnListenForEvent(self.eventName, self.uiNode, self.callBack)

class UIButtonClickBinder(LifecycleBind):
    """ 按钮点击绑定器 """
    def __init__(self, buttonPath=""):
        LifecycleBind.__init__(self)
        self.buttonPath = buttonPath

    def onLoad(self, nodeSelf):
        # type: (ContextNode) -> None
        contextNode = nodeSelf.contextNode
        if isinstance(contextNode, ScreenNodeWrapper):
            contextNode.setButtonClickHandler(self.buttonPath, nodeSelf.funObj)

class QEScreenNode(ScreenNodeWrapper, TimerLoader, AnnotationLoader):
    """ 增强版UI界面节点, 提供更为高阶的UI管理逻辑
        - 继承 `TimerLoader` 支持内环境定时器
        - 继承 `AnnotationLoader` 支持上下文注解
    """
    def __init__(self, namespace, name, param):
        ScreenNodeWrapper.__init__(self, namespace, name, param)
        TimerLoader.__init__(self)

    @staticmethod
    def LoopTimer(time=0.1):
        """ [注解] 循环定时任务 """
        return LoopTimerData.creatAnnotationObj(time)

    @staticmethod
    def Listen(eventName):
        """ [注解] 事件监听 """
        return UIEventListener.Binder.creatAnnotationObj(eventName)
    
    @staticmethod
    def OnClick(buttonPath=""):
        """ [注解] 按钮点击 """
        return UIButtonClickBinder.creatAnnotationObj(buttonPath)

    def Update(self):
        ScreenNodeWrapper.Update(self)
        self._timerUpdate()

    def Create(self):
        ScreenNodeWrapper.Create(self)
        self._loadAnnotation()

    def Destroy(self):
        ScreenNodeWrapper.Destroy(self)
        self._unLoadAnnotation()

class CanvasButtonClickBinder(LifecycleBind):
    """ Canvas类按钮点击绑定器 """
    def __init__(self, buttonPath=""):
        LifecycleBind.__init__(self)
        self.buttonPath = buttonPath

    def onLoad(self, nodeSelf):
        # type: (ContextNode) -> None
        contextNode = nodeSelf.contextNode
        if isinstance(contextNode, QUICanvas):
            contextNode.getUiNode().setButtonClickHandler(
                contextNode._conPath + self.buttonPath,
                nodeSelf.funObj
            )

class IBaseQECanvas(AnnotationLoader, QRAIIDelayed):
    @staticmethod
    def Listen(eventName):
        """ [注解] 事件监听 """
        return UIEventListener.Binder.creatAnnotationObj(eventName)
    
    @staticmethod
    def OnClick(buttonPath=""):
        """ [注解] 按钮点击绑定 """
        return CanvasButtonClickBinder.creatAnnotationObj(buttonPath)

class QECanvas(QUICanvas, IBaseQECanvas):
    """ 增强版画布类 基于RAII机制 """
    def __init__(self, uiNode, parentPath = ""):
        QUICanvas.__init__(self, uiNode, parentPath)

    def onCreate(self):
        QUICanvas.onCreate(self)
        self._loadAnnotation()

    def onDestroyBefore(self):
        QUICanvas.onDestroyBefore(self)
        self._unLoadAnnotation()

    def autoLoad(self):
        self.getUiNode().addRAIIRes(self)
        return self

    def autoRemove(self):
        return self.getUiNode().freeRAIIRes(self)

    def _loadResource(self):
        QRAIIDelayed._loadResource(self)
        self.createControl()

    def _cleanup(self):
        QRAIIDelayed._cleanup(self)
        if self.getUiNode()._raiiCleanState:
            self.removeControl(True)
        else:
            self.removeControl(False)

class QEControlFuntion(QUIControlFuntion, IBaseQECanvas):
    """ 增强版UI控制功能类 基于RAII机制 """
    def __init__(self, uiNode, parentPath = ""):
        QUIControlFuntion.__init__(self, uiNode, parentPath)

    def onCreate(self):
        QUIControlFuntion.onCreate(self)
        self._loadAnnotation()

    def onDestroyBefore(self):
        QUIControlFuntion.onDestroyBefore(self)
        self._unLoadAnnotation()

    def autoLoad(self):
        self.getUiNode().addRAIIRes(self)
        return self

    def autoRemove(self):
        return self.getUiNode().freeRAIIRes(self)

    def _loadResource(self):
        QRAIIDelayed._loadResource(self)
        self.createControl()

    def _cleanup(self):
        QRAIIDelayed._cleanup(self)
        self.removeControl()

def UI_INIT_ERASURE(timelyMode=True):
    """ 用于对UI_ARGS进行擦除 隐式处理参数 """
    def _FORWARD(cls):
        if not issubclass(cls, ScreenNodeWrapper):
            raise TypeError("非法的UI类")
        class WraperForward(cls):
            _WDY_ARGS = tuple()
            _WDY_KWARGS = {}
            def __init__(self, namespace, name, param):
                for baseCls in cls.__bases__:
                    baseCls.__init__(self, namespace, name, param)
                if timelyMode:
                    self._callForwardInit()

            def _callForwardInit(self):
                args = WraperForward._WDY_ARGS
                kwargs = WraperForward._WDY_KWARGS
                WraperForward._WDY_ARGS = tuple()
                WraperForward._WDY_KWARGS = {}
                cls.__init__(self, *args, **kwargs)

            def Create(self):
                if not timelyMode:
                    self._callForwardInit()
                cls.Create(self)

        WraperForward.__name__ = cls.__name__
        if 1 > 2:
            return cls
        return WraperForward
    return _FORWARD

def CREATE_UI_BIND_FORWARDER(uiCls, pushUI=False):
    """
    创建 UI 绑定转发器

    示例:
        class UIXXX(...):
            ...

        uiForward = CREATE_UI_BIND_FORWARD(UIXXX)
        uiForward(*args)  # 通过函数调用方式创建 UI
    """
    if not issubclass(uiCls, ScreenNodeWrapper):
        raise TypeError("非法的UI类")
    def _FORWARD(*args, **kwargs):
        setattr(uiCls, "_WDY_ARGS", args)
        setattr(uiCls, "_WDY_KWARGS", kwargs)
        if not pushUI:
            return uiCls.createUI()
        else:
            return uiCls.pushScreen()
    return _FORWARD