# coding=utf-8
import logging

from QuModLibs.QuMod import *
import commonConfig

MyMod = EasyMod()

# 服务端
MyMod.Server("Script_Main.broadcasterServer")
MyMod.Server("Script_Main.platinumServer")
MyMod.Server("Script_UI.baubleServer")
MyMod.Server("DataManager.baubleSlotServerService")
MyMod.regNativePyServer(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER,
                        "Script_Main.broadcasterServer.BroadcasterServer")
MyMod.regNativePyServer("buildInBauble", "buildInBaubleServer",
                        "buildInBaubleServer.BuildInBaubleServer")

MyMod.Client("Script_UI.baubleClient")
MyMod.Client("DataManager.baubleDatabase")
MyMod.Client("Script_Main.broadcasterClient")
MyMod.Client("animSoundClient")
MyMod.Client("Script_UI.tipsClient")
MyMod.regNativePyClient(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_CLIENT,
                        "Script_Main.broadcasterClient.BroadcasterClient")
MyMod.regNativePyClient("buildInBauble", "buildInBaubleClient",
                        "buildInBaubleClient.BuildInBaubleClient")
