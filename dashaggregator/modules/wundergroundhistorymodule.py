import datetime
import pytz
import requests
from dashaggregator.modules import Basemodule
from dateutil import parser

class WundergroundhistoryException(Exception):
    pass

class WundergroundhistoryModule(Basemodule):
    refreshrate = 300
    apikey = None
    pws = None
    timerange = None

    def configure(self, config):
        super(WundergroundhistoryModule, self).configure(config)
        self.apikey = self.config['apikey']
        self.pws = self.config['pws']
        self.timerange = self.config['timerange'] if 'timerange' in self.config else 60

    def render(self):
        today = datetime.datetime.now(tz=pytz.timezone('Europe/Zurich')).strftime('%Y%m%d')
        url = 'http://api.wunderground.com/api/%s/history_%s/q/pws:%s.json' % (self.apikey, today, self.pws)
        r = requests.get(url)
        data = r.json()
        if 'error' in data['response']:
            raise WundergroundhistoryException(data['response']['error']['type'])

        start = datetime.datetime.now(tz=pytz.timezone('Europe/Zurich'))
        end = datetime.datetime.now(tz=pytz.timezone('Europe/Zurich'))-datetime.timedelta(minutes=self.timerange)

        relevant_records = filter(lambda x: parser.parse(x['utcdate']['pretty']) >= end and parser.parse(x['utcdate']['pretty']) <= start, data['history']['observations'])

        avg_winddir = sum(int(r['wdird']) for r in relevant_records) / len(relevant_records)
        avg_wind = (sum(float(r['wspdm']) for r in relevant_records) / len(relevant_records)) * 0.539957 #kmh -> kt
        avg_gust = (sum(float(r['wgustm']) for r in relevant_records) / len(relevant_records)) * 0.539957 #kmh -> kt
        max_gust = float(reduce(lambda a, b: a if float(a['wgustm']) >= float(b['wgustm']) else b, relevant_records)['wgustm']) * 0.539957 #kmh -> kt
        max_wind = float(reduce(lambda a, b: a if float(a['wspdm']) >= float(b['wspdm']) else b, relevant_records)['wspdm']) * 0.539957 #kmh -> kt

        return {
            'avg_winddir': avg_winddir,
            'avg_wind_kt': round(avg_wind, 1),
            'avg_gust_kt': round(avg_gust, 1),
            'max_gust_kt': round(max_gust, 1),
            'max_wind_kt': round(max_wind, 1),
        }

if __name__ == "__main__":
    s = WundergroundhistoryModule('wundergroundhistory')
    s.configure(config={'apikey':'d15f0bdf210bec6d', 'pws':'ISCHUPFA3'})

    print s.render()


