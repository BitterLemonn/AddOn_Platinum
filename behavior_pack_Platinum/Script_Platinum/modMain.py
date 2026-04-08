from . import commonConfig
from Script_Platinum.QuModLibs.QuMod import *

platinum = EasyMod()


@PRE_SERVER_LOADER_HOOK
def serverRegister():
    platinum.Server("server.server")
    platinum.Server("server.player.playerBaubleSlot")
    platinum.Server("server.inner.innerService")
    # -----------
    platinum.regNativePyServer(
        commonConfig.PLATINUM_NAMESPACE,
        commonConfig.PLATINUM_BROADCAST_SERVER,
        "server.vanilla.boardcastServer.BroadcasterServer",
    )


@PRE_CLIENT_LOADER_HOOK
def clientRegister():
    platinum.Client("client.player.playerBaubleSlot")
