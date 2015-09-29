from nyaa_client.subscriber import NyaaSubscription


s = NyaaSubscription('jojo', 0, 'HorribleSubs', '720')
s.download_new('torrents')

