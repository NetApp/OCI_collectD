"""
OCI write plugin for collectd
"""
import time
import traceback
from modules.configuration.configuration import Configuration
from modules.logger import oci_logger
from modules.processor.data_processor import DataProcessor
from modules.processor.data_reporter import DataReporter
try:
    import collectd
except ImportError:
    import modules.collectd as collectd

_configuration = None
_data_reporter = None


def oci_config(config):
    """collectd configuration callback method"""
    global _configuration
    _configuration = Configuration(config)


def oci_write(value_list, data_processor):
    """collectd write callback method"""
    data_processor.process(value_list)


def oci_shutdown():
    """collectd shutdown callback method"""
    global _data_reporter
    if _data_reporter:
        _data_reporter.shutdown()


def oci_init():
    """collectd initialization callback method"""
    global _configuration, _data_reporter
    logger = None
    try:
        while not _configuration:
            time.sleep(1)
        data_processor = DataProcessor(configuration=_configuration)
        collectd.register_write(oci_write, data=data_processor)
        _data_reporter = DataReporter(_configuration, data_processor)
        logger = oci_logger.get_logger(__name__, _configuration.logging_level)
        logger.info('Initialization completed successfully.')
    except Exception as e:
        logger.error("Cannot initialize plugin. Cause: " + str(e) + "\n" + traceback.format_exc())


collectd.register_init(oci_init)
collectd.register_config(oci_config)
collectd.register_shutdown(oci_shutdown)
