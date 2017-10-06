import pytz
from datetime import datetime
from . import Basemodule

class TimeModule(Basemodule):
    timezone = None

    def configure(self, config):
        super(TimeModule, self).configure(config)
        if config and 'timezone' in self.config:
            self.timezone = self.config['timezone']
        else:
            self.timezone = 'utc'

    def render(self):
        tz = pytz.timezone(self.timezone)
        t = datetime.now(tz)
        time = t.strftime('%H:%M')
        date = t.strftime('%d.%m.%Y')

        return {"time": time, "date": date, "timezone": str(self.timezone).upper() }