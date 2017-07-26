import xmltodict
import requests
import math
from . import Basemodule

class AerodromeWeather(object):

    icao = None
    alt = None # feet
    oat = None # Celcius
    pressure = None # hpa
    wind = None
    winddir = None
    rwyheading = None
    metar = None
    source = None

    def __init__(self, icao, alt=0, oat=15, pressure=1013.25, wind=0, winddir=0, rwyheading=180):
        self.icao = icao
        self.alt = alt
        self.oat = oat
        self.pressure = pressure
        self.wind = wind
        self.winddir = winddir
        self.rwyheading = rwyheading

    @property
    def pa(self):
        return int(float(self.alt) + 30.0 * (1013.25 - float(self.pressure)))

    @property
    def da(self):
        return self.pa + int((self.oat - (15 - ((self.pa / 1000) * 2))) * 120)

    @property
    def crosswind(self):
        return int(math.ceil(math.fabs(math.sin(math.radians(self.winddir-self.rwyheading)) * self.wind)))

    @property
    def oppositerwy(self):
        return self.rwyheading+180 if self.rwyheading <= 180 else self.rwyheading-180

    @property
    def runwayname(self):
        return "%02d/%02d" % (self.rwyheading / 10, self.oppositerwy / 10)

    def update(self):
        url = 'http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&stationString=%s&hoursBeforeNow=1&mostRecent=true' % \
              self.icao.upper()
        r = requests.get(url)
        metar = xmltodict.parse(r.content)
        if 'METAR' in metar['response']['data']:
            self.metar = metar['response']['data']['METAR']['raw_text']
            self.pressure = round(float(metar['response']['data']['METAR']['altim_in_hg']) * 33.863886666667, 2)
            self.oat = float(metar['response']['data']['METAR']['temp_c'])
            self.wind = float(metar['response']['data']['METAR']['wind_speed_kt'])
            self.winddir = float(metar['response']['data']['METAR']['wind_dir_degrees'])
            self.alt = round(float(metar['response']['data']['METAR']['elevation_m']) * 3.28084, 0)
            self.source = "metar"
            return True

        self.metar = None
        return False

    def getOpenWeatherMap(self, id, apikey):
        url = 'http://api.openweathermap.org/data/2.5/weather?id=%d&APPID=%s&units=metric' % (id, apikey)
        r = requests.get(url)
        data = r.json()

        self.pressure = data['main']['pressure']
        self.oat = data['main']['temp']
        self.wind = round(data['wind']['speed'] * 1.94384,0) #m/s
        self.winddir = data['wind']['deg']
        self.source = 'openweathermap'

class AerodromeModule(Basemodule):
    weather = None

    def configure(self, config):
        super(AerodromeModule, self).configure(config)
        self.weather = AerodromeWeather(self.config['icao'], alt=self.config['altitude'], rwyheading=self.config['runwaydirection'])

    def render(self):
        if not self.weather.update():
            if 'openweathermap_city_id' in self.config:
                self.weather.getOpenWeatherMap(self.config['openweathermap_city_id'], self.config['openweathermap_apikey'])

        return {
            'metar': self.weather.metar,
            'hpa': self.weather.pressure,
            'alt': self.weather.alt,
            'oat': self.weather.oat,
            'wind': self.weather.wind,
            'winddir': self.weather.winddir,
            'pa': self.weather.pa,
            'da': self.weather.da,
            'crosswind': self.weather.crosswind,
            'runway': self.weather.runwayname,
            'source': self.weather.source
        }


