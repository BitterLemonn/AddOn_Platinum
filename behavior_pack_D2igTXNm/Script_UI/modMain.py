# -*- coding: utf-8 -*-
from QuModLibs.QuMod import *

MyMod = EasyMod()


def SERVER():
    """ 服务端工作作用域 """
    from QuModLibs.Server import setSystem
    import UIServer.baubleServer as Server
    setSystem(Server)

    # 注册原版系统
    import mod.server.extraServerApi as serverApi
    serverApi.RegisterSystem("..", "..", "..")


def CLIENT():
    """ 客户端工作作用域 """
    from QuModLibs.Client import setSystem
    import UIClient.baubleClient as Client
    setSystem(Client)

    # 注册原版系统
    import mod.client.extraClientApi as clientApi
    clientApi.RegisterSystem("..", "..", "..")


MyMod.addServerFunc(SERVER)
MyMod.addClientFunc(CLIENT)
