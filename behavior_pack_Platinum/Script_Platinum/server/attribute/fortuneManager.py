# coding=utf-8
import random


class FortuneManager(object):
    """时运掉落管理器：注册方块后按自定义时运倍率重复模拟原始掉落。"""

    DEFAULT_FORTUNE_BLOCKS = frozenset(
        (
            "minecraft:coal_ore",
            "minecraft:deepslate_coal_ore",
            "minecraft:diamond_ore",
            "minecraft:deepslate_diamond_ore",
            "minecraft:emerald_ore",
            "minecraft:deepslate_emerald_ore",
            "minecraft:gold_ore",
            "minecraft:deepslate_gold_ore",
            "minecraft:iron_ore",
            "minecraft:deepslate_iron_ore",
            "minecraft:lapis_ore",
            "minecraft:deepslate_lapis_ore",
            "minecraft:redstone_ore",
            "minecraft:deepslate_redstone_ore",
            "minecraft:nether_gold_ore",
            "minecraft:nether_quartz_ore",
            "minecraft:copper_ore",
            "minecraft:deepslate_copper_ore",
        )
    )

    def __init__(self, registerDefaults=True):
        # type: (bool) -> None
        self._blockSet = set(self.DEFAULT_FORTUNE_BLOCKS) if registerDefaults else set()  # type: set[str]

    def registerBlock(self, blockName):
        # type: (str) -> bool
        """注册方块：玩家带时运等级破坏时取消引擎掉落，按自定义倍率独立重掷原始掉落表。"""
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

    def getRegisteredBlocks(self):
        # type: () -> list[str]
        """返回已注册时运方块的有序副本。"""
        return sorted(self._blockSet)

    @staticmethod
    def rollFortuneMultiplier(level):
        # type: (int) -> int
        """原版矿石时运算法：掷 randint(0, level + 1)。
        结果 < level 时倍率为 (结果 + 2)；结果 >= level（权重 2，倍率 2..level+1 各权重 1）时倍率为 1。"""
        if level <= 0:
            return 1
        # 权重展开：1 有两份（index level 与虚拟 index level+1），2..level+1 各一份
        roll = random.randint(0, level + 1)
        return roll + 2 if roll < level else 1
