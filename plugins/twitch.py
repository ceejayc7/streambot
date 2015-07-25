from plugin import plugin
import urllib2
import json

class twitch(plugin):

    url = "https://api.twitch.tv/kraken/streams?channel="
    website = "http://www.twitch.tv/"

    @classmethod
    def get_streams(cls, streams):
        # Clear URL
        baseUrl = cls.url

        # TODO: Can twitch handle over 100 streams on one call?
        for stream in streams:
            baseUrl += stream +","
        baseUrl = baseUrl[:-1]

        req = urllib2.Request(baseUrl)
        req.add_header('Accept','application/vnd.twitchtv.v2+json')
        res = urllib2.urlopen(req)
        jsonResponse = json.loads(res.read())
        liveStreams = {}
        for stream in jsonResponse["streams"]:
            liveStreams[stream["channel"]["name"]] = (stream["channel"]["status"],stream["viewers"])
        return liveStreams
