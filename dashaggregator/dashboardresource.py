from flask_restful import Resource
from dashaggregator import BaseResource

class DashboardResource(Resource, BaseResource):
    def get(self, module=None):
        if module:
            return self.ml.render(module)
        return self.ml.renderall()