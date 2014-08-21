#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmcplugin,xbmcgui,sys,xbmcaddon,requests,re,os
from requests_oauthlib import OAuth1
from urllib import quote, unquote_plus, unquote, urlencode,quote_plus,urlretrieve

pluginhandle = int(sys.argv[1])
addon = xbmcaddon.Addon(id='plugin.video.vimeosearch')
home = addon.getAddonInfo('path').decode('utf-8')
imageDir = os.path.join(home, 'thumbnails') + '/'
fanart=imageDir+"fanart.jpg"

VIMEO_CLIENTID='1170e6c3406aed0005e37249a01a4828a320753d'
VIMEO_CLIENTSECRET='0e84266daaa4f588ce9fa19947482661533a0391'
VIMEO_ACCESSTOKEN='277729cb4d65df594fe41bb56989ef86'
VIMEO_ACCESSTOKENSECRET='4578d6a548bc097829f50a020624b016e325387d'
auth = OAuth1(VIMEO_CLIENTID,VIMEO_CLIENTSECRET,VIMEO_ACCESSTOKEN,VIMEO_ACCESSTOKENSECRET)

def MovieSearch():
    search_entered =search()
    url='http://vimeo.com/api/rest/v2?format=json&method=vimeo.videos.search&summary_response=1&query=%s' % search_entered
    data=requests.get(url, auth=auth).json()['videos']['video']
    for video in data:
		name=video['title'].encode('utf-8')
		url=video['id']
		iconimage=video['thumbnails']['thumbnail'][1]['_content']
		fanart=video['thumbnails']['thumbnail'][2]['_content']
		addLink(name,url,"play",iconimage,'')
              
              
              
def search():
        search_entered = ''
        keyboard = xbmc.Keyboard(search_entered, 'Vimeo Search')
        keyboard.doModal()
        if keyboard.isConfirmed():
            search_entered = keyboard.getText() .replace(' ','+')  # sometimes you need to replace spaces with + or %20
            if search_entered == None:
                return False          
        return search_entered
        
def play(url):
	    vimeo_id=url
	    url='http://player.vimeo.com/v2/video/%s/config?type=moogaloop&referrer=&player_url=player.vimeo.com&v=1.0.0&cdn_url=http://a.vimeocdn.com' % vimeo_id
	    try:
	      Video_url=requests.get(url).json()['request']['files']['h264']['sd']['url']
	    except:
		  Video_url=requests.get(url).json()['request']['files']['vp6']['sd']['url']
	    listitem = xbmcgui.ListItem(path=Video_url)
	    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
			

def addLink(name,url,mode,iconimage,desc):
        u=sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name , "Plot": desc } )
        liz.setProperty('IsPlayable', 'true')
        liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok

def parameters_string_to_dict(parameters):
    ''' Convert parameters encoded in a URL to a dict. '''
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict

params=parameters_string_to_dict(sys.argv[2])
mode=params.get('mode')
url=params.get('url')
if type(url)==type(str()):
  url=unquote_plus(url)




if mode == 'play':
    play(url)

else:
    MovieSearch()

xbmcplugin.endOfDirectory(pluginhandle) 






















#vimeo_url='http://vimeo.com/12339592'
#vimeo_id=vimeo_url.split('/')[3]
#url='http://player.vimeo.com/v2/video/%s/config?type=moogaloop&referrer=&player_url=player.vimeo.com&v=1.0.0&cdn_url=http://a.vimeocdn.com' % vimeo_id
#url=requests.get(url).json()['request']['files']['h264']['sd']['url']
#os.system("cvlc "+url)





