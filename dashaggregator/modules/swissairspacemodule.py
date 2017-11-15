
import base64
from datetime import datetime, timedelta
import requests
import pytz
import tempfile
import os
from bs4 import BeautifulSoup
from subprocess import call

from dashaggregator.modules import Basemodule

class Gafor(object):
    url = 'https://www.skybriefing.com/portal/en/gafor?p_p_id=meteogaforportlet_WAR_ibsportletmeteo&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_cacheability=cacheLevelPage&_meteogaforportlet_WAR_ibsportletmeteo_skb_resource=%2Fusr%2Fjava%2Fliferay%2Ftomcat%2Ftemp%2Fibs_weatherbriefing_903930574.png'

class Dabs(object):
    url = 'https://www.skybriefing.com/portal/delegate/dabs?%s'

    def _url(self, tomorrow=False):
        return self.url % ('today' if not tomorrow else 'tomorrow')

    def _download(self, url, store=False):
        r = requests.get(url, stream=True)
        if r.status_code == requests.codes.ok:
            r.raw.decode_content = True
            if not store:
                return base64.b64encode(r.raw.read())
            else:
                filename = tempfile.mkstemp(prefix='dabs', suffix='pdf')[1]
                with open(filename, 'w') as f:
                    f.write(r.raw.read())
                return filename
        return None

    @property
    def today(self):
        return self._download(self._url(), store=True)

    @property
    def tomorrow(self):
        return self._download(self._url(tomorrow=True), store=True)

    @property
    def todaydata(self):
        return self._download(self._url(), store=False)

    @property
    def tomorrowdata(self):
        return self._download(self._url(tomorrow=True), store=False)

class SwissairspaceModule(Basemodule):
    refreshrate = 5 * 60

    def render(self):
        return {
            "dabs": self.base64image(self.convertPdf2Image(self.dabs))
        }

    @property
    def dabs(self):
        return Dabs().today

    @property
    def gafor(self):
        return '/Users/tspycher/Desktop/gafor.png'

    def convertPdf2Image(self, file):
        imagefile = tempfile.mkstemp(prefix='airspace', suffix='png')[1]

        try:
            backval = call(["gs", "-dBATCH", "-dNOPAUSE", "-sDEVICE=png16m", "-r400", "-dFirstPage=1", "-dLastPage=1", "-sOutputFile=%s" % imagefile, file])
            if not backval == 0:
                return None
        except OSError:
            return None

        image = base64.b64encode(open(imagefile, "rb").read())

        os.remove(file)
        os.remove(imagefile)
        return image

    def base64image(self, base64file, isFile=False):
        if isFile:
            with open(base64file, "rb") as image_file:
                base64file = base64.b64encode(image_file.read())

        return 'data:image/png;base64,%s' % base64file

if __name__ == "__main__":
    import requests
    import base64


    sa = SwissairspaceModule('skybriefing')

    pdfile = sa.dabs
    #print sa.render()
    print sa.base64image(sa.convertPdf2Image(pdfile))
    #s = requests.Session()

    #fuckingquery = {
    #    'p_p_id': 'dabsportlet_WAR_ibsportletdabs',
    #    'p_p_lifecycle': 2,
    #    'p_p_state': 'normal',
    #    'p_p_mode': 'view',
    #    'p_p_resource_id': 'APP',
    #    'p_p_cacheability': 'cacheLevelPage',
    #    'p_p_col_id': 'column-3',
    #    'p_p_col_count': 3,
    #    '_dabsportlet_WAR_ibsportletdabs_v-resourcePath': '/APP/connector/0/2/href/dabs-2017-10-26.pdf'
    #}

    #fuckingcookies = {
    #    'JSESSIONID': '$xc/HhYDWcOhNNq9EHAra0hWhfqU1jEObuttlp8t0JmBpQ9fpbb9dI1yEwMZjk0_hPVBrphAHg=='
    #}

    #r1 = requests.get('https://www.skybriefing.com/portal/en/')
    #soup = BeautifulSoup(r1.content, "html.parser")

    #alllinks = []
    #for text in soup.find_all('div', class_='skb-dabslink'):
    #    alllinks = alllinks + [l.get('href') for l in text.find_all('a')]


    #jar = requests.cookies.RequestsCookieJar()
    #jar.set('JSESSIONID', r1.cookies['JSESSIONID'], domain='www.skybriefing.com', path='/portal/')

    #r = requests.get('https://www.skybriefing.com/portal/en/home', stream=True, params=fuckingquery, cookies=jar)

    #if r.status_code == requests.codes.ok:
    #    r.raw.decode_content = True
    #    print r.raw.read()
    #    #print base64.b64encode(r.raw.read())