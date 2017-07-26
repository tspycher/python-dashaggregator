import feedparser
from datetime import datetime
from . import Basemodule


class RssModule(Basemodule):
    def configure(self, config):
        super(RssModule, self).configure(config)
        self.config['feed_url']

    def render(self):
        feed = feedparser.parse(self.config['feed_url'])

        result = []
        for i in feed['entries'][:3]:
            result.append({'content': i['content'][0]['value'], 'title': i['title'], 'published': i['published'], 'summary': i['summary']})
        return result