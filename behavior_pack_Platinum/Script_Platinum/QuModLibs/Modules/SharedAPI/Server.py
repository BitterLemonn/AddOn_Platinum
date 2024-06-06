# -*- coding: utf-8 -*-
from ...Server import serverApi, SuperEntityCompCls
from Util import SharedBox, _DEFAULT

lambda: "By Zero123"

class ImmuneDamageComp(SuperEntityCompCls):
    """ 免疫伤害组件 """
    def __init__(self, entityId):
        SuperEntityCompCls.__init__(self, entityId)
        self.sharedBox = SharedBox(
            lambda: serverApi.GetEngineCompFactory().CreateHurt(entityId).ImmuneDamage(True),
            lambda: self.RemoveComp()
        )
    
    def OnRemove(self):
        SuperEntityCompCls.OnRemove(self)
        self.sharedBox.free()
        serverApi.GetEngineCompFactory().CreateHurt(self.entityId).ImmuneDamage(False)

class EntitySharedAPI:
    """ 实体共享API 基于引用计数管理 """
    @staticmethod
    def immuneDamage(entityId, state = True, key = _DEFAULT):
        """ 设置实体是否免疫伤害(该属性不一定存档)
            state 为True时引用次数+1 否则-1 基于Key值处理边界
        """
        if state:
            comp = ImmuneDamageComp.GetComp(entityId)
            if not comp:
                ImmuneDamageComp.create(entityId)

        comp = ImmuneDamageComp.GetComp(entityId)   # type: ImmuneDamageComp | None
        if comp and state:
            comp.sharedBox.increaseRefCountWithKey(key)
        elif comp and not state:
            comp.sharedBox.decreaseRefCountWithKey(key)