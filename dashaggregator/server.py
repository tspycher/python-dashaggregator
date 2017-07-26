from application import create_app
from flask import redirect
from flask_restful import Api
from dashaggregator import DashboardResource, DashboardConfigResource

app = create_app()
api = Api(app)

@app.route("/")
def default():
    return redirect('/web/index.html#source=/config')

api.add_resource(DashboardResource, '/data', '/data/<string:module>')
api.add_resource(DashboardConfigResource, '/config', '/config/<string:name>')

if __name__ == '__main__':
    app.run()

