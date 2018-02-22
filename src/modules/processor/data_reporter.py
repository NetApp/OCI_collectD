import threading
import time
import decimal
import json
import requests
from collections import deque
from modules.logger import oci_logger


class InvalidDataException(Exception):
    pass


class DataReporter(object):
    def __init__(self, configuration, data_processor):
        self.configuration = configuration
        self.data_processor = data_processor
        self.logger = oci_logger.get_logger(__name__, configuration.logging_level)
        self.lock = threading.Lock()
        self.stopping = False
        self.failed_report_queue = deque(maxlen=self.configuration.failed_report_queue_size)
        self.last_report_time = time.time()
        self.worker = threading.Thread(name='reporting_thread', target=self._report_oci_integration_data, args=())
        self.worker.start()

    def shutdown(self):
        with self.lock:
            self.stopping = True
        self.worker.join()

    def _report_oci_integration_data(self):
        """method to report OCI integration data"""
        while True:
            with self.lock:
                if self.stopping:
                    break
            current_time = time.time()
            elapsed_time = current_time - self.last_report_time
            if decimal.Decimal(elapsed_time) >= self.configuration.report_interval:
                report_stats = self.data_processor.refresh_stats()
                if report_stats:
                    self._report_stats_into_oci(report_stats)
                self.last_report_time = current_time
                if self.configuration.failed_report_queue_size > 0 and len(self.failed_report_queue) > 0:
                    self._report_failed_reports()
            time.sleep(1)

    def _report_stats_into_oci(self, stats):
        data_set_types = self.data_processor.get_data_set_types()
        self.logger.info("-------------Raw Report-------------")
        self.logger.info(json.dumps(stats))

        payload_by_plugin_map = {}

        for plugin in stats:
            plugin_instance = ''
            plugin_key = plugin
            if '#' in plugin:
                index = plugin.index('#')
                plugin_key = plugin[0:index]
                plugin_instance = plugin[index+1:]

            if plugin_key not in payload_by_plugin_map:
                payload_by_plugin_map[plugin_key] = []
            payload = payload_by_plugin_map[plugin_key]

            host_data_entry_map = {}
            plugin_stats = stats[plugin]
            for value_type in plugin_stats:
                type_stats = plugin_stats[value_type]
                # data set definition could be tricky, it may not include type instance
                if '#' in value_type:
                    data_set = data_set_types[value_type[0:value_type.index('#')]]
                else:
                    data_set = data_set_types[value_type]
                # OCI does not allow dash in data point key ???
                data_point_key = value_type.replace('-', '_')
                if '#' in data_point_key:
                    data_point_key = data_point_key.replace('#', '.')
                for host in type_stats:
                    host_stats = type_stats[host]
                    if host not in host_data_entry_map:
                        entry = dict()
                        entry['identifiers'] = {'host': host}
                        entry['attributes'] = {}
                        entry['dataPoints'] = {'sampleTimeUTC': host_stats['time'][-1] * 1000}
                        payload.append(entry)
                        host_data_entry_map[host] = entry
                    else:
                        entry = host_data_entry_map[host]

                    if plugin_instance != '':
                        entry['identifiers']['subtype'] = plugin_instance

                    data_points = host_data_entry_map[host]['dataPoints']
                    for col in range(len(data_set)):
                        if data_set[col][0] == 'value':
                            data_points[data_point_key] = self._calculate_data_value(host_stats, col, data_set[col][1])
                        else:
                            data_points[data_point_key + '_' + data_set[col][0]] \
                                = self._calculate_data_value(host_stats, col, data_set[col][1])

        for plugin in payload_by_plugin_map.keys():
            payload = payload_by_plugin_map[plugin]
            if payload:
                status_code = self._report_payload_to_server(plugin, payload)
                if status_code != 200 and self.configuration.failed_report_queue_size > 0:
                    self.failed_report_queue.append((plugin, payload))

    def _construct_url(self, plugin):
        """method to construct data integration URL"""
        return 'https://' + self.configuration.host + '/rest/v1/integrations/collectd_' + plugin

    def _calculate_data_value(self, host_stats, col, data_type):
        """private method to calculate aggregated value for sampling data"""
        length = len(host_stats['data'])
        if data_type == 'gauge':
            if self.configuration.aggregation_type == 'average':
                total = 0.0
                for row in range(length):
                    total = total + host_stats['data'][row][col]
                return total / length
            elif self.configuration.aggregation_type == 'mininum':
                return min(x[col] for x in ((y for y in host_stats['data'])))
            elif self.configuration.aggregation_type == 'maximum':
                return max(x[col] for x in ((y for y in host_stats['data'])))
            elif self.configuration.aggregation_type == 'last':
                return host_stats['data'][length-1][col]
            else:
                raise InvalidDataException(
                    "Unsupported guaged value aggregation type %s\n" % self.configuration.aggregation_type)
        elif data_type == 'counter' or data_type == 'derive' or data_type == 'absolute':
            if length < 2:
                self.logger.warning("Not enough samples to process delta value: %s\n" % host_stats)
                return None
            if host_stats['time'][0] >= host_stats['time'][-1]:
                self.logger.warning("Timestamp reverted to process delta value: %s\n" % host_stats)
                return None
            if host_stats['data'][0] > host_stats['data'][-1]:
                self.logger.warning("Data reverted to process delta value: %s\n" % host_stats)
                return None

            delta_time = decimal.Decimal(host_stats['time'][-1]) - decimal.Decimal(host_stats['time'][0])
            delta_value = host_stats['data'][-1][col]
            if data_type == 'counter' or data_type == 'derive':
                delta_value = delta_value - host_stats['data'][0][col]
            return delta_value / float(delta_time)
        else:
            raise InvalidDataException("Unsupported data type %s\n" % data_type)

    def _report_failed_reports(self):
        while len(self.failed_report_queue) > 0:
            (plugin, payload) = self.failed_report_queue.popleft()
            self.logger.info('-------------Re-reported Failed Report-------------')
            status_code = self._report_payload_to_server(plugin, payload)
            if status_code != 200:
                self.failed_report_queue.appendleft((plugin, payload))
                return

    def _report_payload_to_server(self, plugin, payload):
        data_json = json.dumps(payload)
        url = self._construct_url(plugin)
        try:
            response = requests.post(url, data=data_json, headers=self.configuration.headers, verify=False)
            log_method = getattr(self.logger, 'info')
            if response.status_code != 200:
                log_method = getattr(self.logger, 'warning')
            log_method('----------REQUEST-----------')
            log_method('plugin = ' + plugin)
            log_method(data_json)
            log_method('----------RESPONSE-----------')
            log_method(str(response.status_code))
            log_method(str(response.json()))
            return response.status_code
        except Exception as e:
            self.logger.error("HTTP Request Error. Cause: " + str(e))
            return 999
