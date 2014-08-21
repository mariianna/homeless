# -*- coding: utf-8 -*-
import xbmcaddon,xbmcplugin,xbmcgui,sys,urllib
import os,re,urllib2
import xml.etree.ElementTree as etree 



pluginhandle = int(sys.argv[1])
addon = xbmcaddon.Addon(id='plugin.audio.plexmusic')
home = addon.getAddonInfo('path').decode('utf-8')
image = xbmc.translatePath(os.path.join(home, 'logo.png'))
fanartaddon= xbmc.translatePath(os.path.join(home, 'fanart.jpg'))
view_id='506'


IP=addon.getSetting('ipaddress')
PORT='32400'
Server='http://%s:%s' % (IP,PORT)
music='/library/sections/1/all'


def main():
    fanart= xbmc.translatePath(os.path.join(home, 'fanart.jpg'))
    addDir('Search Artist',fanart,'',"ArtistSearch",image)
    addDir('Search Album',fanart,'',"AlbumSearch",image)
    addDir('Search Song',fanart,'',"SongSearch",image)
    url='%s%s' % (Server,music)
    html=getURL(url)
    tree = etree.fromstring(html).getiterator("Directory")
    for entry in tree:
      url=Server+(entry.get('key')).encode('utf-8')
      name=entry.get('title').encode('utf-8')
      try:
        iconimage=Server+(entry.get('thumb')+'.jpg').encode('utf-8')
      except:
        iconimage=image
      try:
        fanart=Server+(entry.get('art')+'.jpg').encode('utf-8')
      except:
        fanart=fanartaddon
      addDir(name,fanart,url,"Album",iconimage)
      

def Album(fanart,url):
     html=getURL(url)
     tree = etree.fromstring(html).getiterator("Directory")
     for entry in tree:
       name=entry.get('title').encode('utf-8')
       url=Server+(entry.get('key')).encode('utf-8')
       try:
         iconimage=Server+(entry.get('thumb')+'.jpg').encode('utf-8')
       except:
         iconimage=image
       addDir(name,fanart,url,"Songs",iconimage)
       


def Songs(fanart,iconimage,url):
    html=getURL(url)
    tree = etree.fromstring(html).getiterator("MediaContainer")[0]
    artist=tree.get('grandparentTitle')
    album=tree.get('parentTitle')
    date=tree.get('parentYear')
    tree = etree.fromstring(html).getiterator("Track")
    for entry in tree:
      name=entry.get('title').encode('utf-8')
      tracknumber=entry.get('index')
      #print 'ffffffffffffffffffffffffffffffffff'+number
      media=entry.getiterator("Media")[0]
      data=entry.getiterator("Part")[0]
      url=Server+(data.get('key'))
      addLink(name,fanart,artist,album,tracknumber,url,"play",iconimage,date)

def play(url):
        listitem = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def getURL(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:16.0) Gecko/20100101 Firefox/16.0')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link
       
def ArtistSearch():
        search_entered =search()
        url='%s/library/sections/1/all?type=8&title=%s&X-Plex-Container-Start=0' % (Server,search_entered)
        html=getURL(url)
        tree = etree.fromstring(html).getiterator("Directory")
        for entry in tree:
          url=Server+(entry.get('key')).encode('utf-8')
          name=entry.get('title').encode('utf-8')
          desc=entry.get('summary').encode('utf-8')
          try:
            iconimage=Server+(entry.get('thumb')+'.jpg').encode('utf-8')
          except:
            iconimage=image
          try:
            fanart=Server+(entry.get('art')+'.jpg').encode('utf-8')
          except:
            fanart=fanartaddon
          addDir(name,fanart,url,"Album",iconimage)
          
        
def AlbumSearch():
       search_entered =search()
       url='%s/library/sections/1/all?type=9&title=%s&X-Plex-Container-Start=0' % (Server,search_entered)
       html=getURL(url)
       tree = etree.fromstring(html).getiterator("Directory")
       for entry in tree:
         url=Server+(entry.get('key')).encode('utf-8')
         name=entry.get('title').encode('utf-8')
         try:
           iconimage=Server+(entry.get('thumb')+'.jpg').encode('utf-8')
         except:
           iconimage=image
         year=entry.get('year')
         fanart= xbmc.translatePath(os.path.join(home, 'fanart.jpg'))
         addDir(name,fanart,url,"Songs",iconimage)
         
def SongSearch():
       search_entered =search()
       url='%s/search?type=10&query=%s' % (Server,search_entered)
       html=getURL(url)
       tree = etree.fromstring(html).getiterator("Track")
       for entry in tree:
         url=Server+(entry.get('key')).encode('utf-8')
         name=entry.get('title').encode('utf-8')
         artist=entry.get('grandparentTitle').encode('utf-8')
         album=entry.get('parentTitle')
         try:
           iconimage=Server+(entry.get('thumb')+'.jpg').encode('utf-8')
         except:
           iconimage=image
         try:
           fanart=Server+(entry.get('art')+'.jpg').encode('utf-8')
         except:
           fanart=fanartaddon
         addLink(name,fanart,artist,album,'',url,"play1",iconimage,'')

def play1(url):
        html=getURL(url)
        tree = etree.fromstring(html).getiterator("Part")[0]
        url=Server+(tree.get('key'))
        listitem = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
        
        
def search():
        search_entered = ''
        keyboard = xbmc.Keyboard(search_entered, 'Search on Plex-Music')
        keyboard.doModal()
        if keyboard.isConfirmed():
            search_entered = keyboard.getText()
            if search_entered == None:
                return False          
        return search_entered	


def addLink(name,fanart,artist,album,tracknumber,url,mode,iconimage,date):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&iconimage="+urllib.quote_plus(iconimage)+"&fanart="+urllib.quote_plus(fanart)
        ok=True
        liz=xbmcgui.ListItem(name,iconImage=iconimage,thumbnailImage=iconimage)
        liz.setInfo( type="music", infoLabels={ "Artist": artist, "Title": name, "Album": album, "tracknumber": tracknumber, "Year": date })
        liz.setProperty('IsPlayable', 'true')
        liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok
 
def addDir(name,fanart,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&fanart="+urllib.quote_plus(fanart)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
    
def parameters_string_to_dict(parameters):
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
fanart=params.get('fanart')
iconimage=params.get('iconimage')
if type(url)==type(str()):
  url=urllib.unquote_plus(url)
if type(name)==type(str()):
  name=urllib.unquote_plus(name)
if type(fanart)==type(str()):
  fanart=urllib.unquote_plus(fanart)
if type(iconimage)==type(str()):
  iconimage=urllib.unquote_plus(iconimage)


if  mode == "Album":
    Album(fanart,url)
elif  mode == "Songs": 
    Songs(fanart,iconimage,url)
elif  mode == "ArtistSearch":
    ArtistSearch()
elif  mode == "AlbumSearch":
    AlbumSearch()
elif  mode == "SongSearch":
    SongSearch()
elif  mode == 'play':
    play(url)
elif  mode == 'play1':
    play1(url)
else:
  main()

xbmcplugin.endOfDirectory(pluginhandle)
xbmc.executebuiltin("Container.SetViewMode(%s)" % view_id)
