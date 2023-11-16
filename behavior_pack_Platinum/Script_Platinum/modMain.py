# coding=utf-8
import logging

from QuModLibs.QuMod import *
import commonConfig

MyMod = EasyMod()


def SERVER():
    """ 服务端工作作用域 """
    from QuModLibs.Server import setSystem
    import Script_Main.platinumServer as platinumServer
    setSystem(platinumServer)
    import Script_UI.baubleServer as baubleServer
    setSystem(baubleServer)
    import Script_Main.broadcasterServer as broadcasterServer
    setSystem(broadcasterServer)

    # 注册原版系统
    import mod.server.extraServerApi as serverApi
    serverApi.RegisterSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER,
                             "Script_Platinum.Script_Main.broadcasterServer.BroadcasterServer")
    serverApi.RegisterSystem("buildInBauble", "buildInBaubleServer",
                             "Script_Platinum.buildInBaubleServer.BuildInBaubleServer")


def CLIENT():
    """ 客户端工作作用域 """
    from QuModLibs.Client import setSystem
    import Script_Main.platinumClient as platinumClient
    setSystem(platinumClient)
    import Script_UI.baubleClient as baubleClient
    setSystem(baubleClient)
    import Script_Main.broadcasterClient as broadcasterClient
    setSystem(broadcasterClient)

    # 注册原版系统
    import mod.client.extraClientApi as clientApi
    clientApi.RegisterSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_CLIENT,
                             "Script_Platinum.Script_Main.broadcasterClient.BroadcasterClient")
    isR = clientApi.RegisterSystem("buildInBauble", "buildInBaubleClient",
                                   "Script_Platinum.buildInBaubleClient.BuildInBaubleClient")


MyMod.addServerFunc(SERVER)
MyMod.addClientFunc(CLIENT)
