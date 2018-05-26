import requests
from bs4 import BeautifulSoup
import hashlib
from datetime import datetime
import pytz
from dashaggregator.modules import Basemodule


class Event(object):
    def __init__(self, date, title, description):
        super(Event, self).__init__()
        self.date = pytz.timezone('Europe/Zurich').localize(datetime.strptime(date, '%d.%m.%Y'))
        self.title = title
        self.description = description

    date = None
    title = None
    description = None

    @property
    def description_text(self):
        return unicode(self.description).replace('<br>', ' ')

    def render(self):
        return {
            'date': self.date.strftime('%d.%m.%y'),
            'title': self.title,
            'description': self.description,
            'html': '<div style="padding: 7px; vertical-align: middle; font-size: 20px;"><strong>%s - %s</strong><hr /><span style="font-size: 18px;">%s</span></div>' % (self.date.strftime('%d.%m.%y'), self.title, self.description_text),
        }

class Resair(object):
    secret = None
    base = None

    def __init__(self, secret):
        super(Resair, self).__init__()
        self.secret = secret

    @property
    def password(self):
        now = datetime.now(tz=pytz.timezone('Europe/Zurich')).strftime('%Y%m%d')
        return hashlib.md5("%s%s" % (self.secret, now)).hexdigest()

    def getUsers(self):
        r = requests.get('https://www.resnet.ch/api/mfgf-export-mbr.asp', {"p": self.password})

    def getEvents(self):
        r = requests.get('https://www.resnet.ch/api/mfgf-export-sorties.asp', {"p": self.password})
        data = r.json()

        events = []
        for event in data:
            events.append(Event(event['DateDebut'], event['Titre'], event['Description']))

        return events
        #return [Event(datetime.today().strftime('%d.%m.%Y'), 'currently disabled', 'datafeed has currently been disabled')]

class ResairModule(Basemodule):
    resair = None

    def configure(self, config):
        super(ResairModule, self).configure(config)
        self.resair = Resair(self.config['secret'])

    def _nothing_today(self):
        return Event(datetime.today().strftime('%d.%m.%Y'), 'no Event', '-')

    def render(self):
        events = self.resair.getEvents()
        event_today = filter(lambda x: x.date.date() == datetime.today().date(), events)

        return {
            'today': event_today[0].render() if event_today else self._nothing_today().render(),
            'all': [e.render() for e in events]
        }

if __name__ == "__main__":
    m = Resair('mfgf_2875345')
    e = m.getEvents()
    #u = m.getUsers()
    pass