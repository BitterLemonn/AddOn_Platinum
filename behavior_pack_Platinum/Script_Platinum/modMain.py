# coding=utf-8
import logging

from QuModLibs.QuMod import *
import commonConfig

MyMod = EasyMod()

# 服务端
MyMod.Server("Script_Main.broadcasterServer")
MyMod.Server("Script_Main.platinumServer")
MyMod.Server("Script_UI.baubleServer")
MyMod.regNativePyServer(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER,
                        "Script_Main.broadcasterServer.BroadcasterServer")
MyMod.regNativePyServer("buildInBauble", "buildInBaubleServer",
                        "buildInBaubleServer.BuildInBaubleServer")

MyMod.Client("Script_UI.baubleClient")
MyMod.Client("Script_UI.baubleDatabase")
MyMod.Client("Script_Main.broadcasterClient")
MyMod.Client("animSoundClient")
MyMod.regNativePyClient(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_CLIENT,
                        "Script_Main.broadcasterClient.BroadcasterClient")

# def SERVER():
#     """ 服务端工作作用域 """
#     from QuModLibs.Server import setSystem
#     from QuModLibs.Server import GetSystem
#     if not GetSystem(commonConfig.PLATINUM_SERVER):
#         import Script_Main.platinumServer as platinumServer
#         setSystem(platinumServer, commonConfig.PLATINUM_SERVER)
#         import Script_UI.baubleServer as baubleServer
#         setSystem(baubleServer, commonConfig.PLATINUM_BAUBLE_SERVER)
#         import Script_Main.broadcasterServer as broadcasterServer
#         setSystem(broadcasterServer, "QU_BROADCAST_SERVER")
#
#         # 注册原版系统
#         serverApi.RegisterSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER,
#                                  "Script_Platinum.Script_Main.broadcasterServer.BroadcasterServer")
#         serverApi.RegisterSystem("buildInBauble", "buildInBaubleServer",
#                                  "Script_Platinum.buildInBaubleServer.BuildInBaubleServer")
#
#
# def CLIENT():
#     """ 客户端工作作用域 """
#     from QuModLibs.Client import setSystem
#     from QuModLibs.Client import GetSystem
#     if not GetSystem(commonConfig.PLATINUM_CLIENT):
#         import Script_Main.platinumClient as platinumClient
#         setSystem(platinumClient, commonConfig.PLATINUM_CLIENT)
#         import Script_UI.baubleNewClient as baubleNewClient
#         setSystem(baubleNewClient, commonConfig.PLATINUM_BAUBLE_CLIENT)
#         import Script_Main.broadcasterClient as broadcasterClient
#         setSystem(broadcasterClient, "QU_BROADCAST_CLIENT")
#         import Script_UI.tipsClient as tipsClient
#         setSystem(tipsClient)
#
#         # 注册原版系统
#         import mod.client.extraClientApi as clientApi
#         clientApi.RegisterSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_CLIENT,
#                                  "Script_Platinum.Script_Main.broadcasterClient.BroadcasterClient")
#         clientApi.RegisterSystem("buildInBauble", "buildInBaubleClient",
#                                  "Script_Platinum.buildInBaubleClient.BuildInBaubleClient")
#
#
# MyMod.addServerFunc(SERVER)
# MyMod.addClientFunc(CLIENT)
