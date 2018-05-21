from .application import create_app
import urllib3


urllib3.disable_warnings()
app = create_app()

if __name__ == '__main__':
    app.run()

