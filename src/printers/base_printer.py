import enum


class Level(enum.Enum):
    DEBUG = 0
    INFO = 1
    ERROR = 2


class BasePrinter:
    def __init__(self, config, level: Level):
        self.level = level

    def _print(self, msg):
        raise NotImplementedError

    def print_msg(self, msg, level=Level.INFO):
        if level.value >= self.level.value:
            self._print(msg)
