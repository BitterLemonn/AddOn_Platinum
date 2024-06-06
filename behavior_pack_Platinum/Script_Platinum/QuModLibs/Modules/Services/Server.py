# -*- coding: utf-8 -*-
from ...Server import SuperEntityCompCls, levelId, ListenForEvent, UnListenForEvent, serverApi, Entity
lambda: "Service By Zero123"

class IService:
    def onCreate(self):
        pass

    def onServiceUpdate(self):
        pass
    
    def onServiceStop(self):
        pass

class ListenData:
    def __init__(self, eventName = ""):
        self.eventName = eventName

class BaseService(SuperEntityCompCls, IService):
    """ 服务基类 """
    SERVICE_KEY = "__quService__"
    LISTEN_DATA_KEY = "__quListenData__"

    @staticmethod
    def Listen(eventName):
        """ 服务监听注解 """
        def _zsq(funObj):
            setattr(funObj, BaseService.LISTEN_DATA_KEY, ListenData(eventName))
            return funObj
        return _zsq

    def __init__(self):
        SuperEntityCompCls.__init__(self, levelId)
        self._callObjList = []
        """ 待执行列表 """
        self.persistentWork = True
        if not hasattr(self, BaseService.SERVICE_KEY):
            self.__class__.stop()
            raise Exception("请通过 start方法 安全的启用服务")
        self._startListenAnnotation()
    
    def _findAllListenAnnotationData(self):
        for k in dir(self):
            v = getattr(self, k)    # type: object
            if hasattr(v, BaseService.LISTEN_DATA_KEY):
                dataObj = getattr(v, BaseService.LISTEN_DATA_KEY)   # type: ListenData
                yield (v, dataObj)
    
    def _startListenAnnotation(self):
        """ 加载监听注解 """
        for fun, data in self._findAllListenAnnotationData():
            ListenForEvent(data.eventName, self, fun)

    def _stopListenAnnotation(self):
        """ 停止监听注解 """
        for fun, data in self._findAllListenAnnotationData():
            UnListenForEvent(data.eventName, self, fun)
    
    def onCreate(self):
        """ 服务初始化事件 """
        pass

    def getID(self):
        """ 获取服务对象ID """
        return id(self)
    
    def OnTick(self):
        """ 组件Tick事件 建议使用onServiceUpdate管理服务更新 """
        SuperEntityCompCls.OnTick(self)
        self._updateCall()
        # UPDATE 更新触发逻辑
        self.onServiceUpdate()
    
    def OnRemove(self):
        """ 组件移除事件 建议使用onServiceStop管理服务停止逻辑 """
        SuperEntityCompCls.OnRemove(self)
        self._stopListenAnnotation()
        self.onServiceStop()
    
    def onServiceUpdate(self):
        """ 服务更新事件 默认每秒30次 """
        pass
    
    def onServiceStop(self):
        """ 服务停止事件 """
        pass

    def addCallFun(self, obj):
        """ 添加执行函数 """
        self._callObjList.append(obj)
    
    def _updateCall(self):
        if len(self._callObjList) <= 0:
            return
        for obj in self._callObjList:
            try:
                obj()
            except Exception:
                import traceback
                traceback.print_exc()
        self._callObjList = []

    @classmethod
    def getService(cls):
        # type: () -> BaseService
        """ 如果服务存在 返回服务实例 否则None """
        comp = cls.GetComp(levelId)
        if comp:
            return comp
        return None
    
    @classmethod
    def start(cls):
        """ 尝试启用服务 如果未启用 """
        comp = cls.getService()
        if comp:
            return comp
        obj = cls.__new__(cls)
        setattr(obj, BaseService.SERVICE_KEY, True)
        obj.__init__()
        obj.onCreate()
        return obj

    @classmethod
    def stop(cls):
        """ 尝试停用服务 如果已启用 """
        comp = cls.getService()
        if not comp:
            return
        comp.RemoveComp()

# class BaseChunkService(BaseService):
#     """ 基本区块服务 """
#     class ChunkData:
#         """ 区块信息 """
#         def __init__(self, minPos, maxPos, dm = -1):
#             # type: (tuple[float, float], tuple[float, float], int) -> None
#             self.minPos = minPos
#             self.maxPos = maxPos
#             self.dm = dm

#         def __eq__(self, other):  
#             if isinstance(other, BaseChunkService.ChunkData):  
#                 return self.minPos == other.minPos and self.maxPos == other.maxPos and self.dm == other.dm
#             return False
    
#         def __hash__(self):  
#             return hash((self.minPos, self.minPos, self.dm))

#     def __init__(self):
#         BaseService.__init__(self)

#     def getPlayerRenderChunks(self, playerId, _step = 16, _maxStep = 128):
#         """ [生成器] 获取特定玩家周围所渲染的区块信息 """
#         import itertools
#         chunks = set()  # type: set[BaseChunkService.ChunkData]
#         stopWork = False
#         comp = serverApi.GetEngineCompFactory().CreateChunkSource(levelId)
#         playerObj = Entity(playerId)
#         x, y, z = playerObj.FootPos
#         dm = playerObj.DimensionId
#         for i in range(0, _maxStep+1, _step):
#             if stopWork:
#                 break
#             for cx, cz in itertools.product(range(-i, i+1, _step), range(-i, i+1, _step)):
#                 pos = (x + cx, z + cz)
#                 if not comp.CheckChunkState(dm, (pos[0], y, pos[1])):
#                     stopWork = True
#                     break
#                 minPos = comp.GetChunkMinPos(pos)
#                 maxPos = comp.GetChunkMaxPos(pos)
#                 data = BaseChunkService.ChunkData(minPos, maxPos, dm)
#                 if data in chunks:
#                     continue
#                 chunks.add(data)
#                 yield data

#     def getAllRenderChunks(self, _step = 8, _maxStep = 128, dm = [0]):
#         """ [生成器] 获取所有玩家所渲染的区块信息 """
#         chunks = set()  # type: set[BaseChunkService.ChunkData]
#         dmSet = set(dm)
#         for playerId in serverApi.GetPlayerList():
#             dmId = Entity(playerId).DimensionId
#             # 去除无关维度的玩家
#             if not dmId in dmSet:
#                 continue
#             for _chunk in self.getPlayerRenderChunks(playerId, _step, _maxStep):
#                 if _chunk in chunks:
#                     continue
#                 chunks.add(_chunk)
#                 yield _chunk

