import logging

from QuModLibs.Client import *

minecraftEnum = clientApi.GetMinecraftEnum()


@AllowCall
def Swing():
    comp = clientApi.GetEngineCompFactory().CreatePlayer(playerId)
    comp.Swing()


@AllowCall
def PlaySound(data):
    soundName = data["soundName"]
    pos = data.get("pos", (0, 0, 0))
    volume = data.get("volume", 1)
    pitch = data.get("pitch", 1.0)
    targetId = data.get("targetId", -1)

    comp = clientApi.GetEngineCompFactory().CreateCustomAudio(levelId if targetId == -1 else targetId)
    comp.PlayCustomMusic(soundName, pos, volume, pitch, False, None if targetId == -1 else targetId)


@AllowCall
def PlayMusic(data):
    logging.debug("PlayMusic: " + str(data))
    musicName = data["musicName"]
    volume = data.get("volume", 1)
    loop = data.get("loop", False)
    comp = clientApi.GetEngineCompFactory().CreateCustomAudio(levelId)
    comp.DisableOriginMusic(True)
    isPlay = comp.PlayGlobalCustomMusic(musicName, volume, loop)


@Listen(Events.OnMusicStopClientEvent)
def OnMusicStopClientEvent(data):
    musicName = data["musicName"]
    if musicName.startswith("music.legend_forest"):
        comp = clientApi.GetEngineCompFactory().CreateCustomAudio(levelId)
        comp.DisableOriginMusic(False)
        clientApi.GetLevelId()


@AllowCall
def BindParticleEntity(data):
    particleName = data["particleName"]
    entityId = data["entityId"]
    boneName = data.get("boneName", "body")
    offset = data.get("offset", (0, 0, 0))
    rotation = data.get("rotation", (0, 0, 0))

    comp = clientApi.GetEngineCompFactory().CreateParticleSystem(None)
    comp.CreateBindEntity(particleName, entityId, boneName, offset, rotation)


@AllowCall
def PlayParticle(data):
    particleName = data["particleName"]
    pos = data.get("pos", (0, 0, 0))

    comp = clientApi.GetEngineCompFactory().CreateParticleSystem(playerId)
    pId = comp.Create(particleName)
    comp.SetPos(pId, pos)


@AllowCall
def SetShadowFalse(entityId):
    comp = clientApi.GetEngineCompFactory().CreateModel(entityId)
    comp.SetEntityShadowShow(False)


@AllowCall
def OpenCameraShakeAfterReset(delayTime):
    comp = clientApi.GetEngineCompFactory().CreatePlayerView(levelId)
    isOn = comp.GetToggleOption(minecraftEnum.OptionId.CAMERA_SHAKE)
    isOn = True if isOn == 1 else False
    clientApi.GetEngineCompFactory().CreateGame(levelId).AddTimer(
        delay=delayTime,
        func=comp.SetToggleOption,
        optionId=minecraftEnum.OptionId.CAMERA_SHAKE,
        isOn=isOn
    )
    comp.SetToggleOption(minecraftEnum.OptionId.CAMERA_SHAKE, True)
