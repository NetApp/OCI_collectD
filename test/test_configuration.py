import unittest
import logging
from modules.configuration.configuration import Configuration
from modules.collectd import Config


class ConfigurationTest(unittest.TestCase):

    def test_configuration(self):
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
        self.assertTrue(type(configuration) is Configuration)
        self.assertTrue(configuration.host == 'localhost')
        self.assertTrue(configuration.token == '3859a3ee-3244-4e93-aea2-8777d99c280c')
        self.assertTrue(configuration.report_interval == 60)
        self.assertTrue(configuration.failed_report_queue_size == 10)
        self.assertTrue(configuration.aggregation_type == 'average')
        self.assertTrue(configuration.plugins == {'cpu', 'memory'})
        self.assertTrue(configuration.logging_level == logging.INFO)
