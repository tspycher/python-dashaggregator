from flask import Flask

def create_app():
    app = Flask('DashboardAggregator', static_url_path='/web', static_folder='../web')
    return app