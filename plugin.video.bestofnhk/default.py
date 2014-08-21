# Best of NHK - by misty 2013.
# import python libraries
import urllib
import urllib2
import re
import xbmcplugin
import xbmcgui
import xbmcaddon
import random
addon01 = xbmcaddon.Addon('plugin.video.bestofnhk')
addon_id = 'plugin.video.bestofnhk'
from t0mm0.common.addon import Addon
addon = Addon(addon_id, sys.argv)
from t0mm0.common.net import Net
net = Net()

# global variables
host = 'http://bestofnhk.tv/'
host2 = 'http://www3.nhk.or.jp/'
radio = 'rj/podcast/mp3/'
shows = 'http://bestofnhk.tv/shows/'
icon = addon01.getAddonInfo('icon') # icon.png in addon directory

# Main Menu
def CATEGORIES():
    media_item_list('NHK World Live Stream','rtmp://ca-1.srv.fivecool.net/nhkw/gwm')
    addDir('NHK Radio News', host2, 'audio', icon)
    addDir('Latest Shows', host, 'latest', icon)
    addDir('Shows by Name', host, 'by_name', icon)
    addDir('Random Show', host, 'by_random', icon)


# Create content list
def addDir(name,url,mode,iconimage):
     params = {'url':url, 'mode':mode, 'name':name}
     addon.add_directory(params, {'title': str(name)}, img = icon)


# Pre-recorded NHK World Radio in 17 languages
def IDX_RADIO(url):
    media_item_list('NHK Radio News in Arabic',host2+radio+'arabic.mp3')
    media_item_list('NHK Radio News in Bengali',host2+radio+'bengali.mp3')
    media_item_list('NHK Radio News in Burmese',host2+radio+'burmese.mp3')
    media_item_list('NHK Radio News in Chinese',host2+radio+'chinese.mp3')
    media_item_list('NHK Radio News in English',host2+radio+'english.mp3')
    media_item_list('NHK Radio News in French',host2+radio+'french.mp3')
    media_item_list('NHK Radio News in Hindi',host2+radio+'hindi.mp3')
    media_item_list('NHK Radio News in Indonesian',host2+radio+'indonesian.mp3')
    media_item_list('NHK Radio News in Korean',host2+radio+'korean.mp3')
    media_item_list('NHK Radio News in Persian',host2+radio+'persian.mp3')
    media_item_list('NHK Radio News in Portugese',host2+radio+'portugese.mp3')
    media_item_list('NHK Radio News in Russian',host2+radio+'russian.mp3')
    media_item_list('NHK Radio News in Spanish',host2+radio+'spanish.mp3')
    media_item_list('NHK Radio News in Swahili',host2+radio+'swahili.mp3')
    media_item_list('NHK Radio News in Thai',host2+radio+'thai.mp3')
    media_item_list('NHK Radio News in Urdu',host2+radio+'urdu.mp3')
    media_item_list('NHK Radio News in Vietnamese',host2+radio+'vietnamese.mp3')

	 
# Simple website scrape for content list
def IDX_LATEST_SHOWS(url):
    link = net.http_GET(url).content
    match=re.compile('<option value="(.+?).flv" >(.+?)&nbsp;&nbsp;&nbsp;(.+?)</option>').findall(link)
    for url,date,name in match:
        media_item_list(url.encode('UTF-8'),shows+url+'.flv')


# Simple website scrape for content list
def IDX_SHOWS_BY_NAME(url):
    link = net.http_GET(url).content
    match=re.compile('<option value="(.+?).flv" >(.+?)&nbsp;&nbsp;&nbsp;(.+?)</option>').findall(link)
    match.sort()
    for url,name,date in match:
        media_item_list(url.encode('UTF-8'),shows+url+'.flv')


# Play a random video
def IDX_RANDOM_SHOW(url):
    link = net.http_GET(host).content
    match=re.compile('<option value="(.+?).flv" >(.+?)&nbsp;&nbsp;&nbsp;(.+?)</option>').findall(link)
    rnd_match = random.choice(match)
    for url in rnd_match:
        addon.add_video_item({'url': shows+url+'.flv'}, {'title': url}, img = icon, playlist=False)
        addon.resolve_url(url.encode('UTF-8'))
        addon.end_of_directory()

        
# Create media items list
def media_item_list(name,url):
    if mode=='audio':
        addon.add_music_item({'url': url}, {'title': name}, context_replace = icon, playlist=False)
    elif mode!='audio':    
        addon.add_video_item({'url': url}, {'title': name}, img = icon, playlist=False)

# Query play, mode, url and name
play = addon.queries.get('play', None)
mode = addon.queries['mode']
url = addon.queries.get('url', '')
name = addon.queries.get('name', '')

print "Play: " +str(play)
print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)


# Program flow control
if play:
    addon.resolve_url(url.encode('UTF-8')) # <<< Play resolved media url

if mode=='main':
    print ""
    CATEGORIES()

elif mode=='audio':
    print ""+url
    IDX_RADIO(url)

elif mode=='latest':
    print ""+url
    IDX_LATEST_SHOWS(url)

elif mode=='by_name':
    print ""+url
    IDX_SHOWS_BY_NAME(url)
    
elif mode=='by_random':
    print ""+url
    IDX_RANDOM_SHOW(url)    

if not play:
    addon.end_of_directory()
