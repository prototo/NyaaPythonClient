import requests
import feedparser
from nyaaclient.file import NyaaFile
import nyaaclient.trustfilter as TrustFilter


class NyaaClient:
    base_path = 'http://www.nyaa.se/?page=rss&cats=1_37&filter={filter}&sort=2&term={term}'

    def __init__(self):
        self.session = requests.Session()

    def search(self, term, group=None, min_episode=None, min_season=None, quality=None, trust_filter=TrustFilter.TrustedOnly):
        path = self.base_path.format(**{'term': term, 'filter': trust_filter})
        (status, body) = self.request(path)

        if status != 200:
            return None

        rss = feedparser.parse(body)
        entries = rss.get('entries', [])
        entries = self.parse_entries(entries)

        # only return items that fit any given criteria
        return [entry for entry in entries if entry.fits_criteria(group, quality, min_episode, min_season)]

    def get_available_groups(self, term):
        items = self.search(term)
        groups = {}
        for item in items:
            group, quality = item.group, item.quality
            if group:
                groups[group] = groups.get(group, set())
                if quality:
                    groups[group].add(quality)
        return groups

    def request(self, path, data={}):
        res = self.session.get(path, data=data)
        return int(res.status_code), res.text

    def parse_entries(self, entries):
        return [NyaaFile(e) for e in entries]
