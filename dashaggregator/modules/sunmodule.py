from astral import Astral
import datetime
import pytz
from dashaggregator.modules import Basemodule


class SunModule(Basemodule):
    refreshrate = 10
    city = None

    def configure(self, config):
        super(SunModule, self).configure(config)
        if 'city' in config:
            self.city = config['city']

    def render(self):

        a = Astral()
        a.solar_depression = 'civil'
        city = a[self.city if self.city else 'London']
        sun = city.sun(date=datetime.datetime.utcnow(), local=False)

        data = {
            "timezone": city.timezone,
            "latitude": city.latitude,
            "longitude": city.longitude,
            "dawn": sun['dawn'].astimezone(pytz.timezone(city.timezone)).strftime('%H:%M'),
            "sunrise": sun['sunrise'].astimezone(pytz.timezone(city.timezone)).strftime('%H:%M'),
            "noon": sun['noon'].astimezone(pytz.timezone(city.timezone)).strftime('%H:%M'),
            "sunset": sun['sunset'].astimezone(pytz.timezone(city.timezone)).strftime('%H:%M'),
            "dusk": sun['dusk'].astimezone(pytz.timezone(city.timezone)).strftime('%H:%M')
        }

        data['aviation_sunrise'] = "%s / %s" % (data['dawn'], data['sunrise'])
        data['aviation_sunset'] = "%s / %s" % (data['sunset'], data['dusk'])

        return data


