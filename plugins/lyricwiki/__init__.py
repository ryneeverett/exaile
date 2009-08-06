from xl.lyrics import LyricSearchMethod
from xl.lyrics import LyricsNotFoundException
from xl import event
import re

try:
    import xml.etree.cElementTree as cETree
except:
    import cElementTree as cETree

import urllib

def enable(exaile):
    """
        Enables the lyric wiki plugin that fetches track lyrics
        from lyricswiki.org
    """
    if exaile.loading:
        event.add_callback(_enable, "exaile_loaded")
    else:
        _enable(None, exaile, None)

def _enable(eventname, exaile, nothing):
    exaile.lyrics.add_search_method(LyricWiki())


def disable(exaile):
    exaile.lyrics.remove_search_method_by_name("lyricwiki")

class LyricWiki(LyricSearchMethod):
    
    name= "lyricwiki"
    def find_lyrics(self, track):
        search = "http://lyricwiki.org/api.php?artist=%s&song=%s&fmt=xml" % (
            urllib.quote_plus(track["artist"][0]), 
            urllib.quote_plus(track["title"][0]))
        sock = urllib.urlopen(search)
        xml = sock.read()
        sock.close()
        try:
            (lyrics, url) = self.parse_xml(xml)
        except:
            raise LyricsNotFoundException
        if lyrics == "Not found":
            raise LyricsNotFoundException
        html = urllib.urlopen(url).read()
        lyrics = re.search("<div class='lyricbox' >(.*)", html).group(1)
        lyrics = lyrics.replace("<br />", "\n")
        return (lyrics, "Lyric Wiki",url)

    def parse_xml(self, xml):
        """
            Parses the xml into the lyrics and the URL
        """
        tree = cETree.XML(xml)
        lyrics = tree.find("lyrics").text
        url = tree.find("url").text
        return (lyrics, url)
