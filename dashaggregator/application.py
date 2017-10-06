from flask import Flask, send_from_directory

def create_app():
    app = Flask('DashboardAggregator', static_url_path='/web', static_folder='../web')

    @app.route('/custom/<path:filename>')
    def custom_web(filename):
        return send_from_directory(app.root_path + '/../web_custom', filename)

    return app