# coding=utf-8
from Script_Platinum.QuModLibs.Client import *
from Script_Platinum.QuModLibs.Modules.Services.Client import BaseService, QRequests
from Script_Platinum.client.player.playerBaubleInfo import PlayerBaubleInfoClientService
from Script_Platinum.client.player.playerBaubleSlot import PlayerBaubleSlotClientService
from Script_Platinum.data.responseData import ItemStack
from Script_Platinum.utils.clientUtils import compFactory

ProxyCls = clientApi.GetUIScreenProxyCls()
Binding = clientApi.GetViewBinderCls()
minecraftEnum = clientApi.GetMinecraftEnum()
BAUBLE_CONTAINER_NAME = "bauble_reborn.screen.name"
BAUBLE_KEY_MAPPING_NAME = "platinum.open_bauble_window"
BAUBLE_KEY_MAPPING_CATEGORY = "Platinum-铂"
RESERVED_UI_SLOT_INDEX = 107
BAUBLE_GRID_CELL_SIZE = 18
BAUBLE_GRID_BASE_COLUMN_COUNT = 9
BAUBLE_GRID_MAX_ROW_COUNT = 5
BAUBLE_GRID_HORIZONTAL_PADDING = 14
baubleContainerRules = {}
_returnInventoryCategory = None


def _getVisibleSlotCount(slotCount):
    return min(max(slotCount, 0), RESERVED_UI_SLOT_INDEX)


def _getBaubleGridLayout(slotCount):
    slotCount = _getVisibleSlotCount(slotCount)
    columnCount = max(
        BAUBLE_GRID_BASE_COLUMN_COUNT,
        (slotCount + BAUBLE_GRID_MAX_ROW_COUNT - 1) // BAUBLE_GRID_MAX_ROW_COUNT,
    )
    rowCount = (slotCount + columnCount - 1) // columnCount
    gridWidth = columnCount * BAUBLE_GRID_CELL_SIZE
    return (
        (columnCount, rowCount),
        (
            gridWidth,
            rowCount * BAUBLE_GRID_CELL_SIZE,
        ),
        gridWidth + BAUBLE_GRID_HORIZONTAL_PADDING,
    )


def _getContainerItemCount(slotCount):
    slotCount = _getVisibleSlotCount(slotCount)
    return slotCount + (1 if slotCount > RESERVED_UI_SLOT_INDEX else 0)


def _getSlotIndex(containerIndex, slotCount):
    if not isinstance(containerIndex, (int, long)) or containerIndex < 0 or containerIndex == RESERVED_UI_SLOT_INDEX:
        return None
    slotCount = _getVisibleSlotCount(slotCount)
    slotIndex = containerIndex - (1 if containerIndex > RESERVED_UI_SLOT_INDEX else 0)
    return slotIndex if slotIndex < slotCount else None


def _isValidContainerItem(itemDict, slotType, baubleRules):
    itemStack = ItemStack.fromDict(itemDict)
    return itemStack.count == 1 and slotType in baubleRules.get(itemStack.name, ())


def _onBaubleContainerOpened(data):
    data = getattr(data, "data", data)
    baubleContainerRules.clear()
    if isinstance(data, dict):
        baubleContainerRules.update(data.get("rules", {}))


def openBaubleContainer(returnCategory=None):
    global _returnInventoryCategory
    _returnInventoryCategory = returnCategory
    baubleContainerRules.clear()
    if returnCategory is not None:
        clientApi.PopTopUI()

    def readyToOpen():
        if clientApi.GetTopUI() not in ("inventory_screen", "inventory_screen_pocket"):
            BaseService().syncRequest(
                "server/player/openBaubleContainer", QRequests.Args().setCallBack(_onBaubleContainerOpened)
            )
            return
        compFactory.CreateGame(levelId).AddTimer(0.0, readyToOpen)

    readyToOpen()


@BaseService.Init
class BaubleKeyMappingClientService(BaseService):

    @BaseService.Listen("LoadClientAddonScriptsAfter")
    def registerKeyMapping(self, data):
        compFactory.CreatePlayerView(levelId).RegisterCustomKeyMapping(
            BAUBLE_KEY_MAPPING_NAME, minecraftEnum.KeyBoardType.KEY_C, BAUBLE_KEY_MAPPING_CATEGORY
        )

    @BaseService.Listen("OnCustomKeyPressInGame")
    def onCustomKeyPressInGame(self, data):
        if (
            data.get("name") != BAUBLE_KEY_MAPPING_NAME
            or data.get("isDown") != "1"
            or data.get("screenName") != "hud_screen"
        ):
            return
        openBaubleContainer()


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
        self.contentStackPath = (
            "variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/"
            "safezone_screen_panel/root_screen_panel/root_panel/bauble_panel/content_stack"
        )
        self.baubleGridPath = self.contentStackPath + "/bauble_top_half/content_stack/bauble_grid"
        self.pendingSlotLayout = None

    def OnCreate(self):
        self.slotManager.addPlayerSlotListener(self.onSlotListChanged)
        self.baubleInfoManager.addBaubleInfoListener(self.onBaubleInfoChanged)
        ListenForEvent("PlayerTryPutCustomContainerItemClientEvent", self, self.onTryPutItem)
        ListenForEvent("PlayerTryAddCustomContainerItemClientEvent", self, self.onTryPutItem)
        self._updateBaubleLayout(len(self.slotManager.getPlayerSlotList()))

    def OnDestroy(self):
        global _returnInventoryCategory
        self.pendingSlotLayout = None
        self.slotManager.removePlayerSlotListener(self.onSlotListChanged)
        self.baubleInfoManager.removeBaubleInfoListener(self.onBaubleInfoChanged)
        UnListenForEvent("PlayerTryPutCustomContainerItemClientEvent", self, self.onTryPutItem)
        UnListenForEvent("PlayerTryAddCustomContainerItemClientEvent", self, self.onTryPutItem)
        if _returnInventoryCategory is not None:
            category = _returnInventoryCategory
            _returnInventoryCategory = None

            def readyToOpenInventory():
                screen = clientApi.GetTopUI()
                if screen != "hud_screen":
                    compFactory.CreateGame(levelId).AddTimer(0.0, readyToOpenInventory)
                    return
                clientApi.OpenInventoryGui(category, True)

            readyToOpenInventory()

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
        slotIndex = _getSlotIndex(index, len(slotList))
        if slotIndex is None:
            data["cancel"] = True
            return
        if not _isValidContainerItem(data.get("itemDict"), slotList[slotIndex].slotType, baubleContainerRules):
            data["cancel"] = True

    def onSlotListChanged(self, slotList):
        self._updateBaubleLayout(len(slotList))

    def OnTick(self):
        if self.pendingSlotLayout is None:
            return
        slotCount, columnCount = self.pendingSlotLayout
        containerItemCount = _getContainerItemCount(slotCount)
        if containerItemCount == 0:
            self.pendingSlotLayout = None
            return
        if (
            self.screen.GetBaseUIControl(self.baubleGridPath + "/bauble_ui_grid_item{}".format(containerItemCount))
            is None
        ):
            return
        for containerIndex in range(containerItemCount):
            slotIndex = _getSlotIndex(containerIndex, slotCount)
            if slotIndex is None:
                continue
            self.screen.GetBaseUIControl(
                self.baubleGridPath + "/bauble_ui_grid_item{}".format(containerIndex + 1)
            ).SetPosition(
                (
                    slotIndex % columnCount * BAUBLE_GRID_CELL_SIZE,
                    slotIndex // columnCount * BAUBLE_GRID_CELL_SIZE,
                )
            )
        self.pendingSlotLayout = None

    def _updateBaubleLayout(self, slotCount):
        containerItemCount = _getContainerItemCount(slotCount)
        gridDimension, gridSize, contentWidth = _getBaubleGridLayout(slotCount)
        containerGridDimension = _getBaubleGridLayout(containerItemCount)[0]
        gridControl = self.screen.GetBaseUIControl(self.baubleGridPath)
        contentStackControl = self.screen.GetBaseUIControl(self.contentStackPath)
        topHalfPath = self.contentStackPath + "/bauble_top_half"
        topHalfContentControl = self.screen.GetBaseUIControl(topHalfPath + "/content_stack")
        if gridDimension[1] > 0:
            gridControl.asGrid().SetGridDimension(containerGridDimension)
        gridControl.SetFullSize(axis="x", paramDict={"absoluteValue": gridSize[0]})
        gridControl.SetFullSize(axis="y", paramDict={"absoluteValue": gridSize[1]})
        contentStackControl.SetFullSize(axis="x", paramDict={"absoluteValue": contentWidth})
        topHalfContentControl.SetFullSize(
            axis="x",
            paramDict={"absoluteValue": -BAUBLE_GRID_HORIZONTAL_PADDING, "followType": "parent", "relativeValue": 1.0},
        )
        self.pendingSlotLayout = (slotCount, gridDimension[0])

    def onBaubleInfoChanged(self, baubleInfo):
        self._updateBaubleLayout(len(self.slotManager.getPlayerSlotList()))

    @Binding.binding(Binding.BF_BindInt, "#bauble_reborn.container.max_items_count")
    def bindingMaxItemsCount(self):
        return _getContainerItemCount(len(self.slotManager.getPlayerSlotList()))

    @Binding.binding_collection(Binding.BF_BindBool, "netease_ui_container", "#bauble_reborn.container.slot.visible")
    def bindingSlotVisible(self, index):
        return _getSlotIndex(index, len(self.slotManager.getPlayerSlotList())) is not None

    @Binding.binding_collection(Binding.BF_BindString, "netease_ui_container", "#bauble_reborn.container.slot_overlay")
    def bindingSlotOverlay(self, index):
        slotList = self.slotManager.getPlayerSlotList()
        slotIndex = _getSlotIndex(index, len(slotList))
        return slotList[slotIndex].placeholderPath if slotIndex is not None else ""

    @Binding.binding_collection(
        Binding.BF_BindBool, "netease_ui_container", "#bauble_reborn.container.slot_overlay.visible"
    )
    def bindingSlotOverlayVisible(self, index):
        slotList = self.slotManager.getPlayerSlotList()
        slotIndex = _getSlotIndex(index, len(slotList))
        return (
            slotIndex is not None and self.baubleInfoManager.getBaubleInfoBySlot(slotList[slotIndex].identifier) is None
        )
