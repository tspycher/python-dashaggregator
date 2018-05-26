from flask import Flask, send_from_directory, redirect, request
from flask_restful import Api
from flask_cors import CORS
import yaml
import os

from dashaggregator import DashboardResource, DashboardConfigResource


def create_app():
    app = Flask('DashboardAggregator', static_url_path='/web', static_folder='./web_copy')
    api = Api(app)
    CORS(app)

    api.add_resource(DashboardResource, '/data', '/data/<string:module>')
    api.add_resource(DashboardConfigResource, '/config', '/config/<string:name>')

    @app.route('/.well-known/acme-challenge/<string:challenge>')
    def catch_all_letsencrypt(challenge):
        return (os.getenv('LETSENCRYPT_KEY', "No key authorization provided"), 200)

    @app.route('/custom/<path:filename>')
    def custom_web(filename):
        return send_from_directory(app.root_path + '/../web_custom', filename)

    @app.route("/")
    def default():
        if 'device' in request.args:
            with open(app.root_path + "/../config/config.yml") as f:
                y = yaml.load(f)
            if 'routes' in y and request.args.get('device') in y['routes']:
                custom_config = y['routes'][request.args.get('device')]
                if str(custom_config).startswith('/'):
                    return redirect(custom_config)
                return redirect('/web/index.html#source=/config/%s' % custom_config)

        if request.user_agent.platform.lower() in ['iphone', 'android']:
            return redirect('/web/index-mobile.html#source=/config/default_mobile')

        return redirect('/web/index.html#source=/config/default_webcam')

    return app