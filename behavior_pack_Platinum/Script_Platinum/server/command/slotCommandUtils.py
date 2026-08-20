# coding=utf-8

import uuid


MAX_SLOT_COUNT = 107
COMMAND_SLOT_ID_PREFIX = "platinum_command_slot_"


def isValidSlotCount(count):
    return not isinstance(count, bool) and isinstance(count, (int, long)) and 1 <= count <= MAX_SLOT_COUNT


def createCommandSlotIds(existingSlotIds, count):
    existingSlotIds = set(existingSlotIds)
    slotIds = []
    while len(slotIds) < count:
        slotId = COMMAND_SLOT_ID_PREFIX + uuid.uuid4().hex
        if slotId not in existingSlotIds:
            existingSlotIds.add(slotId)
            slotIds.append(slotId)
    return slotIds


def getDeletableCommandSlots(slots, slotType, ownedSlotIds, count, allowDefault):
    result = []
    ownedSlotIds = set(ownedSlotIds)
    for slot in reversed(slots):
        if (
            slot.slotType == slotType
            and slot.isCommandAdded
            and slot.identifier in ownedSlotIds
            and (allowDefault or not slot.isDefault)
        ):
            result.append(slot)
            if len(result) == count:
                break
    return result


if __name__ == "__main__":
    class _Slot(object):
        def __init__(self, identifier, slotType, isDefault=False, isCommandAdded=True):
            self.identifier = identifier
            self.slotType = slotType
            self.isDefault = isDefault
            self.isCommandAdded = isCommandAdded

    assert isValidSlotCount(1)
    assert isValidSlotCount(MAX_SLOT_COUNT)
    assert not isValidSlotCount(0)
    assert not isValidSlotCount(MAX_SLOT_COUNT + 1)
    generatedIds = createCommandSlotIds([], 2)
    assert len(generatedIds) == len(set(generatedIds)) == 2
    slots = [_Slot("a", "hand"), _Slot("b", "hand", True), _Slot("c", "belt")]
    assert [slot.identifier for slot in getDeletableCommandSlots(slots, "hand", ["a", "b"], 2, False)] == ["a"]
    assert [slot.identifier for slot in getDeletableCommandSlots(slots, "hand", ["a", "b"], 2, True)] == ["b", "a"]
