# coding=utf-8
from QuModLibs.QuMod import *

MyMod = EasyMod()


def SERVER():
    """ 服务端工作作用域 """
    from QuModLibs.Server import setSystem
    import Scrpit_Main.platinumServer as platinumServer
    setSystem(platinumServer)
    import Script_UI.baubleServer as baubleServer
    setSystem(baubleServer)


def CLIENT():
    """ 客户端工作作用域 """
    from QuModLibs.Client import setSystem
    import Scrpit_Main.platinumClient as platinumClient
    setSystem(platinumClient)
    import Script_UI.baubleClient as baubleClient
    setSystem(baubleClient)


MyMod.addServerFunc(SERVER)
MyMod.addClientFunc(CLIENT)
