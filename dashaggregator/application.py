from flask import Flask, send_from_directory, redirect, request
from flask_restful import Api


from dashaggregator import DashboardResource, DashboardConfigResource


def create_app():
    app = Flask('DashboardAggregator', static_url_path='/web', static_folder='../web')
    api = Api(app)

    api.add_resource(DashboardResource, '/data', '/data/<string:module>')
    api.add_resource(DashboardConfigResource, '/config', '/config/<string:name>')

    @app.route('/custom/<path:filename>')
    def custom_web(filename):
        return send_from_directory(app.root_path + '/../web_custom', filename)

    @app.route("/")
    def default():
        if request.user_agent.platform.lower() in ['iphone', 'android']:
            return redirect('/web/index-mobile.html#source=/config/default_mobile')

        return redirect('/web/index.html#source=/config/default_webcam')

    return app