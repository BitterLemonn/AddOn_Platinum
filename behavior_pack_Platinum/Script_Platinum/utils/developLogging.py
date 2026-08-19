isDebug = True
LOGGER_LEVEL = "DEBUG"
_LOGGER_LEVEL_VALUES = {"DEBUG": 10, "INFO": 20, "WARNING": 30}
assert LOGGER_LEVEL in _LOGGER_LEVEL_VALUES


def isEnabledFor(level):
    return isDebug and level in _LOGGER_LEVEL_VALUES and _LOGGER_LEVEL_VALUES[level] >= _LOGGER_LEVEL_VALUES[LOGGER_LEVEL]


def info(msg):
    if isEnabledFor("INFO"):
        _logging.info(msg)


def debug(msg):
    if isEnabledFor("DEBUG"):
        _logging.debug(msg)


def error(msg):
    _logging.error(msg)


def warning(msg):
    if isEnabledFor("WARNING"):
        _logging.warn(msg)


def success(msg):
    if isEnabledFor("INFO"):
        _logging.suc(msg)


class _logging:

    @classmethod
    def info(cls, msg):
        print("[INFO] {}".format(msg))

    @classmethod
    def debug(cls, msg):
        print("[DEBUG] {}".format(msg))

    @classmethod
    def error(cls, msg):
        print("[ERROR] {}".format(msg))

    @classmethod
    def warn(cls, msg):
        print("[WARN] {}".format(msg))

    @classmethod
    def suc(cls, msg):
        print("[SUC] {}".format(msg))
