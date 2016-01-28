import re
from dateutil.parser import parse as parse_date


TITLE_RE = re.compile(r'\[(?P<group>[^\]]+)\]\s*(?P<title>.+?)[\s-]*(?:[Ss]?(?P<season>\d+)[\s-]+?)?(?P<episode>\d+)(?:-(?P<extra_episode>\d+))?\s*(?:\[[^\]]*(?P<quality>(360|720|1080))[^\]]*\])?')

class NyaaFile:
    link = ''
    group = None
    quality = None
    episode = None
    season = None

    def __init__(self, entry):
        self.link = entry.get('link', '')
        self.parse_title(entry.get('title', ''))
        self.parse_published(entry.get('published', ''))

    def parse_title(self, file_title):
        """Extract important parts of the file title and set as attributes on self"""
        matches = TITLE_RE.search(file_title)
        if matches:
            attrs = matches.groupdict()
            for key in list(attrs.keys()):
                attr = attrs[key]
                if attr:
                    if attr.isdigit():
                        attr = int(attr)
                    setattr(self, key, attr)

    def parse_published(self, published):
        if published:
            self.published = parse_date(published)

    def fits_criteria(self, group=None, quality=None, min_episode=None, min_season=None):
        """Checks this file fits the given criteria of group, quality, etc

        Fails check if a parameter is given and the matching attribute is not
        present for this file.
        """
        try:
            if group != None and (self.group == None or self.group.lower() != group.lower()):
                return False
            if quality != None and (self.quality == None or self.quality != quality):
                return False
            if min_episode != None and (self.episode == None or self.episode < min_episode):
                return False
            if min_season != None and (self.season == None or self.season < min_season):
                return False
            return True
        except AttributeError as attr_err:
            # Something isn't right about this file
            print('bad file', attr_err)
            return False

    def __str__(self):
        return str(self.__dict__)
