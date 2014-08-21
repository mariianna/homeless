import urllib,urllib2,re,xbmcplugin,xbmcgui

def CATEGORIES():
        addDir('Front Page','http://thesciencenetwork.org/',3,'')
        addDir('Meetings','http://thesciencenetwork.org/section/meetings.rss',4,'')
        addDir('Series','http://thesciencenetwork.org/section/series.rss',4,'')
        addDir('Et Cetera','http://thesciencenetwork.org/section/et-cetera.rss',4,'')
        addDir('Topics','http://thesciencenetwork.org/search?q=&',5,'')
        addDir('Speakers','http://thesciencenetwork.org/search?q=&',6,'')

def LISTTOPICS(url): #Mode 5, Read search list for topics
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        link2 = link.replace('[','').replace(']','').replace('!','')
        match=re.compile('<a href="/search\?q\=\&topics=(.+?)">(.+?)</a>',re.DOTALL).findall(link2)
        for topicstr,title in match:
         addDir(title,'http://thesciencenetwork.org/search.rss?q=&topics=' + topicstr + '&page=1',1,'')

def LISTSPEAKERS(url): #Mode 6, read search list for speakers
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        link2 = link.replace('[','').replace(']','').replace('!','')
        match=re.compile('<a href="/search\?q\=\&speakers=(.+?)">(.+?)</a>',re.DOTALL).findall(link2)
        for spkstr,title in match:
         addDir(title,'http://thesciencenetwork.org/search.rss?q=&speakers=' + spkstr + '&page=1',1,'')

def LISTCATS(url): #Mode 4, Read rss for categories, works on series/meeting pages
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        link2 = link.replace('[','').replace(']','').replace('!','')
        match=re.compile('<title><CDATA(.+?)></title>(.+?)<link>(.+?)</link>(.+?)src="(.+?)"',re.DOTALL).findall(link2)
        for title,fill,url2,fill2,thumbnail in match:
         thumbnail2 = 'http://thesciencenetwork.org/' + thumbnail
         addDir(title.replace('&amp;','&'),url2 + '.rss',1,thumbnail2)

def LISTFEEDS(url): #Mode 3, Read page for rss feeds, works on front page
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        match=re.compile('<div class="hrline">&nbsp;</div><h1><a href="(.+?)">(.+?)<(.+?)<a href="(.+?).rss">').findall(link)
        for fill1,title,fill2,link in match:
         addDir(title.replace('&amp;','&'),link + '.rss',1,'')

def INDEX(url): #Mode 1, Read rss for videos
        req = urllib2.Request(url)
        print "indexurl=" + url
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        link2 = link.replace('[','').replace(']','').replace('!','')
        match=re.compile('<title><CDATA(.+?)></title>(.+?)<link>(.+?)</link>(.+?)src="(.+?)"',re.DOTALL).findall(link2)
        i = 0
        for title,fill,url2,fill2,thumbnail in match:
         i = i + 1
         thumbnail2 = 'http://thesciencenetwork.org/' + thumbnail
         addDir(title,url2,2,thumbnail2)
        #continue searching for multiple pages
        if url.find('search.rss')>1:
          if i > 1:
            curPage = url[((len(url) - url.rfind('='))-1) * -1:]
            searchstr = url[:(len(url) - (len(url) - url.rfind('=')))] + '='
            addDir('Page ' + str(int(curPage) + 1),searchstr + str(int(curPage) + 1),1,'')
          else:
            addDir('No more results found','','','')

def VIDEOLINKS(url,name): #Mode 2, Read video page for download link
         req = urllib2.Request(url)
         req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
         response = urllib2.urlopen(req)
         link=response.read()
         response.close()
         match=re.compile('<li class="download"><a href="(.+?)">Download').findall(link)
         for url in match:
              addLink(name,url,'')

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


def addLink(name,url,iconimage):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.setProperty("IsPlayable","true");
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
        
              
params=get_params()
url=None
name=None
mode=None

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

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)

if mode==None or url==None or len(url)<1:
        CATEGORIES()       
elif mode==1:
        INDEX(url)
elif mode==2:
        VIDEOLINKS(url,name)
elif mode==3:
        LISTFEEDS(url)
elif mode==4:
        LISTCATS(url)
elif mode==5:
        LISTTOPICS(url)
elif mode==6:
        LISTSPEAKERS(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
