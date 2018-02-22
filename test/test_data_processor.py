import unittest
import time
from modules.configuration.configuration import Configuration
from modules.processor.data_processor import DataProcessor
from modules.collectd import Config, ValueList


class DataProcessorTest(unittest.TestCase):

    def test_data_processor(self):
        config_map = {
            'host': 'localhost',
            'token': '3859a3ee-3244-4e93-aea2-8777d99c280c',
            'report_interval': '60',
            'failed_report_queue_size': '10',
            'aggregation_type': 'average',
            'plugins': 'cpu,memory',
            'logging_level': 'info'
        }
        config = Config(**config_map)
        configuration = Configuration(config)
        data_processor = DataProcessor(configuration, log_file='/tmp/collectd_oci.log')
        value_list = ValueList('cpu', 'cpu')
        data_processor.process(value_list)
        self.assertTrue('cpu' in data_processor.data_set_types)
        self.assertTrue(data_processor.data_set_types.get('cpu') == 'DERIVE')
        self.assertTrue('cpu' in data_processor.current_stats)  # plugin
        self.assertTrue('cpu' in data_processor.current_stats.get('cpu'))  # type
        self.assertTrue('localhost' in data_processor.current_stats.get('cpu').get('cpu'))
        self.assertTrue('data' in data_processor.current_stats.get('cpu').get('cpu').get('localhost'))
        self.assertTrue(
            data_processor.current_stats.get('cpu').get('cpu').get('localhost').get('data')[0][0] == float(123))
        self.assertTrue('time' in data_processor.current_stats.get('cpu').get('cpu').get('localhost'))
        self.assertTrue(
            time.time() - data_processor.current_stats.get('cpu').get('cpu').get('localhost').get('time')[0] < 1)
