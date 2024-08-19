# -*- coding: utf-8 -*-
from ...Server import Call, ListenForEvent, Events

class CallService:
    """ 呼叫服务 """
    _cacheMap = {}  # type: dict[str, list]
    _workState = False

    @staticmethod
    def _init():
        if CallService._workState:
            return
        CallService._workState = True
        ListenForEvent(Events.OnScriptTickServer, CallService, CallService.OnScriptTickServer)
    
    @staticmethod
    def OnScriptTickServer(_={}):
        if len(CallService._cacheMap) <= 0:
            return
        for playerId in CallService._cacheMap:
            Call(playerId, "__calls__", CallService._cacheMap[playerId])
        CallService._cacheMap = {}

    @staticmethod
    def delayCall(playerId, key, *args, **kwargs):
        # type: (str, str, object, object) -> None
        """ 延迟呼叫 智能合批处理 """
        CallService._init()
        CallService._cacheMap[playerId] = CallService._cacheMap.get(playerId, [])
        CallService._cacheMap[playerId].append(
            (key, args, kwargs)
        )

