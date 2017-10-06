import importlib
import yaml

class Modulemanager(object):
    __modules__ = None

    def __init__(self, config=None):
        self.__modules__ = {}
        if config: self.load_from_config(config)

    def load_from_config(self, config):
        for m, data in config.iteritems():
            self.load_module(m, data['type'], data['config'] if 'config' in data else None)

    def load_module(self, name, type, config=None):
        self.__modules__[name.lower()] = getattr(
            importlib.import_module("dashaggregator.modules.%smodule" % (type.lower())), "%sModule" % type)(
            name)
        self.__modules__[name.lower()].configure(config)

    def load(self, modules):
        for m in modules:
            self.load_module(m['name'], m['type'], m['config'] if 'config' in m else None)

    def render(self, module):
        if not module in self.__modules__:
            return {}
        return {"name": self.__modules__[module].name, "data": self.__modules__[module].render()}

    def renderall(self):
        data = {}
        for key, m in self.__modules__.iteritems():
            data[key] = self.render(key)
        return data

    def module(self, name):
        return self.__modules__[name]

    def datasources(self):
        return self.__modules__.keys()

if __name__ == '__main__':
    config = """
modules:
    OtherModule:
        type: Dummy
        config:
            a: blafasel
            b: katsching
    """
    y = yaml.load(config)

    ml = Modulemanager(config=y['modules'])
    print ml.renderall()
