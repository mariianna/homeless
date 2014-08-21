# -*- coding: utf-8 -*-
import urllib,re,xbmcplugin,xbmcgui,xbmcaddon,os
import xbmc
import base64
import os
if sys.version_info >=  (2, 7):
    import requests
else:
    import urllib2
    import simplejson as json 


pluginhandle = int(sys.argv[1])
xbox = xbmc.getCondVisibility("System.Platform.xbox")
addon = xbmcaddon.Addon(id="plugin.video.revision3light")
home = addon.getAddonInfo('path').decode('utf-8')
image = xbmc.translatePath(os.path.join(home, 'icon.png'))
imageDir = os.path.join(home, 'thumbnails') + '/'
fanart=imageDir+"fanart.jpg"
base='http://revision3.com/api/'
apikey=base64.b64decode('YjBmNjk2ZmYzNDNiZWE1M2RiNTY0YjRmNTRkNDdmMTk4ODlhYmVhZg==')
show='getShows'
showURL='%s%s.json?api_key=%s' % (base,show,apikey)
episode='getEpisodes'
downloadpath= addon.getSetting('download_path')


def main():
       url=showURL
       data = getUrl(url)['shows']
       for entry in data:
         url=entry['id']
         name=entry['name']
         slug=entry['slug']
         desc=entry['summary']
         iconimage=entry['images']['logo_200']
         addDir(name,url,"index",iconimage)
       xbmcplugin.endOfDirectory(pluginhandle)
       xbmc.executebuiltin("Container.SetViewMode(500)")    

def index(url):
      rid=url
      url='%s%s.json?api_key=%s&show_id=%s' % (base,episode,apikey,rid)
      data = getUrl(url)['episodes']
      for entry in data:
        url=entry['media']['large']['url']
        name=entry['name']
        iconimage=entry['images']['medium']
        desc=entry['summary']
        addLink(name,url,"play",iconimage,desc)
      xbmcplugin.endOfDirectory(pluginhandle)
      xbmc.executebuiltin("Container.SetViewMode(515)")

def playVideo(url):
	    listitem = xbmcgui.ListItem(path=url)
	    return xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
	    

def Download(name,url):
    dp = xbmcgui.DialogProgress()
    dp.create("Revision 3 Light ","Downloading Video ",name)
    dest = (addon.getSetting('download_path')+name+'.mp4')
    dest = xbmc.makeLegalFilename(dest)
    urllib.urlretrieve(url,dest,lambda nb, bs, fs: _pbhook(nb,bs,fs,url,dp))
 
def _pbhook(numblocks, blocksize, filesize, url=None,dp=None):
    try:
        percent = min((numblocks*blocksize*100)/filesize, 100)
        print percent
        dp.update(percent)
    except:
        percent = 100
        dp.update(percent)
    if dp.iscanceled(): 
        print "DOWNLOAD CANCELLED" # need to get this part working
        dp.close()
        Download(url,dest) 	    		
    				
					    
	        
def addLink(name,url,mode,iconimage,desc):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name , "Plot": desc } )
        liz.setProperty('IsPlayable', 'true')
        liz.setProperty('fanart_image', fanart)
        liz.addContextMenuItems([('Download', 'XBMC.RunPlugin(%s?mode=59&name=%s&url=%s)' % (sys.argv[0], name, url))])
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok	    										   
        
def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok        

def getUrl(url):
	    if sys.version_info >=  (2, 7):
			headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:16.0) Gecko/20100101 Firefox/16.0'}
			r = requests.get(url, headers=headers)
			link=r.json()
			r.close()
			return link
            else:
			r = urllib2.urlopen(url)
			link=json.load(r)
			r.close()
			return link
		  
           		
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
name=params.get('name')
if type(url)==type(str()):
  url=urllib.unquote_plus(url)

if mode == 'index':
    index(url)

elif mode == 'play':
    playVideo(url)
    
elif mode == '59':
    Download(name,url)
    

else:
    main()

        
        
        
                
                                  
