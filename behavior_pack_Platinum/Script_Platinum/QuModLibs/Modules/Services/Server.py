# -*- coding: utf-8 -*-
from ...Server import ListenForEvent, UnListenForEvent, _loaderSystem, Events, Call, CallBackKey
from Globals import _BaseService, _ServiceManager, _AutoStopService, BaseEvent, BaseBusiness, KeyBusiness, QRequests
lambda: "Service By Zero123"

__all__ = [
    "BaseService",
    "_serviceManager",
    "AutoStopService",
    "BaseEvent",
    "BaseBusiness",
    "KeyBusiness",
    "QRequests"
]

_serviceManager = _ServiceManager(
    ListenForEvent, UnListenForEvent, Call, lambda key, funObj: CallBackKey(key)(funObj)
)

class BaseService(_BaseService):
    """ 服务基类 """
    _BINDMANAGER = _serviceManager

    def syncRequest(self, playerId, apiPath = "", argsObject = QRequests.Args()):
        # type: (str, str, QRequests.Args) -> None
        """ 同步请求 """
        argsObject.preParam = playerId
        return self.getManager().syncRequest(apiPath, argsObject)

class AutoStopService(BaseService, _AutoStopService):
    """ 自动关闭服务类 """
    def __init__(self):
        BaseService.__init__(self)
        _AutoStopService.__init__(self)
    
    def onAccessed(self):
        BaseService.onAccessed(self)
        return _AutoStopService.onAccessed(self)
    
    def _onTick(self):
        BaseService._onTick(self)
        _AutoStopService._onTick(self)

def getServiceManager():
    return _serviceManager

# ================= 系统级业务逻辑注册 =================
ListenForEvent(Events.OnScriptTickServer, _serviceManager, _serviceManager.onTick)
def _onGameOver():
    BaseService._CLOSE_STATE = True
    _serviceManager.removeAllService()
_loaderSystem._onDestroyCall_LAST.append(_onGameOver)