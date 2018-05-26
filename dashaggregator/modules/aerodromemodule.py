import xmltodict
import requests
from xml.etree import ElementTree
from copy import copy
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
    dewpoint = None # Celcius
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
    def cloudbase(self):
        if not self.oat or not self.dewpoint:
            return {'ground': 0, 'alt': 0}
        spread = float(self.oat) - float(self.dewpoint)
        base = spread / 2.5 * 1000
        return {'ground': base, 'alt': self.alt + base}

    @property
    def pa(self):
        return float(self.alt) + 27.0 * (1013.25 - float(self.pressure))

    @property
    def da(self):
        return self.pa + ((self.oat - (15.0 - (self.pa / 1000.0 * 2.0))) * 120.0)

    @property
    def crosswind(self):
        return int(math.ceil(math.fabs(math.sin(math.radians(self.winddir-self.rwyheading)) * self.wind)))

    @property
    def oppositerwy(self):
        return (self.rwyheading + 180) % 360

    @property
    def runwayname(self):
        return "%02d/%02d" % (self.rwyheading / 10, self.oppositerwy / 10)

    @property
    def suggested_runway(self):
        difference = self.winddir-self.rwyheading
        if ((self.rwyheading + 90) % 360) - self.rwyheading >= difference >= ((self.rwyheading - 90) % 360) - self.rwyheading:
            return self.rwyheading

        return self.oppositerwy

    def update(self):
        url = 'http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&stationString=%s&hoursBeforeNow=1&mostRecent=true' % \
              self.icao.upper()
        r = requests.get(url)
        metar = xmltodict.parse(r.content)
        if 'METAR' in metar['response']['data']:
            self.metar = metar['response']['data']['METAR']['raw_text']
            self.pressure = round(float(metar['response']['data']['METAR']['altim_in_hg']) * 33.863886666667, 2)
            self.oat = float(metar['response']['data']['METAR']['temp_c'])
            self.dewpoint = float(metar['response']['data']['METAR']['dewpoint_c'])
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

    def getWeatherLinkOnline(self, station, password):
        def dictify(r):
            data = {}
            if list(r):
                data[r.tag] = {}
                for i in list(r):
                    data[r.tag] = data[r.tag].copy().update(dictify(i))
            else:
                data[r.tag] = r.text
            return data

        url = "http://www.weatherlink.com/xml.php?user=%s&pass=%s" % (station, password)
        tree = ElementTree.fromstring(requests.get(url).content)
        data = dictify(tree)

        self.freshdata = self.checkFresh(parser.parse(data['current_observation']['observation_time_rfc822']), maxage=5)#parser.parse(current['datetime'], ignoretz=True )) #datetime.strptime(current['datetime'], '%d.%m.%y %H:%M'))
        self.time = parser.parse(data['current_observation']['observation_time_rfc822']).strftime('%d.%m.%y %H:%M')
        self.pressure = float(data['current_observation']['pressure_mb'])
        self.oat = float(data['current_observation']['temp_c'])
        self.dewpoint = float(data['current_observation']['dewpoint_c'])
        self.wind = float(data['current_observation']['wind_kt'])
        self.winddir = int(data['current_observation']['wind_degrees'])
        self.wind_high = round(float(data['current_observation']['davis_current_observation']['wind_ten_min_avg_mph']) * 0.868976,1)
        self.winddir_high = None
        self.source = 'weatherlinkonline'


    def getWeatherLink(self, url):
        #http://www.weatherlink.com/xml.php?user=constantwind&pass=iubb
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


        """00 - Date
        01 - Time
        02 - Temp Out
        03 - Hi Temp
        04 - Low Temp
        05 - Out Hum
        06 - Dew Pt.
        07 - Wind Speed
        08 - Wind Dir
        09 - Wind Run
        10 - Hi Speed
        11 - Hi Dir
        12 - Wind chill
        13 - Heat Index
        14 - THW Index
        15 - THSW Index
        16 - Bar
        17 - Rain
        18 - Rain Rate
        19 - Solar Rad
        20 - Solar Engergy
        21 - Hi Solar Rad
        22 - UV Index
        23 - UV Dose
        24 - Hi UV
        25 - Head D-D
        26 - Cool D-D
        27 - In Temp
        28 - In Hum 
        29 - In Dew
        30 - In Heat
        31 - In EMC
        32 - In Air Density
        33 - ET
        34 - Wind Samp
        35 - Wind TX
        36 - ISS Recept
        37 - Arc Int"""

        self.freshdata = self.checkFresh(datetime.strptime(current['datetime'], '%d.%m.%y %H:%M'), maxage=10)#parser.parse(current['datetime'], ignoretz=True )) #datetime.strptime(current['datetime'], '%d.%m.%y %H:%M'))
        self.time = current['datetime']
        self.pressure = current['pressure']
        self.oat = current['oat']
        self.dewpoint = current['dewpt']
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

    def checkFresh(self, d, timezone='Europe/Zurich', maxage=30):
        if not d.tzinfo:
            d = pytz.timezone(timezone).localize(d)#.replace(tzinfo=pytz.timezone(timezone))
        now = datetime.now(tz=pytz.timezone(timezone))
        age = (now - d).total_seconds() / 60  # minutes
        if age <= maxage:
            return True
        return False

class AerodromeModule(Basemodule):
    weather = None

    def configure(self, config):
        super(AerodromeModule, self).configure(config)
        self.weather = AerodromeWeather(self.config['icao'], alt=self.config['altitude'], rwyheading=self.config['runwaydirection'])

    def render(self):
        if not self.weather.update():
            if 'openweathermap_city_id' in self.config:
                self.weather.getOpenWeatherMap(self.config['openweathermap_city_id'], self.config['openweathermap_apikey'])
                self.refreshrate = 300
            if 'weatherlink_url' in self.config:
                self.weather.getWeatherLink(url=self.config['weatherlink_url'])
                self.refreshrate = 120
            if 'weatherlink_station' in self.config:
                self.weather.getWeatherLinkOnline(station=self.config['weatherlink_station'], password=self.config['weatherlink_password'])
                self.refreshrate = 60

        color = "ff000c" if self.weather.da >= self.weather.alt * 1.65 else "ffc401" if self.weather.da >= self.weather.alt * 1.35 else "00cd03"
        text = "high da risk" if self.weather.da >= self.weather.alt * 1.65 else "moderate da risk" if self.weather.da >= self.weather.alt * 1.35 else "low da risk"
        da_warning = '<div style="padding: 20px;background-color: #%s;color: white;width=100%%; heigth=100%%; font-size: 20px;">%s</div>' % (color, text.upper())

        return {
            'metar_raw': self.weather.metar,
            'metar': '<div style="padding: 10px; vertical-align: middle; font-size: 20px;">%s</div>' % self.weather.metar,
            'hpa': round(self.weather.pressure,0),
            'alt': self.weather.alt,
            'oat': self.weather.oat,
            'dewpoint': self.weather.dewpoint,
            'cloudbase': round(self.weather.cloudbase['ground'], 0),
            'cloudbase_alt': round(self.weather.cloudbase['alt'], 0),
            'wind': int(self.weather.wind),
            'winddir': int(self.weather.winddir),
            'wind_high': int(self.weather.wind_high),
            'winddir_high': int(self.weather.winddir_high) if self.weather.winddir_high else None,
            'pa': int(round(self.weather.pa, 0)),
            'da': int(round(self.weather.da, 0)),
            'da_danger': True if self.weather.da >= self.weather.alt * 1.65 else False,
            'da_warning': da_warning,
            'crosswind': self.weather.crosswind,
            'runway': self.weather.runwayname,
            'suggested_runway': self.weather.suggested_runway,
            'suggested_runway_name': "%02d" % (self.weather.suggested_runway / 10),
            'first_runway': self.weather.rwyheading,
            'source': self.weather.source,
            'airfield_status': self.airfieldstatus,
            'airfield_status_text': '<div style="padding: 5px; vertical-align: middle; font-size: 14px;">%s</div>' % self.airfieldstatustext,
            'airfield_status_text_plain': self.airfieldstatustext,
            'fresh_meteo': self.weather.freshdata,
            'meteo_time': self.weather.time
        }

    @property
    def airfieldstatustext(self):
        if not 'airfieldstatus_url' in self.config:
            return ""
        url = self.config['airfieldstatus_url']

        try:
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.content, "html.parser")
            return soup.find_all('td')[2].text.split("\r\n")[2]
        except:
            return "Error fetching airfieldstatus"

    @property
    def airfieldstatus(self):
        if not 'airfieldstatus_url' in self.config:
            return 9
        url = self.config['airfieldstatus_url']

        try:
            r = requests.get(url, timeout=10)
            g = re.search("(?<=stufe.)\\d", r.content, re.I | re.S)
            if g:
                return int(g.group(0))
        except:
            return 9


if __name__ == "__main__":
    a = AerodromeWeather("lszi", alt=1788, rwyheading=250)
    #a.getWeatherLink(url="http://www.aecs-fricktal.ch/wetter/reports/downld02.txt")
    #a.getWeatherLinkOnline(station='lszi', password='Feelfree')