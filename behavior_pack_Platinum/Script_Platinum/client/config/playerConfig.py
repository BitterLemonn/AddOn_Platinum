# coding=utf-8
from Script_Platinum import commonConfig
from Script_Platinum.QuModLibs.Client import *
from Script_Platinum.QuModLibs.Modules.Services.Client import BaseService, QRequests
from Script_Platinum.utils import developLogging as logging, oldVersionFixer


class DataAlias(object):
    PLATINUM_LOCAL_DATA = "platinum_local_data"
    BAUBLE_SLOT_INFO = "bauble_slot_info"
    BAUBLE_BTN_POSITION = "bauble_btn_position"
    SHOW_BAUBLE_SIDEBAR_BUTTON = "show_bauble_sidebar_button"
    SHOW_BAUBLE_CONTAINER_BUTTON = "show_bauble_container_button"
    BAUBLE_FORMAT_VERSION = "bauble_format_version"
    BAUBLE_COMMAND_MODIFY = "bauble_command_modify"


class PlayerConfig(object):
    """玩家本地配置"""

    formatVersion = commonConfig.PLAYER_LOCAL_DATA_VERSION
    uiPosition = "left_top"
    showBaubleSidebarButton = True
    showBaubleContainerButton = True


@BaseService.Init
class PlayerConfigService(BaseService):
    """玩家配置服务"""

    SETTING_ITEM_ID = "4667732199784769754"
    SETTING_SHOW_SIDEBAR_BUTTON = "show_bauble_sidebar_button"
    SETTING_SHOW_CONTAINER_BUTTON = "show_bauble_container_button"
    SETTING_ENTRY_POSITION = "bauble_entry_position"
    POSITION_OPTIONS = ["左上角", "右上角", "左下角", "右下角"]
    POSITION_BY_OPTION = ["left_top", "right_top", "left_bottom", "right_bottom"]
    OPTION_BY_POSITION = {
        "left_top": "左上角",
        "right_top": "右上角",
        "left_bottom": "左下角",
        "right_bottom": "右下角",
    }

    def __init__(self):
        BaseService.__init__(self)
        self.uid = None
        self.settingInst = None

    @BaseService.Listen("LoadClientAddonScriptsAfter")
    def onLoadClientAddonScriptsAfter(self, data):
        comp = compFactory.CreateNeteaseWindow(levelId)
        self.settingInst = comp.RegisterSettingInst(self.SETTING_ITEM_ID, "铂", "textures/ui/platinum_logo")
        if self.settingInst is None:
            logging.error("铂: 通用设置实例注册失败")
            return
        self.settingInst.AddToggle(
            self.SETTING_SHOW_SIDEBAR_BUTTON,
            "显示人物框饰品侧边栏按钮",
            self.onToggleChanged,
            1,
            PlayerConfig.showBaubleSidebarButton,
        )
        self.settingInst.AddToggle(
            self.SETTING_SHOW_CONTAINER_BUTTON,
            "显示背包独立饰品窗口按钮",
            self.onToggleChanged,
            2,
            PlayerConfig.showBaubleContainerButton,
        )
        self.settingInst.AddDropDown(
            self.SETTING_ENTRY_POSITION,
            "人物框饰品按钮位置",
            self.POSITION_OPTIONS,
            self.onPositionChanged,
            3,
            self.OPTION_BY_POSITION.get(PlayerConfig.uiPosition, "左上角"),
        )
        self.syncSettingDefaults()

    def onToggleChanged(self, *args):
        if len(args) < 2:
            return
        key, value = args[0], bool(args[1])
        if key == self.SETTING_SHOW_SIDEBAR_BUTTON:
            PlayerConfig.showBaubleSidebarButton = value
        elif key == self.SETTING_SHOW_CONTAINER_BUTTON:
            PlayerConfig.showBaubleContainerButton = value
        else:
            return
        self.mannalySaveData()

    def onPositionChanged(self, *args):
        if len(args) < 2:
            return
        option = args[1]
        if not isinstance(option, int) or option < 0 or option >= len(self.POSITION_OPTIONS):
            return
        position = self.POSITION_BY_OPTION[option]
        if position is None:
            return
        self.setUiPosition(position)

    def setUiPosition(self, position):
        if position not in self.OPTION_BY_POSITION:
            return
        PlayerConfig.uiPosition = position
        if self.settingInst is not None:
            self.settingInst.SetDropDownDefault(self.SETTING_ENTRY_POSITION, self.OPTION_BY_POSITION[position])
        self.mannalySaveData()

    def syncSettingDefaults(self):
        if self.settingInst is None:
            return
        self.settingInst.SetToggleDefault(self.SETTING_SHOW_SIDEBAR_BUTTON, PlayerConfig.showBaubleSidebarButton)
        self.settingInst.SetToggleDefault(self.SETTING_SHOW_CONTAINER_BUTTON, PlayerConfig.showBaubleContainerButton)
        self.settingInst.SetDropDownDefault(
            self.SETTING_ENTRY_POSITION,
            self.OPTION_BY_POSITION.get(PlayerConfig.uiPosition, "左上角"),
        )

    @BaseService.Listen("OnLocalPlayerStopLoading")
    def onLocalPlayerStopLoading(self, data):
        """玩家加载完成事件"""
        playerComp = compFactory.CreatePlayer(playerId)
        self.uid = playerComp.getUid()
        self._loadingData()

    def _loadingData(self):
        # 旧版本使用uid保存数据
        if self.uid is None:
            logging.error("铂: 玩家UID获取失败, 无法加载铂数据")
            return
        comp = clientApi.GetEngineCompFactory().CreateConfigClient(levelId)
        legacyKey = DataAlias.PLATINUM_LOCAL_DATA + "_{}".format(self.uid)
        legacyData = comp.GetConfigData(legacyKey)
        data = comp.GetConfigData(DataAlias.PLATINUM_LOCAL_DATA) or legacyData or {}
        PlayerConfig.uiPosition = data.get(DataAlias.BAUBLE_BTN_POSITION, "left_top")
        PlayerConfig.showBaubleSidebarButton = data.get(DataAlias.SHOW_BAUBLE_SIDEBAR_BUTTON, True)
        PlayerConfig.showBaubleContainerButton = data.get(DataAlias.SHOW_BAUBLE_CONTAINER_BUTTON, True)
        if legacyData:
            self._migrateLegacyData(comp, legacyKey, legacyData)
        self.syncSettingDefaults()

    def _migrateLegacyData(self, comp, legacyKey, data):
        baubleDict = self.migrateData(data.get(DataAlias.BAUBLE_FORMAT_VERSION, 0), data.get(DataAlias.BAUBLE_SLOT_INFO, {}))
        commandSlots = data.get(DataAlias.BAUBLE_COMMAND_MODIFY, [])
        if baubleDict is None or not isinstance(commandSlots, (list, tuple)):
            logging.warning("铂: 旧版饰品数据格式无效, 已保留原数据")
            return

        def finishMigration():
            if comp.GetConfigData(legacyKey) == data and self._saveData() and comp.SetConfigData(legacyKey, {}):
                logging.debug("铂: 玩家数据迁移完成, 已删除旧数据")

        def sendMigration(api, payload, onSuccess):
            def onResult(result):
                if result.success and result.data is True:
                    onSuccess()
                else:
                    logging.warning("铂: 服务端未确认迁移成功, 已保留旧数据")

            self.syncRequest(api, QRequests.Args(payload).setCallBack(onResult))

        def migrateBaubles():
            if baubleDict:
                sendMigration("server/player/syncOldData", baubleDict, finishMigration)
            else:
                finishMigration()

        if commandSlots:
            sendMigration("server/player/syncCommandSlot", commandSlots, migrateBaubles)
        else:
            migrateBaubles()

    def mannalySaveData(self):
        """手动保存数据"""
        self._saveData()

    @BaseService.Listen("UnLoadClientAddonScriptsBefore")
    def _saveData(self, _=None):
        return compFactory.CreateConfigClient(levelId).SetConfigData(
            DataAlias.PLATINUM_LOCAL_DATA,
            {
                DataAlias.BAUBLE_FORMAT_VERSION: PlayerConfig.formatVersion,
                DataAlias.BAUBLE_BTN_POSITION: PlayerConfig.uiPosition,
                DataAlias.SHOW_BAUBLE_SIDEBAR_BUTTON: PlayerConfig.showBaubleSidebarButton,
                DataAlias.SHOW_BAUBLE_CONTAINER_BUTTON: PlayerConfig.showBaubleContainerButton,
            },
        )

    def migrateData(self, formatVersion, data):
        if not isinstance(data, dict) or formatVersion not in (0, 1, commonConfig.PLAYER_LOCAL_DATA_VERSION):
            return None
        if formatVersion != 0:
            return data
        migrated = {}
        for slotId, value in data.items():
            newId = oldVersionFixer.oldSlotIdFixer(slotId)
            if newId in migrated and migrated[newId] != value:
                return None
            migrated[newId] = value
        return migrated
