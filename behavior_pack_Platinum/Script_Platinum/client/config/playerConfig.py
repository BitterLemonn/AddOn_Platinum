# coding=utf-8
from Script_Platinum import commonConfig
from Script_Platinum.QuModLibs.Client import *
from Script_Platinum.QuModLibs.Modules.Services.Client import BaseService, QRequests
from Script_Platinum.utils import developLogging as logging, oldVersionFixer


class DataAlias(object):
    PLATINUM_LOCAL_DATA = "platinum_local_data"
    BAUBLE_SLOT_INFO = "bauble_slot_info"
    BAUBLE_BTN_POSITION = "bauble_btn_position"
    BAUBLE_FORMAT_VERSION = "bauble_format_version"
    BAUBLE_COMMAND_MODIFY = "bauble_command_modify"


class PlayerConfig(object):
    """玩家本地配置"""

    formatVersion = commonConfig.PLAYER_LOCAL_DATA_VERSION
    uiPosition = "left_top"

    # 旧版本兼容
    playerBaubleInfo = {}
    baubleCommandModifyAdding = []


@BaseService.Init
class PlayerConfigService(BaseService):
    """玩家配置服务"""

    def __init__(self):
        BaseService.__init__(self)
        self.uid = None

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
        data = comp.GetConfigData(DataAlias.PLATINUM_LOCAL_DATA + "_{}".format(self.uid))
        if data:
            logging.debug("铂: 发现旧数据, 开始迁移数据")
            formatVersion = data.get(DataAlias.BAUBLE_FORMAT_VERSION, 0)
            PlayerConfig.uiPosition = data.get(DataAlias.BAUBLE_BTN_POSITION, "left_top")
            PlayerConfig.playerBaubleInfo = self.migrateData(formatVersion, data.get(DataAlias.BAUBLE_SLOT_INFO, {}))
            PlayerConfig.baubleCommandModifyAdding = data.get(DataAlias.BAUBLE_COMMAND_MODIFY, [])

            # 将当前的废弃数据发送至服务端 (不久后将移除此危险操作) TODO
            if PlayerConfig.baubleCommandModifyAdding:
                self.syncRequest(
                    "server/player/syncCommandSlot", QRequests.Args(PlayerConfig.baubleCommandModifyAdding)
                )
                PlayerConfig.baubleCommandModifyAdding = []
            if PlayerConfig.playerBaubleInfo:
                self.syncRequest("server/player/syncOldData", QRequests.Args(PlayerConfig.playerBaubleInfo))
                PlayerConfig.playerBaubleInfo = {}
            # 同步完成后删除旧数据 避免重复发送
            comp.SetConfigData(DataAlias.PLATINUM_LOCAL_DATA + "_{}".format(self.uid), {})
            # 保存为新数据格式
            self.mannalySaveData()
            logging.debug("铂: 玩家数据迁移完成, 已删除旧数据")
        else:
            data = comp.GetConfigData(DataAlias.PLATINUM_LOCAL_DATA)
            PlayerConfig.uiPosition = data.get(DataAlias.BAUBLE_BTN_POSITION, "left_top")

    def mannalySaveData(self):
        """手动保存数据"""
        self._saveData()

    @BaseService.Listen("UnLoadClientAddonScriptsBefore")
    def _saveData(self, _=None):
        compFactory.CreateConfigClient(levelId).SetConfigData(
            DataAlias.PLATINUM_LOCAL_DATA,
            {
                DataAlias.BAUBLE_FORMAT_VERSION: PlayerConfig.formatVersion,
                DataAlias.BAUBLE_BTN_POSITION: PlayerConfig.uiPosition,
            },
        )

    def migrateData(self, formatVersion, data):
        if formatVersion != commonConfig.PLAYER_LOCAL_DATA_VERSION:
            # 数据版本从0升级到1
            if formatVersion == 0:
                formatVersion = 1
                for baubleName, value in data.items():
                    newId = oldVersionFixer.oldSlotIdFixer(baubleName)
                    data[newId] = value
                    data.pop(baubleName)

            elif formatVersion == 1:
                formatVersion = 2

            self.migrateData(formatVersion, data)
        return data
