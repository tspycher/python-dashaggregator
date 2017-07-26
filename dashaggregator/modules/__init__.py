class Basemodule(object):

    name = None
    config = None

    def __init__(self, name):
        self.name = name

    def configure(self, config):
        self.config = config

    def render(self):
        return {}