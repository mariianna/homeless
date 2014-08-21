

import urllib,urllib2,re,xbmcplugin,xbmcgui,httplib,htmllib,xbmc

PLUGIN              ='plugin.audio.radiobob'
VERSION             ='0.1'
USER_AGENT          ='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'


url = 'http://stream01.hoerradar.de/mp3-radiobob.m3u'
xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(url)
