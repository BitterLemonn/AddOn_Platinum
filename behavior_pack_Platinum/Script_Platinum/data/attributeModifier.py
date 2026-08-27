# coding=utf-8


def calculateModifiedValue(baseValue, modifiers, operationEnum):
    """按网易属性修饰符操作顺序计算 OperandCurrent。"""
    value = float(baseValue)
    for modifier in modifiers:
        if modifier["operation"] == operationEnum.OperationAddition:
            value += modifier["amount"]
    for modifier in modifiers:
        if modifier["operation"] == operationEnum.OperationMultiplyBase:
            value += baseValue * modifier["amount"]
    for modifier in modifiers:
        if modifier["operation"] == operationEnum.OperationMultiplyTotal:
            value *= 1.0 + modifier["amount"]
    for modifier in modifiers:
        if modifier["operation"] == operationEnum.OperationCap:
            value = min(value, modifier["amount"])
    return value


def calculateProtectionMultiplier(damageReduction):
    """按减伤比例计算伤害倍率。"""
    return max(0.0, 1.0 - damageReduction)


if __name__ == "__main__":
    assert calculateProtectionMultiplier(0) == 1.0
    assert abs(calculateProtectionMultiplier(-0.2) - 1.2) < 1e-9
    assert abs(calculateProtectionMultiplier(0.2) - 0.8) < 1e-9
    assert abs(
        calculateProtectionMultiplier(0.2)
        * calculateProtectionMultiplier(0.3)
        - 0.56
    ) < 1e-9
    assert calculateProtectionMultiplier(1.0) == 0.0
    assert calculateProtectionMultiplier(2.0) == 0.0
