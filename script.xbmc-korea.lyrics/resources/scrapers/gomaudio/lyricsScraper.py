# -*- Mode: python; coding: utf-8; tab-width: 8; indent-tabs-mode: t; -*-
"""
Scraper for http://newlyrics.gomtv.com/
"""

import md5
import urllib
import xbmc
import re

__title__ = "gomtv.com"
__allow_exceptions__ = False

GOM_URL = "http://newlyrics.gomtv.com/cgi-bin/lyrics.cgi?cmd=find_get_lyrics&file_key=%s&title=%s&artist=%s&from=gomaudio_local"

class gomClient(object):
    '''
    privide Gom specific function, such as key from mp3
    '''
    @staticmethod
    def GetKeyFromFile(file):
        from resources.lib.audiofile import AudioFile
        musf = AudioFile()
        musf.Open(file)
        buf = musf.ReadAudioStream(100*1024)	# 100KB from audio data
        musf.Close()
        # calculate hashkey
        m = md5.new(); m.update(buf);
        return m.hexdigest()

    @staticmethod
    def mSecConv(msec):
        s,ms = divmod(msec/10,100)
        m,s = divmod(s,60)
        return m,s,ms

class LyricsFetcher:
    def __init__( self ):
        self.base_url = "http://newlyrics.gomtv.com/"

    def get_lyrics(self, artist, song):
        musicFullPath = xbmc.Player().getPlayingFile()
        print musicFullPath
        key = gomClient.GetKeyFromFile( musicFullPath )
        if not key:
            return ''

        title = artist+' - '+song
        lyrics = self.get_lyrics_from_list( (title,key,artist,song) )
        return lyrics

    def get_lyrics_from_list(self, link):
        title,key,artist,song = link
        print key, artist, song
        print GOM_URL %(key, urllib.quote(song.decode("utf-8").encode("euc-kr")), urllib.quote(artist.decode("utf-8").encode("euc-kr")) )

        try:
            response = urllib.urlopen( GOM_URL %(key, urllib.quote(song.decode("utf-8").encode("euc-kr")), urllib.quote(artist.decode("utf-8").encode("euc-kr")) ) )
            Page = response.read()
        except Exception, e:
            print e

        if Page[:Page.find('>')+1] != '<lyrics_reply result="0">':
            print Page[:Page.find('>')+1]
            return ''
        syncs = re.compile('<sync start="(\d+)">([^<]*)</sync>').findall(Page)
        lyric = []
        lyric.append( "[ti:%s]" %song )
        lyric.append( "[ar:%s]" %artist )
        for sync in syncs:
            # timeformat conversion
            t = "%02d:%02d.%02d" % gomClient.mSecConv( int(sync[0]) )
            # unescape string
            s = unicode(sync[1], "euc-kr").encode("utf-8").replace("&apos;","'").replace("&quot;",'"')
            lyric.append( "[%s]%s" %(t,s) )
        return '\n'.join( lyric )

if ( __name__ == '__main__' ):
    script_home = 'D:\\test\\LRC Lyrics'

    import sys
    if not script_home in sys.path:
        sys.path.append( script_home )

    # used to test get_lyrics() 
    artist = "소녀시대"
    song = "소원을 말해봐"

    lyrics = LyricsFetcher().get_lyrics( artist, song )
    if ( isinstance( lyrics, list ) ):
        print "Unexpected multiple search results"
        for song in lyrics:
            print song
    else:
        print lyrics
# vim: softtabstop=4 tabstop=8 shiftwidth=4 expandtab
