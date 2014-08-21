import urllib2,urllib,re,xbmcplugin,xbmcgui

# UBU videos 2008.

# Get all the artists who have videos
def Artists():
        req = urllib2.Request("http://www.ubu.com/film/")
        response = urllib2.urlopen(req)
        link = response.read()
        ALL=re.compile('<a href=\"./(.+?)\">(.+?)</a>').findall(link)
        count = len(ALL)
	for link,title in ALL :
            addDir(title,"http://www.ubu.com/film/"+link,1,count)
        
	
# Get all the videos on a page or links to pages of videos
def INDEX(url) :
        artist = url[url.rfind("/")+1:len(url)-5]
        print artist
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        link = response.read()
        link= link[:link.find("RESOURCES")]
        ALL=re.compile('src=\"../images/arrow_.*?.gif\".*?[\n| ]<a href=\"(.+?)\">(.+?)</a>').findall(link)
        count = len(ALL)
	for urllink,title in ALL :
                # Get rid of Bold tags
                if title[:3] == '<b>' :
                        title= title[4:len(title)-3]
                # Get rid of Emhasis tags
                if title[:4] == '<em>':
                        title= title[4:len(title)-5]
                # If we find a video file we add it as playable                        
		if urllink[len(urllink)-3:] == 'avi' or urllink[len(urllink)-3:] == 'mp4' or urllink[len(urllink)-3:] == 'mpg':
                    	addLink(title,urllink)
                elif urllink.find(artist+"_") <> -1 :
                        addDir(title,"http://www.ubu.com/film/"+urllink,2,count)

# Get all the videos on a page or links to pages of videos
def INDEX2(url) :
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        link = response.read()
        link= link[:link.find("RESOURCES")]
        ALL=re.compile('<a href=\"(.+?).(avi|mp4|mpg)\">(.+?)</a>').findall(link)
	for urllink,extension,title in ALL :
                # Get rid of Bold tags
                if title[:3] == '<b>':
                        title= title[3:len(title)-4]
                # Get rid of Emhasis tags
                if title[:4] == '<em>':
                        title= title[4:len(title)-5]
        	addLink(title,urllink+"."+extension)

                        
              
# Encapsulate data we need to send between different bits            
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
      
# Add a link to the video the final bit 
def addLink(name,url):
        print "Media = "+url
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage="DefaultVideo.png")
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz,totalItems=15)
        return ok


# Add a directory to the list         
def addDir(name,url,mode,total):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&page="+str(page)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name,iconImage="DefaultVideo.png", thumbnailImage="DefaultVideo.png")
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True,totalItems=total)
        return ok

      
params=get_params()
url=None
name=None
mode=None
thumbnailImage="DefaultVideo.png"
page=0
try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass
try :
        thumbnailImage = urllib.unquote_plus(params["thumbnailImage"])
except:
        pass
try :
        page=int(params["page"])
except:
        pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
print "Page: "+str(page)
if mode==None or url==None or len(url)<1:
        print "Artists"
        Artists()
elif mode==1:
        INDEX(url)
elif mode==2:
        INDEX2(url)



xbmcplugin.endOfDirectory(int(sys.argv[1]))
