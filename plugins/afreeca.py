from plugin import plugin
import urllib2
import xml.etree.ElementTree as et

class afreeca(plugin):

    url = "http://afbbs.afreeca.com:8080/api/video/get_bj_liveinfo.php?szBjId="
    website = "http://play.afreeca.com/"

    @classmethod
    def get_streams(cls, streams):
        liveStreams = {}
        for stream in streams:
            data = urllib2.urlopen(cls.url+stream).read()
            isLive = int(et.fromstring(data).findall('result')[0].text)
            if isLive:
                viewerCount = et.fromstring(data).findall('view_cnt')[0].text
                liveStreams[stream] = (stream, viewerCount)

        return liveStreams
