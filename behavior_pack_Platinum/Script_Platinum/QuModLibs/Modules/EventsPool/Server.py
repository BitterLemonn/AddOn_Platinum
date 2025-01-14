# -*- coding: utf-8 -*-
from ...Server import ListenForEvent
from ...Util import TRY_EXEC_FUN, getObjectPathName
from ..Services.Server import BaseService
from copy import copy
lambda: "By Zero123"

# 网易事件监听机制受优先级以及排序影响 在高频率动态监听/取消的环境下对性能造成的压力较高
# EventsPool 用于维护单一的事件监听并做无序分发 实现更高的动态监听变换性能需求

class EventsPoolService(BaseService):
    _EVENTS_MAP = {}    # type: dict[str, set[object]]
    _STATIC_LISTEN_SET = set()
    def _createListenFunc(self, eventName=""):
        nullSet = set()
        def _listenFunc(*args):
            for func in copy(EventsPoolService._EVENTS_MAP.get(eventName, nullSet)):
                TRY_EXEC_FUN(func, *args)
        _listenFunc.__name__ = "QPOOL_{}".format(eventName)
        return _listenFunc

    def _initListenEvent(self, eventName=""):
        ListenForEvent(eventName, self, self._createListenFunc(eventName))

def POOL_ListenForEvent(eventName="", func=lambda *_: None):
    # type: (str | object, object) -> None
    """ 池化监听事件 """
    eventName = eventName if isinstance(eventName, str) else eventName.__name__
    _EVENTS_MAP = EventsPoolService._EVENTS_MAP
    if not eventName in _EVENTS_MAP:
        _EVENTS_MAP[eventName] = set()
        _service = EventsPoolService.start()
        if _service:
            _service._initListenEvent(eventName)
    _EVENTS_MAP[eventName].add(func)

def POOL_UnListenForEvent(eventName="", func=lambda *_: None):
    # type: (str | object, object) -> None
    """ 池化反监听事件 """
    eventName = eventName if isinstance(eventName, str) else eventName.__name__
    _EVENTS_MAP = EventsPoolService._EVENTS_MAP
    if not eventName in _EVENTS_MAP:
        return
    _EVENTS_MAP[eventName].discard(func)

def POOL_STATIC_LISTEN(eventName=""):
    """ 池化静态监听装饰器 """
    def _STATIC_LISTEN(func):
        safeName = getObjectPathName(func)
        if not safeName in EventsPoolService._STATIC_LISTEN_SET:
            EventsPoolService._STATIC_LISTEN_SET.add(safeName)
            POOL_ListenForEvent(eventName, func)
        return func
    return _STATIC_LISTEN