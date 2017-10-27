
import base64
from datetime import datetime, timedelta
import requests
import pytz
import tempfile
import os
from bs4 import BeautifulSoup
from dashaggregator.modules import Basemodule


class Dabs(object):
    # url = 'http://www.skyguide.ch/fileadmin/dabs-%(day)s/DABS_%(date)s.pdf'
    url = 'https://www.skybriefing.com/portal/en/home?p_p_id=dabsportlet_WAR_ibsportletdabs&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=APP&p_p_cacheability=cacheLevelPage&p_p_col_id=column-3&p_p_col_count=3&_dabsportlet_WAR_ibsportletdabs_v-resourcePath=%%2FAPP%%2Fconnector%%2F0%%2F8%%2Fhref%%2Fdabs-%(date)s.pdf'

    def _url(self, tomorrow=False):
        return self.url % {
            "day": 'today' if not tomorrow else 'tomorrow',
            "date": datetime.now(tz=pytz.timezone('Europe/Zurich')).strftime('%Y-%m-%d') if not tomorrow else (datetime.now(tz=pytz.timezone('Europe/Zurich')) + timedelta(days=1)).strftime('%Y-%m-%d')
        }

    def _download(self, url):
        s = requests.Session()

        s.get('https://www.skybriefing.com/portal/en/')
        r = s.get(url, stream=True)

        if r.status_code == requests.codes.ok:
            r.raw.decode_content = True
            return base64.b64encode(r.raw.read())

    @property
    def today(self):
        return self._download(self._url())

    @property
    def tomorrow(self):
        return self._download(self._url(tomorrow=True))

class SwissAirspaceModule(Basemodule):
    refreshrate = 5 * 60

    def render(self):
        return {
            "dabs_html_image": '<img width="500" src="%s" />' % self.base64image(self.dabs),
            "gafor_html_image": '<img width="500" src="%s" />' % self.base64image(self.gafor)
        }

    @property
    def dabs(self):
        dabs = Dabs()
        dabs_pdf = os.path.join(tempfile.gettempdir(), 'dabs_today.pdf')
        with open(dabs_pdf, 'w') as f:
            f.write(base64.b64decode(dabs.today))

        return '/Users/tspycher/Desktop/dabs.png'

    @property
    def gafor(self):
        return '/Users/tspycher/Desktop/dabs.png'

    def base64image(self, file):
        with open(file, "rb") as image_file:
            base64file = base64.b64encode(image_file.read())

        return 'data:image/png;base64, %s' % base64file



if __name__ == "__main__":
    import requests
    import base64

    #s = requests.Session()

    fuckingquery = {
        'p_p_id': 'dabsportlet_WAR_ibsportletdabs',
        'p_p_lifecycle': 2,
        'p_p_state': 'normal',
        'p_p_mode': 'view',
        'p_p_resource_id': 'APP',
        'p_p_cacheability': 'cacheLevelPage',
        'p_p_col_id': 'column-3',
        'p_p_col_count': 3,
        '_dabsportlet_WAR_ibsportletdabs_v-resourcePath': '/APP/connector/0/2/href/dabs-2017-10-26.pdf'
    }

    fuckingcookies = {
        'JSESSIONID': '$xc/HhYDWcOhNNq9EHAra0hWhfqU1jEObuttlp8t0JmBpQ9fpbb9dI1yEwMZjk0_hPVBrphAHg=='
    }

    r1 = requests.get('https://www.skybriefing.com/portal/en/')
    soup = BeautifulSoup(r1.content, "html.parser")

    alllinks = []
    for text in soup.find_all('div', class_='skb-dabslink'):
        alllinks = alllinks + [l.get('href') for l in text.find_all('a')]


    jar = requests.cookies.RequestsCookieJar()
    jar.set('JSESSIONID', r1.cookies['JSESSIONID'], domain='www.skybriefing.com', path='/portal/')

    r = requests.get('https://www.skybriefing.com/portal/en/home', stream=True, params=fuckingquery, cookies=jar)

    if r.status_code == requests.codes.ok:
        r.raw.decode_content = True
        print r.raw.read()
        #print base64.b64encode(r.raw.read())