# -*- coding: utf-8 -*-
from ...Client import Call, Events
from ..EventsPool.Client import POOL_ListenForEvent

class CallService:
    """ 通信服务封装 (客户端推荐使用) """
    _cache = []
    _workState = False

    @staticmethod
    def _init():
        if CallService._workState:
            return
        CallService._workState = True
        POOL_ListenForEvent(Events.OnScriptTickClient, CallService._OnScriptTickClient)
    
    @staticmethod
    def _OnScriptTickClient(_={}):
        if len(CallService._cache) <= 0:
            return
        Call("__calls__", CallService._cache)
        CallService._cache = []

    @staticmethod
    def delayCall(key, *args, **kwargs):
        # type: (str, object, object) -> None
        """ 延迟呼叫 智能合批处理 """
        CallService._init()
        CallService._cache.append(
            (key, args, kwargs)
        )

    @staticmethod
    def updateNow():
        CallService._OnScriptTickClient()