# coding=utf-8
from Script_Platinum.QuModLibs.Client import *
from Script_Platinum.QuModLibs.Modules.Services.Client import BaseService, QRequests
from Script_Platinum.client.player.playerBaubleInfo import PlayerBaubleInfoClientService
from Script_Platinum.client.player.playerBaubleSlot import PlayerBaubleSlotClientService
from Script_Platinum.data.responseData import ItemStack
from Script_Platinum.utils.clientUtils import compFactory

ProxyCls = clientApi.GetUIScreenProxyCls()
Binding = clientApi.GetViewBinderCls()
NETEASE_UI_CONTAINER_SLOT_LIMIT = 50
BAUBLE_CONTAINER_NAME = "bauble_reborn.screen.name"
baubleContainerRules = {}


def _isValidContainerItem(itemDict, slotType, baubleRules):
    itemStack = ItemStack.fromDict(itemDict)
    return itemStack.count == 1 and slotType in baubleRules.get(itemStack.name, ())


def _onBaubleContainerOpened(data):
    data = getattr(data, "data", data)
    baubleContainerRules.clear()
    if isinstance(data, dict):
        baubleContainerRules.update(data.get("rules", {}))


def openBaubleContainer():
    baubleContainerRules.clear()
    clientApi.PopTopUI()

    def readyToOpen():
        if clientApi.GetTopUI() != "inventory_screen":
            BaseService().syncRequest(
                "server/player/openBaubleContainer", QRequests.Args().setCallBack(_onBaubleContainerOpened)
            )
            return
        compFactory.CreateGame(levelId).AddTimer(0.0, readyToOpen)

    readyToOpen()


@Listen("UiInitFinished")
def onUiInitFinished(data):
    clientApi.GetNativeScreenManagerCls().instance().RegisterScreenProxy(
        "bauble_reborn_screen.screen", "Script_Platinum.client.ui.baubleContainerUi.BaubleContainerProxy"
    )


class BaubleContainerProxy(ProxyCls):

    def __init__(self, screenName, screenNode):
        ProxyCls.__init__(self, screenName, screenNode)
        self.screen = self.GetScreenNode()
        self.slotManager = PlayerBaubleSlotClientService.access()
        self.baubleInfoManager = PlayerBaubleInfoClientService.access()

    def OnCreate(self):
        self.slotManager.addPlayerSlotListener(self.onSlotListChanged)
        self.baubleInfoManager.addBaubleInfoListener(self.onBaubleInfoChanged)
        ListenForEvent("PlayerTryPutCustomContainerItemClientEvent", self, self.onTryPutItem)
        ListenForEvent("PlayerTryAddCustomContainerItemClientEvent", self, self.onTryPutItem)

    def OnDestroy(self):
        self.slotManager.removePlayerSlotListener(self.onSlotListChanged)
        self.baubleInfoManager.removeBaubleInfoListener(self.onBaubleInfoChanged)
        UnListenForEvent("PlayerTryPutCustomContainerItemClientEvent", self, self.onTryPutItem)
        UnListenForEvent("PlayerTryAddCustomContainerItemClientEvent", self, self.onTryPutItem)

    @staticmethod
    def _isBaubleContainer(data):
        return (
            data.get("collectionType") == "netease_ui_container" and data.get("collectionName") == BAUBLE_CONTAINER_NAME
        )

    def onTryPutItem(self, data):
        if not self._isBaubleContainer(data):
            return
        index = data.get("collectionIndex")
        slotList = self.slotManager.getPlayerSlotList()
        if not isinstance(index, (int, long)) or not 0 <= index < min(len(slotList), NETEASE_UI_CONTAINER_SLOT_LIMIT):
            data["cancel"] = True
            return
        if not _isValidContainerItem(data.get("itemDict"), slotList[index].slotType, baubleContainerRules):
            data["cancel"] = True

    def onSlotListChanged(self, slotList):
        self.screen.UpdateScreen()

    def onBaubleInfoChanged(self, baubleInfo):
        self.screen.UpdateScreen()

    @Binding.binding(Binding.BF_BindInt, "#bauble_reborn.container.max_items_count")
    def bindingMaxItemsCount(self):
        return min(len(self.slotManager.getPlayerSlotList()), NETEASE_UI_CONTAINER_SLOT_LIMIT)

    @Binding.binding_collection(Binding.BF_BindString, "netease_ui_container", "#bauble_reborn.container.slot_overlay")
    def bindingSlotOverlay(self, index):
        slotList = self.slotManager.getPlayerSlotList()
        return slotList[index].placeholderPath if index < min(len(slotList), NETEASE_UI_CONTAINER_SLOT_LIMIT) else ""

    @Binding.binding_collection(
        Binding.BF_BindBool, "netease_ui_container", "#bauble_reborn.container.slot_overlay.visible"
    )
    def bindingSlotOverlayVisible(self, index):
        slotList = self.slotManager.getPlayerSlotList()
        return (
            index < min(len(slotList), NETEASE_UI_CONTAINER_SLOT_LIMIT)
            and self.baubleInfoManager.getBaubleInfoBySlot(slotList[index].identifier) is None
        )
