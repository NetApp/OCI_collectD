import time


class Node(object):
    def __init__(self, key, value):
        self.key = key
        self.values = [value]


class Config(object):
    def __init__(self, **kwargs):
        self.key = 'Module'
        self.values = ['oci_write_plugin']
        self.children = []
        for key in kwargs.keys():
            self.children.append(Node(key, kwargs.get(key)))


class ValueList(object):
    def __init__(self, plugin, plugin_type):
        self.plugin = plugin
        self.plugin_instance = None
        self.type = plugin_type
        self.type_instance = None
        self.host = 'localhost'
        self.values = [123]
        self.time = time.time()


class collectd(object):
    _data_set = {'cpu': 'DERIVE'}

    @staticmethod
    def get_dataset(data_type):
        return collectd._data_set[data_type]

    @staticmethod
    def register_config(*args):
        pass

    @staticmethod
    def register_init(*args):
        pass

    @staticmethod
    def register_write(*args, **kwargs):
        pass

    @staticmethod
    def register_shutdown(*args):
        pass
