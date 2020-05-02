import logging


def init_log():
    logging.basicConfig(
        level=logging.ERROR, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


class LoggerMixin:
    def __init__(self, name=None):
        logger_name = name if name else __name__
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s %(process)s %(levelname)s %(name)s %(message)s")
        handler.setFormatter(formatter)
        self.logger.handlers = []
        self.logger.addHandler(handler)
        self.logger.propagate = False


__all__ = ["init_log", "LoggerMixin"]
