import socket
from dashaggregator.modules import Basemodule

class SystemModule(Basemodule):
    refreshrate = 10

    def configure(self, config):
        super(SystemModule, self).configure(config)

    def render(self):
        return {"ipaddress":socket.gethostbyname(socket.gethostname())}

if __name__ == "__main__":
    s = SystemModule("System")
    print s.render()


