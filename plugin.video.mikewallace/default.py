import xbmcplugin, xbmcgui 
import re, urllib2, sys

def add_video(name,url,thumbnail,genre):
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=thumbnail)
    liz.setInfo( type="Video", infoLabels={ "Title": name, "Genre": str(genre) } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=sys.argv[0]+'?'+url,listitem=liz)
    return ok

def display_videos():
    rehref=re.compile('img src\=\'(.+)\'.+?<strong><a href\="(\/tmwi\/index.php\/.+?)" title\="(.+?)"')
    url="http://solstice.ischool.utexas.edu/tmwi/index.php/The_Mike_Wallace_Interview"
    base_url="http://solstice.ischool.utexas.edu"
    lines=urllib2.urlopen(url).readlines()
    genre=1
    for line in lines:
        match=rehref.search(line)
        if match:
            add_video(match.group(3), base_url+match.group(2), base_url+match.group(1), genre)
            genre+=1
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_GENRE)

def play_video(url):
    resvideo=re.compile('svideo1.addVariable\("id","(.+?)"\)')
    lines=urllib2.urlopen(url).readlines()
    playpath=""
    for line in lines:
        match=resvideo.search(line)
        if match:
            playpath=match.group(1)
    url='rtmp://aveo.ischool.utexas.edu/vod/'
    swfUrl="http://solstice.ischool.utexas.edu/tmwi/extensions/player/flvplayer.swf"
    liz=xbmcgui.ListItem("Mike Wallace Interview", iconImage="DefaultVideo.png")
    liz.setProperty("SWFPlayer", swfUrl)
    liz.setProperty("PlayPath", playpath)
    xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(url, liz)

script=sys.argv[0]
url=""
if sys.argv[2]:
    url=sys.argv[2][1:]
if not url:
    display_videos()
else:
    play_video(url)
xbmcplugin.endOfDirectory(int(sys.argv[1]))
