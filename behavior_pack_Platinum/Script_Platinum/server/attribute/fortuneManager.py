# coding=utf-8


class FortuneManager(object):
    """时运掉落管理器：注册方块到修饰符时运掉落计算中（掉落由引擎模拟挖掘接口按原版掉落表 + 时运等级生成）。"""

    # 原版吃时运的矿石；铁矿/主世界金矿掉落本体不吃时运，不注册
    DEFAULT_FORTUNE_BLOCKS = frozenset((
        "minecraft:coal_ore",
        "minecraft:deepslate_coal_ore",
        "minecraft:diamond_ore",
        "minecraft:deepslate_diamond_ore",
        "minecraft:emerald_ore",
        "minecraft:deepslate_emerald_ore",
        "minecraft:lapis_ore",
        "minecraft:deepslate_lapis_ore",
        "minecraft:redstone_ore",
        "minecraft:deepslate_redstone_ore",
        "minecraft:nether_gold_ore",
        "minecraft:nether_quartz_ore",
        "minecraft:copper_ore",
        "minecraft:deepslate_copper_ore",
    ))

    def __init__(self, registerDefaults=True):
        # type: (bool) -> None
        self._blockSet = set(self.DEFAULT_FORTUNE_BLOCKS) if registerDefaults else set()  # type: set[str]

    def registerBlock(self, blockName):
        # type: (str) -> bool
        """注册方块：玩家带时运等级破坏时取消引擎掉落，改用引擎模拟挖掘接口带时运等级重新掉落。"""
        if not isinstance(blockName, str) or not blockName:
            return False
        self._blockSet.add(blockName)
        return True

    def unregisterBlock(self, blockName):
        # type: (str) -> bool
        if blockName in self._blockSet:
            self._blockSet.remove(blockName)
            return True
        return False

    def isRegistered(self, blockName):
        # type: (str) -> bool
        return blockName in self._blockSet
