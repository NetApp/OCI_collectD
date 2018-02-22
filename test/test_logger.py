import unittest
import logging
from modules.logger import oci_logger


class LoggerTest(unittest.TestCase):

    def setUp(self):
        self.logger = oci_logger.get_logger(__name__, logging.INFO, log_file='/tmp/collectd_oci.log')
        self.expected_prefix = "[NetAppOnCommandInsightPlugin][" + __name__ + "] "

    def test_type_of_logger(self):
        self.assertTrue(type(self.logger) is oci_logger._CollectdLogger)
