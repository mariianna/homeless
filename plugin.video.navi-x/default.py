#############################################################################
#
# Navi-X Playlist browser
# v2.7 by rodejo (rodejo16@gmail.com)
#
# -v2.7   (2009/04/11)
#
# Changelog (v2.7)
# -Added new playlist item called 'processor'. Points to a playlist item processing server.
# -Youtube fix
# -Added PLX playlist multiline comment tag (""").
#
#############################################################################

import xbmc, xbmcgui, xbmcplugin, urllib2, urllib, re, string, sys, os, traceback, xbmcaddon

sys.path.append(os.path.join(xbmcaddon.Addon(id='plugin.video.navi-x').getAddonInfo('path').replace(";",""),'src'))
from libs2 import *
from navix import *

######################################################################
# Description: 
######################################################################
def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param

######################################################################
# Description: 
######################################################################

params=get_params()

mediaitem=CMediaItem(name="Navi-X home", type="playlist", URL="http://navi-x.googlecode.com/svn/trunk/Playlists/home.plx")

try:
        mediaitem.URL = urllib.unquote_plus(params["url"])
except:
        pass
try:
        mediaitem.name = urllib.unquote_plus(params["name"])
except:
        pass
try:
        mediaitem.type = urllib.unquote_plus(params["type"])
except:
        pass
try:
        mediaitem.processor = urllib.unquote_plus(params["processor"])
except:
        pass
try:
        mediaitem.date = urllib.unquote_plus(params["date"])
except:
        pass         
#try:
#        mode=int(params["mode"])
#except:
#        pass
#try:
#        page=int(params["page"])
#except:
#        pass

#Trace(type + " " + name + " " + url + '\n')

Init()

SelectItem(mediaitem)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
	
