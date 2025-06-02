# -*- coding: utf-8 -*-
from ...Server import Call, Events
from ..EventsPool.Server import POOL_ListenForEvent

class CallService:
    """ 通信服务封装 """
    _cacheMap = {}  # type: dict[str, list]
    _workState = False

    @staticmethod
    def _init():
        if CallService._workState:
            return
        CallService._workState = True
        POOL_ListenForEvent(Events.OnScriptTickServer, CallService._OnScriptTickServer)

    @staticmethod
    def _OnScriptTickServer(_={}):
        if len(CallService._cacheMap) <= 0:
            return
        for playerId in CallService._cacheMap:
            Call(playerId, "__calls__", CallService._cacheMap[playerId])
        CallService._cacheMap = {}

    @staticmethod
    def delayCall(playerId, key, *args, **kwargs):
        # type: (str, str, object, object) -> None
        """ 延迟呼叫 智能合批处理
            注意事项: 如果服务端数据大量重复内容发包给不同玩家客户端 使用该方法并不能缓解开销 仅在少数场景下有用
        """
        CallService._init()
        CallService._cacheMap[playerId] = CallService._cacheMap.get(playerId, [])
        CallService._cacheMap[playerId].append(
            (key, args, kwargs)
        )
    
    @staticmethod
    def updateNow():
        CallService._OnScriptTickServer()