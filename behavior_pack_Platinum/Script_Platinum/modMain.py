# -*- coding: utf-8 -*-
from . import commonConfig
from Script_Platinum.QuModLibs.QuMod import *

platinum = EasyMod()

# 13829 11:24
# 14735 12:17
# 17433 14:51
# 18249 15:36
# 18643 15:55
# 19119 16:52

# -------------------server-------------------
platinum.Server("server.server")
platinum.Server("server.player.playerBaubleSlot")
platinum.Server("server.player.playerBaubleInfo")
platinum.Server("server.items.itemService")
# -----------
platinum.regNativePyServer(
    commonConfig.PLATINUM_BROADCAST_SERVER,
    "platinumRegistryServer",
    "server.inner.innerRegistry.InnerServerRegistry",
)
platinum.regNativePyServer(
    commonConfig.PLATINUM_NAMESPACE,
    commonConfig.PLATINUM_BROADCAST_SERVER,
    "server.vanilla.boardcastServer.BroadcasterServer",
)
platinum.regNativePyServer(
    commonConfig.PLATINUM_NAMESPACE,
    "buildInBauble",
    "server.inner.baubleServer.BaubleServer",
)

# -------------------client-------------------
platinum.Client("client.player.playerBaubleSlot")
platinum.Client("client.ui.baubleUi")
