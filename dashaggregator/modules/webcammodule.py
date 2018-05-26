import datetime
import pytz
import requests
from dashaggregator.modules import Basemodule


class WebcamModule(Basemodule):
    refreshrate = 300
    cams = None


    def configure(self, config):
        super(WebcamModule, self).configure(config)
        if not 'cams' in self.config:
            self.cams = []
        else:
            self.cams = self.config['cams']
    def render(self):
        #cams = ['birrfeld', 'engadin-airport', 'fliegen', 'gstaad-airport', 'albiswings']
        data = {}

        for c in self.cams:
            settings_url = "https://%s.roundshot.com/settings.json" % c
            structure_url = "https://%s.roundshot.com/structure.json" % c

            settings = requests.get(settings_url).json()
            structure = requests.get(structure_url).json()

            lastimage = filter(lambda x: x['id'] == settings['last_image'], structure['images'])[0]
            lastimage_datetime = pytz.timezone('Europe/Zurich').localize(datetime.datetime.utcfromtimestamp(lastimage['datetime']))  # .replace(tzinfo=pytz.timezone(timezone))
            now = datetime.datetime.now(tz=pytz.timezone('Europe/Zurich'))
            age = (now - lastimage_datetime).total_seconds() / 60  # minutes

            data[c] = {}
            data[c]['name'] = settings['customer_name']
            data[c]['current'] = 'https://backend.roundshot.com/cams/%s/original' % settings['hash']
            data[c]['current_half'] = 'https://backend.roundshot.com/cams/%s/half' % settings['hash']
            data[c]['current_thumbnail'] = 'https://backend.roundshot.com/cams/%s/thumbnail' % settings['hash']
            data[c]['image_datetime'] = lastimage_datetime.strftime('%d.%m.%y %H:%M')
            data[c]['iscurrent'] = True if age <= 60 else False

        return data

if __name__ == "__main__":
    s = WebcamModule('webcam')

    print(s.render())


