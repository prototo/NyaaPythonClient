import os
from nyaa_client.client import NyaaClient
from urllib.request import urlretrieve


class NyaaSubscription:
    term = None
    next_episode = 0
    group = None
    quality = None

    client = None
    new_files = []

    def __init__(self, term, next_episode, group=None, quality=None):
        self.term = term
        self.next_episode = next_episode
        self.group = group
        self.quality = quality

        self.client = NyaaClient()

    """
        Check for new files for this subscription
    """
    def check(self):
        items = self.client.search(self.term, self.group, self.next_episode, quality=self.quality)
        self.new_files += sorted(items, key=lambda item: item.episode)
        return self.new_files

    """
        Download the new files available for this subscription
        Calls self.check to update the new files list
    """
    def download_new(self, directory=None):
        # update the new files list
        self.check()

        if len(self.new_files) and directory:
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                # oh
                pass

        while len(self.new_files):
            item = self.new_files.pop(0)
            print('downloading', item.file_title)
            file_path = '.'.join((item.file_title, 'torrent'))
            if directory:
                file_path = os.path.join(directory, file_path)
            urlretrieve(item.link, file_path)

s = NyaaSubscription('jojo', 0, 'HorribleSubs', '720')
s.download_new('torrents')

