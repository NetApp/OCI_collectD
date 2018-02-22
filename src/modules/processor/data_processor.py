import threading
from modules.logger import oci_logger
try:
    import collectd
except ImportError:
    from modules.collectd import collectd


class DataProcessor(object):
    def __init__(self, configuration, log_file=oci_logger.DEFAULT_LOG_FILE_NAME):
        self.configuration = configuration
        self.current_stats = {}
        self.data_set_types = {}
        self.lock = threading.Lock()
        self.logger = oci_logger.get_logger(__name__, configuration.logging_level, log_file)

    def process(self, value_list):
        plugin = value_list.plugin
        if len(self.configuration.plugins) > 0 and plugin not in self.configuration.plugins:
            return

        if value_list.plugin_instance:
            plugin = plugin + '#' + value_list.plugin_instance

        value_type = value_list.type
        if value_type not in self.data_set_types:
            self.data_set_types[value_type] = collectd.get_dataset(value_type)
        self.logger.debug("data set type = %s of value type %s" % (self.data_set_types[value_type], value_type))

        if value_list.type_instance:
            value_type = value_type + '#' + value_list.type_instance

        with self.lock:
            if plugin not in self.current_stats:
                self.current_stats[plugin] = {}
            plugin_stats = self.current_stats[plugin]

            if value_type not in plugin_stats:
                plugin_stats[value_type] = {}
            type_stats = plugin_stats[value_type]

            if value_list.host not in type_stats:
                type_stats[value_list.host] = {}
                type_stats[value_list.host]['data'] = []
                type_stats[value_list.host]['time'] = []
            host_stats = type_stats[value_list.host]
            host_stats['data'].append([float(s) for s in value_list.values])
            host_stats['time'].append(value_list.time)

    def refresh_stats(self):
        with self.lock:
            stats = self.current_stats
            self.current_stats = {}
            return stats

    def get_data_set_types(self):
        return self.data_set_types
