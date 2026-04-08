isDebug = True


def info(msg):
    if isDebug:
        _logging.info(msg)


def debug(msg):
    if isDebug:
        _logging.debug(msg)


def error(msg):
    _logging.error(msg)


def warning(msg):
    if isDebug:
        _logging.warning(msg)


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

    @classmethod
    def i(cls, msg):
        cls.info(msg)

    @classmethod
    def d(cls, msg):
        cls.debug(msg)

    @classmethod
    def e(cls, msg):
        cls.error(msg)

    @classmethod
    def w(cls, msg):
        cls.warn(msg)

    @classmethod
    def s(cls, msg):
        cls.suc(msg)
