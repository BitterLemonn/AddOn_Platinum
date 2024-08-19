# -*- coding: utf-8 -*-
class BaseEntityType:
    """ 基本实体类型 """
    PLAYER = "minecraft:player"

class EntityParams:
    """ 实体参数 """
    def __init__(self,
        identifier = "",
        is_spawnable = True,
        is_summonable = False,
        is_experimental = False,
        runtime_identifier = "",
        events = [],
        **kwargs
    ):
        self.otherArgs = kwargs
        """ 其他参数 """
        self.identifier = identifier
        """ 实体标识符 """
        self.is_spawnable = is_spawnable
        """ 允许刷怪蛋生成 """
        self.is_summonable = is_summonable
        """ 允许命令生成 """
        self.is_experimental = is_experimental
        """ 是实验玩法的 """
        self.runtime_identifier = runtime_identifier
        """ 运行标识符 """
        self.eventsSet = set(events)
        """ 事件集合 """

