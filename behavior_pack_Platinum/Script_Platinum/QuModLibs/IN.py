# -*- coding: utf-8 -*-
from Util import SystemSide

IsServerUser = False
ModDirName = SystemSide.__module__.split(".")[0]
QuModLibsPath = SystemSide.__module__[:SystemSide.__module__.rfind(".")]

class RuntimeService:
    _serviceSystemList = []
    _clientSystemList = []