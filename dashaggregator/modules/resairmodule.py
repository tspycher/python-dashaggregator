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

    def render(self):
        return {
            'date': self.date.strftime('%d.%m.%y'),
            'title': self.title,
            'description': self.description,
            'html': '<div style="padding: 10px; vertical-align: middle; font-size: 20px;"><strong>%s</strong><br />%s</div>' % (self.date.strftime('%d.%m.%y'), self.description),
        }

class Resair(object):
    secret = None
    base = None

    def __init__(self, secret): #tenant, username, password):
        super(Resair, self).__init__()
        self.secret = secret
        #self.tenant = tenant
        #self.base = 'https://www.resnet.ch/%d' % tenant
        #self.login(username, password)

    @property
    def password(self):
        now = datetime.now(tz=pytz.timezone('Europe/Zurich')).strftime('%Y%m%d')
        return hashlib.md5("%s%s" % (self.secret, now)).hexdigest()
        #r = requests.get('https://www.resnet.ch/api/mfgf-export-mbr.asp', {"p": pwd})
        #print r.content

    #def login(self, username, password):
        #self.session = requests.Session()

        # Disabled due to Resaircall
        #self.session.post("%s/login.asp" % self.base, data={'nom': username, 'pwd': password, 'oaci': 'mfgf'})

    def getUsers(self):
        r = requests.get('https://www.resnet.ch/api/mfgf-export-mbr.asp', {"p": self.password})
        print r.content

    def getEvents(self):
        '''r = self.session.get('%s/sortie.asp' % self.base)
        soup = BeautifulSoup(r.content, "html.parser")
        event_tables = soup.body.find_all('table', recursive=False)[1].find_all('table')
        events = []
        for event_table in event_tables:
            td = event_table.find_all('td')
            events.append(Event(td[0].b.text, td[1].b.text, td[3].text))

        return events'''

        return [Event(datetime.today().strftime('%d.%m.%Y'), 'currently disabled', 'datafeed has currently been disabled')]

class ResairModule(Basemodule):
    resair = None

    def configure(self, config):
        super(ResairModule, self).configure(config)
        self.resair = Resair(self.config['secret'])

    def _nothing_today(self):
        return Event(datetime.today().strftime('%d.%m.%Y'), '-', '-')

    def render(self):
        events = self.resair.getEvents()
        event_today = filter(lambda x: x.date.date() == datetime.today().date(), events)

        return {
            'today': event_today[0].render() if event_today else self._nothing_today().render(),
            'all': [e.render() for e in events]
        }

if __name__ == "__main__":
    m = Resair('R3s@ir4_Mfgf')
    m.getEvents()
    m.getUsers()
