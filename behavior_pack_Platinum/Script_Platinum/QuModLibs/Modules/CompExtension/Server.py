# -*- coding: utf-8 -*-
from ...Server import SuperEntityCompCls, serverApi, ListenForEvent, Events, Entity
from ...Util import errorPrint

lambda: "组件扩展 By Zero123"

class ProjectileHitComponent(SuperEntityCompCls):
    """ 抛射物碰撞代理组件 """

    _enable = False
    _entityQuoteMaps = {}       # type: dict[str, int]
    """ 实体引用表 记录实体抛射组件施加次数 以便剔除与优化 """

    @staticmethod
    def _getAllProjectileHitComponent(entityId):
        # type: (str) -> list[ProjectileHitComponent]
        for comp in ProjectileHitComponent.getSubComps(entityId):
            if isinstance(comp, ProjectileHitComponent):
                yield comp

    @staticmethod
    def _ProjectileDoHitEffectEvent(args):
        """ 抛射物碰撞引擎事件 """
        entityId = args["id"]
        if not entityId in ProjectileHitComponent._entityQuoteMaps:
            return
        entityPos = (args["x"], args["y"], args["z"])
        hitTargetType = args["hitTargetType"]
        if hitTargetType == "BLOCK":
            # 方块处理
            hitFace = args["hitFace"]
            blockPos = (args["blockPosX"], args["blockPosY"], args["blockPosZ"])
            for comp in ProjectileHitComponent._getAllProjectileHitComponent(entityId):
                comp.hitPos = entityPos
                try:
                    comp.onHitBlock(blockPos, hitFace)
                except Exception as e:
                    errorPrint("{} 在方块碰撞时发生异常 {}".format(comp, e))
        elif hitTargetType == "ENTITY":
            # 实体处理
            targetId = args["targetId"]
            for comp in ProjectileHitComponent._getAllProjectileHitComponent(entityId):
                comp.hitPos = entityPos
                try:
                    comp.onHitEntity(targetId)
                except Exception as e:
                    errorPrint("{} 在实体碰撞时发生异常 {}".format(comp, e))
    
    @staticmethod
    def _enableEvent():
        """ 启用全局事件管理 """
        if ProjectileHitComponent._enable == False:
            ProjectileHitComponent._enable = True
            ListenForEvent(Events.ProjectileDoHitEffectEvent, ProjectileHitComponent, ProjectileHitComponent._ProjectileDoHitEffectEvent)

    def __init__(self, entityId):
        SuperEntityCompCls.__init__(self, entityId)
        self.sourceId = serverApi.GetEngineCompFactory().CreateBulletAttributes(self.entityId).GetSourceEntityId()
        """ 抛射物源ID 通常指物主 """
        self.hitPos = (0, 0, 0)                  # type: tuple[float]
        """ 碰撞坐标 由引擎提供 """
        ProjectileHitComponent._enableEvent()
        
        # 引用计数
        if not entityId in ProjectileHitComponent._entityQuoteMaps:
            ProjectileHitComponent._entityQuoteMaps[entityId] = 0
        ProjectileHitComponent._entityQuoteMaps[entityId] += 1

    def onHitEntity(self, targetId):
        """ 抛射物碰撞实体触发 """
        pass

    def onHitBlock(self, blockPos, hitFace = -1):
        """ 抛射物碰撞方块触发 """
        pass
    
    def OnRemove(self):
        SuperEntityCompCls.OnRemove(self)

        # 引用计数减消 实现自动回收
        if not self.entityId in ProjectileHitComponent._entityQuoteMaps:
            return
        
        ProjectileHitComponent._entityQuoteMaps[self.entityId] -= 1
        if ProjectileHitComponent._entityQuoteMaps[self.entityId] <= 0:
            del ProjectileHitComponent._entityQuoteMaps[self.entityId]

class EntityComponent(SuperEntityCompCls):
    """ [Beta] 实体代理组件 """

    _enable = False
    _entityQuoteMaps = {}       # type: dict[str, int]
    """ 实体引用表 """

    @staticmethod
    def _getAllEntityComponent(entityId):
        # type: (str) -> list[EntityComponent]
        for comp in EntityComponent.getSubComps(entityId):
            if isinstance(comp, EntityComponent):
                yield comp
    
    @staticmethod
    def _ActuallyHurtServerEvent(args):
        hurtOtherId = args["srcId"]
        hurtEntityId = args["entityId"]
        if hurtOtherId in EntityComponent._entityQuoteMaps:
            # 实体伤害他人
            for comp in EntityComponent._getAllEntityComponent(hurtOtherId):
                try:
                    comp.hurtServerEvent = args
                    comp.onHurtOther(hurtEntityId)
                except Exception as e:
                    errorPrint("组件在onHurtOther事件发生异常 {}".format(e))

        if hurtEntityId in EntityComponent._entityQuoteMaps:
            # 实体受伤
            for comp in EntityComponent._getAllEntityComponent(hurtEntityId):
                try:
                    comp.hurtServerEvent = args
                    comp.onHurt(hurtOtherId)
                except Exception as e:
                    errorPrint("组件在onHurt事件发生异常 {}".format(e))

    @staticmethod
    def _enableEvent():
        """ 启用全局事件管理 """
        if EntityComponent._enable == False:
            EntityComponent._enable = True
            ListenForEvent(Events.ActuallyHurtServerEvent, EntityComponent, EntityComponent._ActuallyHurtServerEvent)

    def __init__(self, entityId):
        SuperEntityCompCls.__init__(self, entityId)
        self.entityObj = Entity(entityId)
        self.hurtServerEvent = {}                   # type: dict
        """ 由引擎传递的上一次受伤事件args """
        EntityComponent._enableEvent()
        
        # 引用计数
        if not entityId in EntityComponent._entityQuoteMaps:
            EntityComponent._entityQuoteMaps[entityId] = 0
        EntityComponent._entityQuoteMaps[entityId] += 1

    def onHurt(self, targetId = None):
        """ 受伤事件 """
        pass
    
    def onHurtOther(self, targetId = None):
        """ 实体对他人造成伤害事件 """
        pass

    def OnRemove(self):
        SuperEntityCompCls.OnRemove(self)

        # 引用计数减消 实现自动回收
        if not self.entityId in EntityComponent._entityQuoteMaps:
            return
        
        EntityComponent._entityQuoteMaps[self.entityId] -= 1
        if EntityComponent._entityQuoteMaps[self.entityId] <= 0:
            del EntityComponent._entityQuoteMaps[self.entityId]