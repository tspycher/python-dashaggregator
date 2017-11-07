from flask_restful import Resource
import json
from dashaggregator import BaseResource


class DashboardConfigResource(Resource, BaseResource):
    def get(self, name='default'):
        with open('../config/%s.json' % name) as f:
            config = json.load(f)

        config['datasources'] = []

        for d in self.ml.datasources():
            m = self.ml.module(d)
            refresh = 60 if not m.refreshrate else m.refreshrate
            config['datasources'].append( {'name':m.name, 'settings':{'url':'/data/%s' % d,'refresh':refresh,'use_thingproxy':True,'method':'GET'}, 'type':'JSON'})
        return config
