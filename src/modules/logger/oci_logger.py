import abc
import logging
from logging.handlers import RotatingFileHandler


DEFAULT_LOG_FILE_NAME = "/var/log/collectd_oci.log"


class _Logger(object):
    """
    The base class for logger, all loggers have to extend this class
    and provide implementation for the basic logging methods.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def debug(self, msg):
        pass

    @abc.abstractmethod
    def info(self, msg):
        pass

    @abc.abstractmethod
    def warning(self, msg):
        pass

    @abc.abstractmethod
    def error(self, msg):
        pass


class _CollectdLogger(_Logger):
    _PREFIX = '[NetAppOnCommandInsightPlugin] '

    def __init__(self, module_name, logging_level, log_file=DEFAULT_LOG_FILE_NAME):
        handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=100)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s : %(message)s')
        handler.setFormatter(formatter)
        handler.setLevel(logging_level)
        self.logger = logging.getLogger(module_name)
        self.logger.propagate = False
        self.logger.setLevel(logging_level)
        self.logger.addHandler(handler)

    def debug(self, msg):
        self.logger.debug(_CollectdLogger._PREFIX + msg)

    def info(self, msg):
        self.logger.info(_CollectdLogger._PREFIX + msg)

    def warning(self, msg):
        self.logger.warning(_CollectdLogger._PREFIX + msg)

    def error(self, msg):
        self.logger.error(_CollectdLogger._PREFIX + msg)


def get_logger(module_name=None, logging_level=logging.INFO, log_file=DEFAULT_LOG_FILE_NAME):
    """
    Provides the default logger for the application.
    """
    return _CollectdLogger(module_name, logging_level, log_file)
