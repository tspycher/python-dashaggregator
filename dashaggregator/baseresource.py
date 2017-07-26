from dashaggregator import Modulemanager
import yaml

class BaseResource(object):

    ml = None

    def __init__(self):
        super(BaseResource, self).__init__()
        with open("../config/config.yml") as f:
            y = yaml.load(f)
        self.ml = Modulemanager(config=y['modules'])