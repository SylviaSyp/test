import logging
import sys
import time
import typing  # type: ignore # noqa: F401

_DEFAULT_LOGGER = "atorch.logger"

_DEFAULT_FORMATTER = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] " "[%(filename)s:%(lineno)d:%(funcName)s] %(message)s"
)

_ch = logging.StreamHandler(stream=sys.stderr)
_ch.setFormatter(_DEFAULT_FORMATTER)

_DEFAULT_HANDLERS = [_ch]

_LOGGER_CACHE = {}  # type: typing.Dict[str, logging.Logger]


def get_logger(name, level="INFO", handlers=None, update=False):
    if name in _LOGGER_CACHE and not update:
        return _LOGGER_CACHE[name]
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers = handlers or _DEFAULT_HANDLERS
    logger.propagate = False
    return logger


default_logger = get_logger(_DEFAULT_LOGGER)


class DashBoardWriter(object):
    def __init__(self, logdir="./"):
        from torch.utils.tensorboard import SummaryWriter

        self.writer = SummaryWriter(logdir)

    def add_scalar(self, key, value, n_iter: int):
        self.writer.add_scalar(key, value, n_iter)

    def add_scalars(self, name, stats, n_iter):
        for k, v in stats.items():
            self.add_scalar(name + "/" + k, v, n_iter)

    def flush(self):
        self.writer.flush()


class TimeStats:
    def __init__(self, name):
        self.name = name
        self.time_statics = dict()

    def __getitem__(self, key):
        return self.time_statics.get(key, None)

    def __setitem__(self, key, value):
        self.time_statics[key] = value

    def to_dashboard(self, dashboard_writer=None, n_iter=None):
        dashboard_writer.add_scalars(self.name, self.time_statics, n_iter)
        dashboard_writer.flush()


class Timer:
    def __init__(self, name, time_stats=None):
        self.name = name
        self.time_stats = time_stats

    def start(self):
        self.start_time = time.time()

    def end(self):
        self.end_time = time.time()
        self.elapsed_time = self.end_time - self.start_time

    def __enter__(self):
        self.start()

    def __exit__(self, type, value, trace):
        self.end()
        if self.time_stats:
            self.time_stats[self.name] = self.elapsed_time
