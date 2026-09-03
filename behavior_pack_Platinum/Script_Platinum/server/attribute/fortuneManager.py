# coding=utf-8
import random
import re

try:
    stringTypes = (str, unicode)
    regexPatternType = re._pattern_type
except (NameError, AttributeError):
    stringTypes = (str,)
    regexPatternType = getattr(re, "Pattern", type(re.compile("")))


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
        self._patternDict = {}
        self._blacklistSet = set()  # type: set[str]
        self._blacklistPatternDict = {}

    def _normalizePattern(self, pattern):
        """解析并返回 (pattern_str, compiled_regex)，非法时返回 (None, None)。"""
        if isinstance(pattern, regexPatternType):
            return pattern.pattern, pattern
        if isinstance(pattern, stringTypes) and pattern:
            try:
                compiled = re.compile(pattern)
                return pattern, compiled
            except re.error:
                return None, None
        return None, None

    def registerBlock(self, pattern):
        """注册方块或正则表达式：玩家带时运等级破坏时取消引擎掉落，按自定义倍率独立重掷原始掉落表。"""
        patternStr, compiled = self._normalizePattern(pattern)
        if not patternStr:
            return False
        # 如果是无特殊正则字符的普通方块ID，优先放入集合以供 O(1) 检索
        self._patternDict[patternStr] = compiled
        self._blockSet.add(patternStr)
        return True

    def unregisterBlock(self, pattern):
        # type: (Any) -> bool
        patternStr, _ = self._normalizePattern(pattern)
        if not patternStr:
            return False
        removed = False
        if patternStr in self._blockSet:
            self._blockSet.remove(patternStr)
            removed = True
        if patternStr in self._patternDict:
            del self._patternDict[patternStr]
            removed = True
        return removed

    def registerBlacklist(self, pattern):
        # type: (Any) -> bool
        """注册黑名单方块或正则表达式：命中黑名单的方块绝不触发时运掉落。"""
        patternStr, compiled = self._normalizePattern(pattern)
        if not patternStr:
            return False
        self._blacklistPatternDict[patternStr] = compiled
        self._blacklistSet.add(patternStr)
        return True

    def unregisterBlacklist(self, pattern):
        # type: (Any) -> bool
        """反注册黑名单方块或正则表达式规则。"""
        patternStr, _ = self._normalizePattern(pattern)
        if not patternStr:
            return False
        removed = False
        if patternStr in self._blacklistSet:
            self._blacklistSet.remove(patternStr)
            removed = True
        if patternStr in self._blacklistPatternDict:
            del self._blacklistPatternDict[patternStr]
            removed = True
        return removed

    def isBlacklisted(self, blockName):
        # type: (str) -> bool
        """检查方块是否处于黑名单中。"""
        if not isinstance(blockName, stringTypes) or not blockName:
            return False
        if blockName in self._blacklistSet:
            return True
        for pattern in self._blacklistPatternDict.values():
            if pattern.search(blockName):
                return True
        return False

    def isRegistered(self, blockName):
        # type: (str) -> bool
        if not isinstance(blockName, stringTypes) or not blockName:
            return False
        # 黑名单优先级最高，命中黑名单则直接不参与时运
        if self.isBlacklisted(blockName):
            return False
        if blockName in self._blockSet:
            return True
        for pattern in self._patternDict.values():
            if pattern.search(blockName):
                return True
        return False

    def getRegisteredBlocks(self):
        # type: () -> list[str]
        """返回已注册时运方块与正则规则的有序列表。"""
        allKeys = set(self._blockSet)
        allKeys.update(self._patternDict.keys())
        return sorted(allKeys)

    def getBlacklistBlocks(self):
        # type: () -> list[str]
        """返回已注册黑名单方块与正则规则的有序列表。"""
        allKeys = set(self._blacklistSet)
        allKeys.update(self._blacklistPatternDict.keys())
        return sorted(allKeys)

    @staticmethod
    def rollFortuneMultiplier(level):
        # type: (int) -> int
        """原版矿石时运算法：掷 randint(0, level + 1)。
        结果 < level 时倍率为 (结果 + 2)；结果 >= level（权重 2，倍率 2..level+1 各权重 1）时倍率为 1。"""
        if level <= 0:
            return 1
        roll = random.randint(0, level + 1)
        return roll + 2 if roll < level else 1
