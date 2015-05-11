import requests
import feedparser
import re
from datetime import datetime
from urllib.request import urlretrieve
from enum import Enum

class TrustFilter(Enum):
    ShowAll = 0
    FilterRemakes = 1
    TrustedOnly = 2
    AOnly = 3

class NyaaFile:
    title = ''
    link = ''
    published = ''

    group = None
    quality = None
    season = None
    episode = None
    extra_episode = None

    def __init__(self, entry):
        self.file_title = entry.get('title', '')
        self.link = entry.get('link', '')
        self.published = entry.get('published', '')

        self.parse_title()
        self.parse_published()

    def parse_title(self):
        reg = r'\[(?P<group>[^\]]+)\]\s*(?P<title>.+?)[\s-]+.*?[\s-]*?(?:[Ss]?(?P<season>\d+)[\s-]+?)?(?P<episode>\d+)(?:-(?P<extra_episode>\d+))?\s*(?:\[[^\]]*(?P<quality>(360|720|1080))[^\]]*\])?'
        matches = re.search(reg, self.file_title)

        if matches:
            attrs = matches.groupdict()
            for key in list(attrs.keys()):
                setattr(self, key, attrs[key])

    def parse_published(self):
        if self.published:
            self.published = datetime.strptime(self.published, '%a, %d %b %Y %H:%M:%S %z')

    def __str__(self):
        return str(self.__dict__)

class NyaaClient:
    base_path = 'http://www.nyaa.se/?page=rss&cats=1_37&filter={filter}&sort=2&term={term}'
    session = None

    def __init__(self):
        self.session = requests.Session()
        pass

    def __getattr__(self, item):
        return self.search(item)

    def search(self, term, group=None, episode=None, season=None, quality=None, trust_filter=TrustFilter.TrustedOnly):
        path = self.base_path.format(**{'term': term, 'filter': trust_filter})
        status, body = self.request(path)

        if int(status) != 200:
            return None

        rss = feedparser.parse(body)
        items = rss.get('entries', [])
        items = self.parse_entries(items)

        if group != None:
            items = list(filter(lambda item: item.group and item.group.lower() == group.lower(), items))
        if episode != None:
            items = list(filter(lambda item: item.episode and int(item.episode) >= episode, items))
        if season != None:
            items = list(filter(lambda item: item.season and int(item.season) >= season, items))
        if quality != None:
            items = list(filter(lambda item: item.quality and item.quality.lower() == quality.lower(), items))

        return items

    def get_available_groups(self, term):
        items = self.search(term)
        groups = {}
        for item in items:
            if item.group:
                groups[item.group] = groups.get(item.group, [])
                if item.quality and item.quality not in groups[item.group]:
                    groups[item.group].append(item.quality)
        return groups

    def request(self, path, data={}):
        res = self.session.get(path, data=data)
        return res.status_code, res.text

    def parse_entries(self, entries):
        return [NyaaFile(e) for e in entries]

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        title = sys.argv[1]
        c = NyaaClient()
        r = c.get_available_groups(title)
        print(r)
