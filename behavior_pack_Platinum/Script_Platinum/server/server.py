# coding=utf-8
from Script_Platinum import commonConfig
from Script_Platinum.data.itemStack import maxStackStore
from Script_Platinum.QuModLibs.Server import *
from Script_Platinum.utils.serverUtils import compFactory

itemComp = compFactory.CreateItem(levelId)
itemComp.GetUserDataInEvent("InventoryItemChangedServerEvent")


# 获取全部物品基本信息
@Listen("LoadServerAddonScriptsAfter")
def onLoadServerAddonScriptsAfter(data):
    allItems = itemComp.GetLoadItems()
    for item in allItems:
        baseInfo = itemComp.GetItemBasicInfo(item)
        if baseInfo is not None:
            maxStackStore[item] = baseInfo["maxStackSize"]
    server = serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER)
    server.BroadcastEvent(commonConfig.PLATINUM_SYSTEM_INIT_FINISHED_EVENT, {})


@Listen("ServerChatEvent")
def onServerChatEvent(data):
    playerId = data["playerId"]
    message = data["message"]
    if message == "1":
        BroadcasterServer = serverApi.GetSystem(commonConfig.PLATINUM_NAMESPACE, commonConfig.PLATINUM_BROADCAST_SERVER)
        baubleInfo = BroadcasterServer.GetPlayerBaubleInfo(playerId)
        print(baubleInfo)
