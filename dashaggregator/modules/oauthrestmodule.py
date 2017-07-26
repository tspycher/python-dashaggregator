import requests
import urllib
from . import Basemodule

class OauthRestModule(Basemodule):
    _client_id = None
    _client_secret = None
    _username = None
    _password = None
    _grant_type = None

    _base = None
    _request_token_url = None
    _authorize_url = None
    _scope = None

    _access_token = None

    def _getConfig(self, name, default=None):
        if name in self.config:
            return self.config[name]
        return default

    def configure(self, config):
        super(OauthRestModule, self).configure(config)
        self._client_id = self._getConfig('client_id')
        self._client_secret = self._getConfig('client_secret')
        self._consumer_key = self._getConfig('consumer_key')
        self._consumer_secret = self._getConfig('consumer_secret')

        self._username = self._getConfig('username')
        self._password = self._getConfig('password')
        self._grant_type = self._getConfig('grant_type')

        self._base = self._getConfig('base')
        self._request_token_url = self._getConfig('request_token_url')
        self._authorize_url = self._getConfig('authorize_url')
        self._scope = self._getConfig('scope')
        self._authenticate()

    def _authenticate(self):
        headers = {'Content-type': 'application/x-www-form-urlencoded'}

        if self._grant_type.lower() == 'client_credentials':
            import base64
            data = {'grant_type': self._grant_type}
            headers['Authorization'] = 'Basic %s' % base64.b64encode("%s:%s" % (self._consumer_key, self._consumer_secret))
        else:
            data = {
                'grant_type': self._grant_type,
                'client_id': self._client_id,
                'client_secret': self._client_secret,
            }

        if self._username: data['username'] = self._username
        if self._password: data['password'] = self._password
        if self._scope: data['scope'] = self._scope

        r = requests.post(self._request_token_url, headers=headers, data=urllib.urlencode(data), verify=False)
        rj = r.json()
        self._access_token = rj['access_token']

    def __getattr__(self, item):
        if not getattr(super(OauthRestModule, self), item, None):  # would this create a new attribute?
            return self.__call(self._base % item, self._getConfig('parameters', {}))
        return getattr(super(OauthRestModule, self), item)

    def __call(self, url, params={}):
        r = requests.get(url, headers={'Authorization': 'Bearer %s' % self._access_token}, params=params, verify=False)
        return r.json()

    def render(self):
        data = getattr(self, self.config['endpoint'])

        if 'datafilter' in self.config:
            for x in str(self.config['datafilter']).split('.'):
                if isinstance(data, list):
                    data = data[int(x)]
                else:
                    data = data[x]

        return data
