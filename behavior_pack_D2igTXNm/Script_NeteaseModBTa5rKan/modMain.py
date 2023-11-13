# -*- coding: utf-8 -*-

from mod.common.mod import Mod


@Mod.Binding(name="Script_NeteaseModBTa5rKan", version="0.0.1")
class Script_NeteaseModBTa5rKan(object):

    def __init__(self):
        pass

    @Mod.InitServer()
    def Script_NeteaseModBTa5rKanServerInit(self):
        pass

    @Mod.DestroyServer()
    def Script_NeteaseModBTa5rKanServerDestroy(self):
        pass

    @Mod.InitClient()
    def Script_NeteaseModBTa5rKanClientInit(self):
        pass

    @Mod.DestroyClient()
    def Script_NeteaseModBTa5rKanClientDestroy(self):
        pass
