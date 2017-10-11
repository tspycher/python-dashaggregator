#

import requests
from . import Basemodule

class InstagramModule(Basemodule):
    access_token = None

    def configure(self, config):
        super(InstagramModule, self).configure(config)
        if config and 'access_token' in self.config:
            self.access_token = self.config['access_token']


    def render(self):
        if not self.access_token: return {}
        data = requests.get('https://api.instagram.com/v1/users/self/media/recent/?count=1&access_token=%s' % self.access_token).json()
        return {
            "mostrecentpicture": data['data'][0]['images']['standard_resolution']['url'],
            "text": '<div style="padding: 10px; vertical-align: middle; font-size: 12px;">%s</div>' % data['data'][0]['caption']['text'],
            "text_raw": data['data'][0]['caption']['text'],
            "likes": data['data'][0]['likes']['count']
        }