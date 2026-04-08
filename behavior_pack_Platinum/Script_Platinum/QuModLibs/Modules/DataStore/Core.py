# -*- coding: utf-8 -*-
lambda: "By Zero123"

class BaseClsStoreMeta(type):
    """
    数据管理元类
    """
    def __setattr__(cls, name, value):
        # type: (str, object) -> None
        if issubclass(cls, BaseStoreCls) and not name.startswith("__"):
            if not type.__getattribute__(cls, "__mInit__"):
                type.__setattr__(cls, "__mInit__", True)
                type.__getattribute__(cls, "mLoadUserData")()
            oldValue = None
            try:
                oldValue = type.__getattribute__(cls, name)
            except AttributeError:
                pass
            if oldValue != value:
                type.__setattr__(cls, name, value)
                # cls.mSignNeedUpdate()
                type.__getattribute__(cls, "mSignNeedUpdate")()
                return
        return type.__setattr__(cls, name, value)
    
    def __getattribute__(cls, name):
        # type: (str) -> object
        if issubclass(cls, BaseStoreCls) and not name.startswith("__"):
            if not type.__getattribute__(cls, "__mInit__"):
                type.__setattr__(cls, "__mInit__", True)
                type.__getattribute__(cls, "mLoadUserData")()
        return type.__getattribute__(cls, name)

class BaseStoreCls(object):
    """
    基础数据存储类
    通过元类实现数据的存取
    继承该类的子类可以直接通过类属性的方式存取数据
    """
    __metaclass__ = BaseClsStoreMeta
    __mInit__ = False

    @classmethod
    def mSignNeedUpdate(cls):
        pass

    @classmethod
    def mLoadUserData(cls):
        pass

    @classmethod
    def mSaveUserData(cls):
        pass

    @classmethod
    def mGenClsAttrNames(cls):
        for name in dir(cls):
            if not name.startswith("__") and not callable(getattr(cls, name)):
                yield name

    @classmethod
    def mGetClsAttrNames(cls):
        return list(cls.mGenClsAttrNames())

def PACK_DATAS(datas):
    # type: (dict[str, object]) -> dict
    """
    打包数据
    """
    import pickle
    packed = {}
    for k, v in datas.items():
        if k.startswith("__"):
            continue
        # 针对基础类型进行优化存储
        if isinstance(v, (int, float, str, bool)) or v is None:
            packed[k] = v
        else:
            packed[k] = {"p": pickle.dumps(v)}
    return packed

def UNPACK_DATAS(packed):
    # type: (dict[str, object]) -> dict
    """
    解包数据
    """
    import pickle
    datas = {}
    for k, v in packed.items():
        if k.startswith("__"):
            continue
        if isinstance(v, dict) and "p" in v:
            try:
                datas[k] = pickle.loads(v["p"])
            except Exception:
                datas[k] = None
        else:
            datas[k] = v
    return datas

class BaseAutoStoreCls(BaseStoreCls):
    """
    自动保存数据存储类
    继承该类的子类可以自动保存数据
    """
    __VERSION__ = 1
    __AUTO_SAVE_INTERVAL__ = 8.0
    __IS_CLIENT__ = False
    __ENV_DESTROY_HANDLER__ = False
    __SAVED_FULL_NAME__ = ""
    __SAVED_MOD_KEY_NAME__ = ""
    __NEED_SAVE__ = False

    @classmethod
    def mPackClsDatas(cls):
        """ 打包类属性数据 """
        srcAttrs = {}
        for name in cls.mGenClsAttrNames():
            srcAttrs[name] = getattr(cls, name)
        return {
            "version": cls.__VERSION__,
            "datas": PACK_DATAS(srcAttrs)
        }

    @classmethod
    def mUnpackClsDatas(cls, packed):
        # type: (dict | None) -> dict
        if packed is None or not isinstance(packed, dict):
            return {}
        version = packed.get("version", cls.__VERSION__)
        datas = UNPACK_DATAS(packed.get("datas", {}))
        if version != cls.__VERSION__:
            # 版本不符, 丢弃数据
            return {}
        return datas

    @classmethod
    def mSignNeedUpdate(cls):
        if cls.__NEED_SAVE__:
            return
        cls.__NEED_SAVE__ = True
        cls.mRegLazyAutoSave()

    @classmethod
    def mRegLazyAutoSave(cls):
        if not cls.__ENV_DESTROY_HANDLER__:
            cls.__ENV_DESTROY_HANDLER__ = True
            cls.mInitEnvDestroyHandler()
        if cls.__IS_CLIENT__:
            import mod.client.extraClientApi as clientApi
            comp = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLevelId())
            comp.AddTimer(cls.__AUTO_SAVE_INTERVAL__, cls.mSaveUserData)
        else:
            import mod.server.extraServerApi as serverApi
            comp = serverApi.GetEngineCompFactory().CreateGame(serverApi.GetLevelId())
            comp.AddTimer(cls.__AUTO_SAVE_INTERVAL__, cls.mSaveUserData)

    @classmethod
    def mSaveUserData(cls):
        if not cls.__NEED_SAVE__:
            return
        cls.__NEED_SAVE__ = False
        cls._mSaveUserData()

    @classmethod
    def _mSaveUserData(cls):
        pass

    @classmethod
    def mLazyGameOverHandler(cls):
        cls.mSaveUserData()

    @classmethod
    def mInitEnvDestroyHandler(cls):
        if cls.__IS_CLIENT__:
            from ...Systems.Loader.Client import LoaderSystem
            LoaderSystem.REG_DESTROY_CALL_FUNC(cls.mLazyGameOverHandler)
            return
        from ...Systems.Loader.Server import LoaderSystem
        LoaderSystem.REG_DESTROY_CALL_FUNC(cls.mLazyGameOverHandler)

    @classmethod
    def mGetSavedFullName(cls):
        if cls.__SAVED_FULL_NAME__:
            # 引用用户自定义fullName
            return cls.__SAVED_FULL_NAME__
        elif cls.__SAVED_MOD_KEY_NAME__:
            from ...IN import ModDirName
            return "{}.{}".format(ModDirName, cls.__SAVED_MOD_KEY_NAME__)
        # 自动生成fullName
        return "{}.{}".format(cls.__module__, cls.__name__)

    @classmethod
    def mergeDataCls(cls, targetCls):
        # type: (type) -> None
        """ 用于合并其他数据类的数据到当前类(适用于旧版数据类升级)
        ```python
        # mergeDataCls仅从运行时数据合并，如果需要拉取旧版数据仍然需要确保AutoSave工作。
        @QuDataStorage.AutoSave(1)
        class DataStore:
            VAR1 = 123
            VAR2 = "Hello"

        class NewDataStore(ServerAutoStoreCls):
            OLD_DATA_SYNC_STATE = False
            VAR1 = 0
            VAR2 = ""

        if not NewDataStore.OLD_DATA_SYNC_STATE:
            # 自动合并(仅执行一次)
            NewDataStore.OLD_DATA_SYNC_STATE = True
            NewDataStore.mergeDataCls(DataStore)
        ```
        """
        for k in dir(targetCls):
            v = getattr(targetCls, k)
            if not k.startswith("__") and not callable(v):
                setattr(cls, k, v)

    @classmethod
    def updateOldDataCls(cls, oldCls):
        # type: (type) -> None
        """
        自动合并升级旧数据类到新数据类（随后丢弃老数据类）
        ```python
        # @QuDataStorage.AutoSave(1)
        # updateOldDataCls从磁盘中读取数据，不再需要AutoSave拉取，需禁用装饰器
        class DataStore:
            VAR1 = 123
            VAR2 = "Hello"

        class NewDataStore(DataStore, ServerAutoStoreCls):
            # 继承旧版数据兼容层
            pass
        
        # 自动合并(若需极致性能还可以额外维护一个状态值避免二次IO)
        NewDataStore.updateOldDataCls(DataStore)
        ```
        """
        if not issubclass(cls, oldCls):
            raise TypeError("新数据类必须继承旧版数据类确保数据兼容性")
        from ....QuModLibs.Util import ObjectConversion
        cls._updateOldDataCls(ObjectConversion.getClsPathWithClass(oldCls))
    
    @classmethod
    def _updateOldDataCls(cls, oldDataKey):
        pass