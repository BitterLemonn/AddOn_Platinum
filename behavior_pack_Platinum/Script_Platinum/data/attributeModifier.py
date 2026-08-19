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