from plugin import plugin
import urllib2
import json

class ustream(plugin):

    url = "http://api.ustream.tv/json/channel/all/search/title:eq:"
    website = "http://www.ustream.tv/channel/"

    @classmethod
    def get_streams(cls, streams):
        liveStreams = {}
        for stream in streams:
            data = json.loads(urllib2.urlopen(cls.url+stream).read())
            if data["results"][0]["status"] == "live":
                liveStreams[stream] = (data["results"][0]["title"], data["results"][0]["viewersNow"])

        return liveStreams
