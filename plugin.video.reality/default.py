# -*- coding: utf-8 -*-

import urllib,urllib2,re,xbmcplugin,xbmcgui,string,gzip,os,xbmcaddon
from BeautifulSoup import BeautifulSoup
from cStringIO import StringIO
#import elementtree.ElementTree as etree



def CLEAN(string):
    def substitute_entity(match):
        ent = match.group(3)
        if match.group(1) == "#":
            if match.group(2) == '':
                return unichr(int(ent))
            elif match.group(2) == 'x':
                return unichr(int('0x'+ent, 16))
        else:
            cp = n2cp.get(ent)
            if cp: return unichr(cp)
            else: return match.group()
    entity_re = re.compile(r'&(#?)(x?)(\w+);')
    return entity_re.subn(substitute_entity, string)[0]

def AID(name):
    local=xbmcaddon.Addon(id='plugin.video.reality')
    allAnimeXML = etree.parse(open("%s/titles.xml"%local.getAddonInfo('path')))
    reg = re.compile('( \(\d{4}\))|[%s]' % re.escape(string.punctuation)) 
    name = reg.sub('', name.lower())
    lastAid = 0
    for Element in allAnimeXML.getiterator():
        if Element.get("aid", False):
            lastAid = int(Element.get("aid"))
        if Element.text:
            testname = reg.sub('', Element.text.lower())
            if testname == name:
                return str(lastAid)
    return 0

def ADB(name):
    anime = AID(name.replace('Ō','oo').replace('-','').replace('ō','ou'))
    xbmc.log('http://anidb.net/perl-bin/animedb.pl?show=anime&aid=%s'%anime)
    txheaders= {'User-Agent': 'Mozilla/6.0 (Macintosh; I; Intel Mac OS X 11_7_9; de-LI; rv:1.9b4) Gecko/2012010317 Firefox/10.0a4'}
    req = urllib2.Request('http://anidb.net/perl-bin/animedb.pl?show=anime&aid=%s'%anime,None,txheaders)
    data=BeautifulSoup(gzip.GzipFile(fileobj=StringIO(urllib2.urlopen(req).read())).read())
    iconimage=data.img.attrs[0][1]
    infoLabels={}
    infoLabels['title']=name
    infoLabels['plot']=re.sub('http://anidb.net/c.+?">','',re.compile('<a href="(.+?)</div>',re.DOTALL).findall(str(data.findAll('div',attrs="g_bubble desc")))[0].replace('\n','').replace('<a href="','').replace('</a>','').replace('\t',''))
    try:infoLabels['votes']=float(re.compile(r'rating tmpanime mid"><a href=".+?">(.+?)</a>',re.DOTALL).findall(str(data))[0])
    except:infoLabels['votes']=float(re.compile(r'rating tmpanime high"><a href=".+?">(.+?)</a>',re.DOTALL).findall(str(data))[0])
    try:infoLabels['genre']=str(re.compile('title="search for other anime with this category">(.+?)</a>').findall(str(data))).replace("'",'').replace('[','').replace(']','')
    except:pass
    try:infoLabels['director']=re.compile('Direction:</a>\n</td>\n<td class="creator"><a href=".+?">(.+?)</a>',re.DOTALL).findall(str(data))[0]
    except:pass
    infoLabels['country']='Japan'
    try:infoLabels['cast']=re.compile('voiced by:</strong> <a class=".+?" title=".+?" href=".+?">(.+?)</a>').findall(str(data))
    except:pass
    try:infoLabels['episode']=int(re.compile('<td class="value">.+?,(.+?)episodes</td>',re.DOTALL).findall(str(data))[0])
    except:pass
    try:infoLabels['writer']=re.compile('Original Work:</a>\n</td>\n<td class="creator"><a href=".+?">(.+?)</a>',re.DOTALL).findall(str(data))[0]
    except:pass
    try:infoLabels['artist']=re.compile('Music:</a>\n</td>\n<td class="creator"><a href=".+?">(.+?)</a>',re.DOTALL).findall(str(data))[0]
    except:pass
    return infoLabels


def CATS():
        addDir('ANIME FULL (800+)','http://www.realitylapse.com/pages/selectvideos.php',2,'','')
        addDir('ANIME A-Z','http://www.realitylapse.com/pages/selectvideos.php',1,'','')
                
def AZ():
        addDir('#','http://www.realitylapse.com/anime/etc.php',2,'','')
        for i in string.ascii_uppercase:
                addDir(i,'http://www.realitylapse.com/anime/%s.php'%i,2,'','')
        
def ANIME(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6')
        data = re.compile(r'<a href="(.+?)">(.+?)<span class="count"> ?(.+?)?</span>').findall(urllib2.urlopen(req).read().replace('&#333;','ou'))
        if data:
                for curl,name,eps in data:
                        addDir(name,'http://www.realitylapse.com%s'%curl,3,'','')
        else:
                data=re.compile('<li><a href="(.+?)">(.+?)</a></li>').findall(urllib2.urlopen(req).read().replace('&#333;','ou'));del data[0];del data[-9:]
                for curl,name in data:
                        addDir(name,'http://www.realitylapse.com%s'%curl,3,'','')

def INDEX(name,url):
    i=0
    #infoLabels=ADB(name)
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6')
    soup=BeautifulSoup(urllib2.urlopen(req).read())
    data=re.compile('href="/downloads/default(.+?)"').findall(str(soup.findAll('a','mousey')))
    desc=re.compile('span id="animeDescription" style=".+?#FFF">(.+?)<a',re.DOTALL).findall(urllib2.urlopen(req).read())[0]
    for url in data:
        i=i+1
        addDir("%s - Episode %s"%(name,str(i)),'http://www.realitylapse.com/downloads/default%s'%url,4,'',CLEAN(desc))
            

def LINKS(name,url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6')
        data = re.compile(r'downloads =.+?"http:\\/\\/.+?realitylapse.com\\/dl\\(.+?)"').findall(urllib2.urlopen(req).read())
        link=data[0].replace('\\','')
        if link:
                servers=[('2. Silicon - FAST','http://silicon.realitylapse.com/dl%s'%link),
                ('4. Promethium - MEDIUM','http://promethium.realitylapse.com/dl%s'%link),
                ('1. Cerium - FASTEST','http://cerium.realitylapse.com/dl%s'%link),
                ('5. Lithium - SLOW','http://lithium.realitylapse.com/dl%s'%link),
                ('3. Tungsten - MEDIUM','http://tungsten.realitylapse.com/dl%s'%link),
                ('6. Titanium - MEDIUM','http://titanium.realitylapse.com/dl%s'%link)]
                for server,url in servers:
                        addLink('%s - %s'%(server,name),url,'')                      
        
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

def addLink(name,url,thumbnail):
        ok=True
        liz=xbmcgui.ListItem(label=name,iconImage="DefaultVideo.png",thumbnailImage=thumbnail)
        liz.setInfo( type="Video", infoLabels={ "Title": name  } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
        return ok

def addDir(name,url,mode,iconimage,desc):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title" : name , "Plot" : desc } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
        return ok

def vaddDir(name,url,mode,iconimage,infoLabels):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels=infoLabels );ok=True
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
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
        CATS()
elif mode==1:
        AZ()
elif mode==2:
        ANIME(url)
elif mode==3:
        INDEX(name,url)
elif mode==4:
        LINKS(name,url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
