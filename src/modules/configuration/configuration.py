import decimal
import logging


class InvalidConfigurationException(Exception):
    pass


class Configuration(object):
    def __init__(self, config):
        if config.key != 'Module':
            raise InvalidConfigurationException("config.key %s != Module\n" % config.key)
        if config.values[0] != 'oci_write_plugin':
            raise InvalidConfigurationException("config.values %s != oci\n" % config.values)
        logging_level_raw = ''

        for node in config.children:
            key = node.key.lower()
            value = node.values[0]
            if key == 'host':
                self.host = value
            elif key == 'token':
                self.token = value
                self.headers = {"Content-type": "application/json", "X-OCI-Integration": self.token}
            elif key == 'report_interval':
                self.report_interval = decimal.Decimal(value)
            elif key == 'failed_report_queue_size':
                self.failed_report_queue_size = decimal.Decimal(value)
            elif key == "aggregation_type":
                self.aggregation_type = value
            elif key == "plugins":
                self.plugins = set([s.strip() for s in value.split(',')])
            elif key == "logging_level":
                logging_level_raw = value
                self.logging_level = logging.getLevelName(value.upper())
            else:
                raise InvalidConfigurationException("Invalid configuration: %s = %s\n" % (key, value))

        if not self.host:
            raise InvalidConfigurationException("Host is not configured in the module configuration")
        if not self.token:
            raise InvalidConfigurationException("Token is not configured in the module configuration")
        if self.report_interval < 60 or self.report_interval > 3600:
            raise InvalidConfigurationException("Interval for data report should be between 60 and 3600 inclusive")
        if self.failed_report_queue_size < 0 or self.failed_report_queue_size > 10000:
            raise InvalidConfigurationException(
                "Queue size for failed data report should be between 0 and 10000 inclusive")
        if self.aggregation_type not in ['average', 'minimum', 'maximum', 'last']:
            raise InvalidConfigurationException(
                "Aggregation type for guaged value can be only one of ['average', 'minimum', 'maximum', 'last']")
        if not self.plugins:
            raise InvalidConfigurationException("Plugins is not configured in the module configuration")
        if logging_level_raw not in ['debug', 'info', 'warning', 'error']:
            raise InvalidConfigurationException(
                "Logging level can be only one of ['debug', 'info', 'warning', 'error']")
