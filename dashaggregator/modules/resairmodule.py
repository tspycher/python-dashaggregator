import requests
from bs4 import BeautifulSoup
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

    session = None
    tenant = None
    base = None

    def __init__(self, tenant, username, password):
        super(Resair, self).__init__()
        self.tenant = tenant
        self.base = 'https://www.resnet.ch/%d' % tenant
        self.login(username, password)

    def login(self, username, password):
        self.session = requests.Session()
        self.session.post("%s/login.asp" % self.base, data={'nom': username, 'pwd': password, 'oaci': 'mfgf'})

    def getEvents(self):
        r = self.session.get('%s/sortie.asp' % self.base)
        soup = BeautifulSoup(r.content, "html.parser")
        event_tables = soup.body.find_all('table', recursive=False)[1].find_all('table')
        events = []
        for event_table in event_tables:
            td = event_table.find_all('td')
            events.append(Event(td[0].b.text, td[1].b.text, td[3].text))

        return events

class ResairModule(Basemodule):
    resair = None

    def configure(self, config):
        super(ResairModule, self).configure(config)
        self.resair = Resair(self.config['tenant'], self.config['username'], self.config['password'])

    def _nothing_today(self):
        return Event(datetime.today().strftime('%d.%m.%Y'), '-', '-')

    def render(self):
        events = self.resair.getEvents()
        #event_today = filter(lambda x: x.date.date() == datetime.today().date(), events)
        event_today = filter(lambda x: x.date.date() == datetime(2017,11,07,23,10).date(), events)


        return {
            'today': event_today[0].render() if event_today else self._nothing_today().render(),
            'all': [e.render() for e in events]
        }

if __name__ == "__main__":
    m = Resair(1702, 'spycher', 'Feelfree')
    m.getEvents()
