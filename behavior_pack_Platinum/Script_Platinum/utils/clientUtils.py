# coding=utf-8
from Script_Platinum.QuModLibs.Client import *

compFactory = clientApi.GetEngineCompFactory()


@AllowCall
def PlaySound(data):
    soundName = data["soundName"]
    pos = data.get("pos", (0, 0, 0))
    volume = data.get("volume", 1)
    pitch = data.get("pitch", 1.0)
    targetId = data.get("targetId", -1)

    comp = clientApi.GetEngineCompFactory().CreateCustomAudio(levelId if targetId == -1 else targetId)
    comp.PlayCustomMusic(soundName, pos, volume, pitch, False, None if targetId == -1 else targetId)
