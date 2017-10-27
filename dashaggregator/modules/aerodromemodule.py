import xmltodict
import requests
import math
import re
from datetime import datetime
from dashaggregator.modules import Basemodule
from bs4 import BeautifulSoup
import pytz
from dateutil import parser



class AerodromeWeather(object):

    icao = None
    alt = None # feet
    oat = None # Celcius
    pressure = None # hpa
    wind = None
    winddir = None
    wind_high = None
    winddir_high = None
    rwyheading = None
    metar = None
    source = None
    freshdata = None
    time = None

    windtranslate = {
        'n': 0.0,
        'nne': 22.5,
        'ne': 45.0,
        'ene': 67.5,
        'e': 90.0,
        'ese': 112.5,
        'se': 135.0,
        'sse': 157.5,
        's': 180.0,
        'ssw': 202.5,
        'sw': 225.0,
        'wsw': 247.5,
        'w': 270.0,
        'wnw': 292.5,
        'nw': 315.0,
        'nnw': 337.5
    }

    def __init__(self, icao, alt=0, oat=15, pressure=1013.25, wind=0, winddir=0, rwyheading=180):
        self.icao = icao
        self.alt = alt
        self.oat = oat
        self.pressure = pressure
        self.wind = wind
        self.winddir = winddir
        self.rwyheading = rwyheading
        self.wind_high = self.wind
        self.winddir_high = self.winddir
        self.freshdata = False

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
            self.wind = int(metar['response']['data']['METAR']['wind_speed_kt'])
            self.winddir = int(metar['response']['data']['METAR']['wind_dir_degrees'])
            self.alt = round(float(metar['response']['data']['METAR']['elevation_m']) * 3.28084, 0)
            self.source = "metar"
            self.freshdata = True
            return True

        self.metar = None
        return False

    def _translateWind(self, string):
        string = str(string).lower()
        if not string in self.windtranslate:
            return 0
        return int(self.windtranslate[string])

    def getWeatherLink(self, url):
        r = requests.get(url, stream=True)
        records = []
        for line in r.iter_lines():
            if line:
                data = filter(lambda x: len(x) >= 1, re.sub(' +', ',', line).split(','))
                try:
                    records.append( {
                        'datetime': "%s %s" % (data[0],data[1]),
                        'oat': float(data[2]),
                        'hum': int(data[5]),
                        'dewpt': float(data[6]),
                        'wind': int(float(data[7])),
                        'winddir': self._translateWind(data[8]),
                        'wind_high': int(float(data[10])),
                        'winddir_high': self._translateWind(data[11]),
                        'pressure': float(data[16]),
                        'rain': float(data[17]),
                        'rainrate': float(data[18]),
                    })
                except ValueError:
                    continue
                except IndexError:
                    continue
        if not records:
            return
        current = records[-1]

        self.freshdata = self.checkFresh(parser.parse(current['datetime'])) #datetime.strptime(current['datetime'], '%d.%m.%y %H:%M'))
        self.time = current['datetime']
        self.pressure = current['pressure']
        self.oat = current['oat']
        self.wind = int(current['wind'])
        self.winddir = int(current['winddir'])
        self.wind_high = int(current['wind_high'])
        self.winddir_high = int(current['winddir_high'])
        self.source = 'weatherlink'

    def getOpenWeatherMap(self, id, apikey):
        url = 'http://api.openweathermap.org/data/2.5/weather?id=%d&APPID=%s&units=metric' % (id, apikey)
        r = requests.get(url)
        data = r.json()

        freshdata = datetime.fromtimestamp(int(data['dt']))
        self.freshdata = self.checkFresh(freshdata)

        self.time = freshdata.strftime('%d.%m.%y %H:%M')
        self.pressure = data['main']['pressure']
        self.oat = data['main']['temp']
        self.wind = int(round(data['wind']['speed'] * 1.94384,0)) #m/s
        self.winddir = int(data['wind']['deg']) if 'deg' in data['wind'] else 0
        self.source = 'openweathermap'

    def checkFresh(self, d, timezone='Europe/Zurich', maxage=60):
        d = pytz.timezone(timezone).localize(d) #freshdata.astimezone(pytz.timezone(timezone))
        now = datetime.now(tz=pytz.timezone(timezone))
        age = (now - d).seconds / 60  # minutes
        if age <= maxage:
            return True

class AerodromeModule(Basemodule):
    weather = None

    def configure(self, config):
        super(AerodromeModule, self).configure(config)
        self.weather = AerodromeWeather(self.config['icao'], alt=self.config['altitude'], rwyheading=self.config['runwaydirection'])

    def render(self):
        if not self.weather.update():
            if 'openweathermap_city_id' in self.config:
                self.weather.getOpenWeatherMap(self.config['openweathermap_city_id'], self.config['openweathermap_apikey'])
            if 'weatherlink_url' in self.config:
                self.weather.getWeatherLink(url=self.config['weatherlink_url'])

        return {
            'metar_raw': self.weather.metar,
            'metar': '<div style="padding: 10px; vertical-align: middle; font-size: 20px;">%s</div>' % self.weather.metar,
            'hpa': self.weather.pressure,
            'alt': self.weather.alt,
            'oat': self.weather.oat,
            'wind': int(self.weather.wind),
            'winddir': int(self.weather.winddir),
            'wind_high': int(self.weather.wind_high),
            'winddir_high': int(self.weather.winddir_high),
            'pa': self.weather.pa,
            'da': self.weather.da,
            'crosswind': self.weather.crosswind,
            'runway': self.weather.runwayname,
            'first_runway': self.weather.rwyheading,
            'source': self.weather.source,
            'airfield_status': self.airfieldstatus,
            'airfield_status_text': self.airfieldstatustext,
            'fresh_meteo': self.weather.freshdata,
            'meteo_time': self.weather.time
        }

    @property
    def airfieldstatustext(self):
        if not 'airfieldstatus_url' in self.config:
            return ""
        url = self.config['airfieldstatus_url']

        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.content, "html.parser")
            return soup.find_all('td')[2].text.split("\r\n")[2]
        except:
            return ""

    @property
    def airfieldstatus(self):
        if not 'airfieldstatus_url' in self.config:
            return 9
        url = self.config['airfieldstatus_url']

        r = requests.get(url)
        g = re.search("(?<=stufe.)\\d", r.content, re.I | re.S)
        if g:
            return int(g.group(0))

        return 9


if __name__ == "__main__":
    a = AerodromeWeather("lszi", alt=1788, rwyheading=250)
    a.getWeatherLink(url="http://www.aecs-fricktal.ch/wetter/reports/downld02.txt")
