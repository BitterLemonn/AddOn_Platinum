# -*- coding: utf-8 -*-
from . import commonConfig
from Script_Platinum.QuModLibs.QuMod import *

platinum = EasyMod()

# -------------------server-------------------
platinum.Server("server.server")
platinum.Server("server.registry.slotRegistry")
platinum.Server("server.player.playerBaubleSlot")
platinum.Server("server.player.playerBaubleInfo")
platinum.Server("server.entity.entityBaubleInfo")
platinum.Server("server.attribute.attributeModifier")
platinum.Server("server.player.baubleContainer")
platinum.Server("server.items.itemService")
platinum.Server("server.command.commandServer")
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
platinum.Client("client.player.playerBaubleInfo")
platinum.Client("client.entity.entityBaubleInfo")
platinum.Client("client.player.playerBaubleSlot")
platinum.Client("client.attribute.playerAttributeClientService")
platinum.Client("client.ui.baubleUi")
# -----------
platinum.regNativePyClient(
    commonConfig.PLATINUM_NAMESPACE,
    commonConfig.PLATINUM_BROADCAST_CLIENT,
    "client.vanilla.boardcastClient.BoardcastClient",
)
