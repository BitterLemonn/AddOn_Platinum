# coding=UTF-8

from Script_Platinum.QuModLibs.Server import *
from Script_Platinum.QuModLibs.Modules.Services.Server import BaseService


@BaseService.Init
class InnerService(BaseService):
    def __init__(self):
        BaseService.__init__(self)

    @BaseService.Listen("LoadServerAddonScriptsAfter")
    def onLoadServerAddonScriptsAfter(self, data):
        # 注册默认槽位
        from Script_Platinum.server.inner.innerSlotRegistry import innerRegisterDefaultSlot

        innerRegisterDefaultSlot()
