from logging import Logger


class DummyLogger(Logger):
    def __init__(self):
        super().__init__("dummy")
    def debug(self, msg, *args, **kwargs):
        pass
    def info(self, msg, *args, **kwargs):
        pass
    def warning(self, msg, *args, **kwargs):
        pass
    def error(self, msg, *args, **kwargs):
        pass
    def critical(self, msg, *args, **kwargs):
        pass
    def exception(self, msg, *args, **kwargs):
        pass