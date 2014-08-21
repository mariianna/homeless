#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmcplugin,xbmcgui,sys,xbmcaddon,requests,re,urlparse,os
from urllib import quote, unquote_plus, unquote, urlencode,quote_plus,urlretrieve

pluginhandle = int(sys.argv[1])
addon = xbmcaddon.Addon(id='plugin.video.youtubesearch')
home = addon.getAddonInfo('path').decode('utf-8')
imageDir = os.path.join(home, 'thumbnails') + '/'
fanart=imageDir+"fanart.jpg"

def categorie():
	addDir('Search Video','','video','')
	addDir('Search Playlist','','playlist','')
	addDir('Search Artist Album','','album','')
	xbmcplugin.endOfDirectory(pluginhandle)
	 


def SearchVideo():
    search_entered =search()
    url='http://gdata.youtube.com/feeds/api/videos?v=2&alt=json&q=%s' % search_entered
    data=requests.get(url).json()['feed']['entry']
    for entry in data:
      name=entry['title']['$t']
      url=entry['link'][0]['href'].replace('&feature=youtube_gdata', '')
      desc=entry['media$group']['media$description']['$t']
      thumbnail=entry['media$group']['media$thumbnail'][0]['url']
      addLink(name,url,"play",thumbnail,desc)
              
def SearchPlaylist():
	search_entered =search()
	url='http://gdata.youtube.com/feeds/api/playlists/snippets?q=%s&v=2&alt=json' % search_entered
	data=requests.get(url).json()['feed']['entry'] 
	for entry in data:
		name= entry['title']['$t'].encode('utf-8')
		url= entry['content']['src']+'&alt=json'
		iconimage= entry['media$group']['media$thumbnail'][1]['url']
		desc=entry['summary']['$t'].encode('utf-8')
		addDir(name,url,"playlistvideo",iconimage)
		
def playlistvideo(url):
	data=requests.get(url).json()['feed']['entry']
	for entry in data:
		 name= entry['title']['$t'].encode('utf-8')
		 try:
			 url= entry['media$group']['media$player']['url'].replace('&feature=youtube_gdata_player','')
		 except:
			 url=entry['link'][0]['href'].replace('&feature=youtube_gdata', '')
		 try:
		     iconimage=entry['media$group']['media$thumbnail'][1]['url']
		 except:
			 iconimage=''
		 try:
		   desc=entry['media$group']['media$description']['$t'].encode('utf-8')
		 except:
		   desc=''
		 addLink(name,url,"play",iconimage,desc)
		 
def album():
	search_entered =search()
	temp=search_entered.split('&')
	artist=temp[0]
	album=temp[1]
	url='http://pipes.yahoo.com/pipes/pipe.run?Album=%s&Artist=%s&_id=9f94cefec4ed486f173f0cfe88562cee&_render=json' % (album,artist)
	data=requests.get(url).json()['value']['items']
	for entry in data:
		name= entry['title']
		url= entry['link']
		iconimage= entry['media:thumbnail']['url']
		url=re.sub('&feature=youtube_gdata','',url)
		addLink(name,url,'play',iconimage,'')
		            
              
def search():
        search_entered = ''
        keyboard = xbmc.Keyboard(search_entered, 'YouTube Search')
        keyboard.doModal()
        if keyboard.isConfirmed():
            search_entered = keyboard.getText() .replace(' ','+')  # sometimes you need to replace spaces with + or %20
            if search_entered == None:
                return False          
        return search_entered

def addLink(name,url,mode,iconimage,desc):
        u=sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name , "Plot": desc } )
        liz.setProperty('IsPlayable', 'true')
        liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok


def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)+"&name="+quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def play(url, videoPrio=0):
		# this part is from mtube plugin
		video_id = urlparse.parse_qs(urlparse.urlparse(url).query)['v'][0]
		print "got url:", url
		if videoPrio == 0:
			VIDEO_FMT_PRIORITY_MAP = {'22' : 4,'35' : 2,'18' : 1,'34' : 3}
		elif videoPrio == 1:
			VIDEO_FMT_PRIORITY_MAP = {'22' : 1,'35' : 3,'18' : 2,'34' : 4}
		else:
			VIDEO_FMT_PRIORITY_MAP = {'22' : 2,'35' : 5,'18' : 4,'34' : 6,}
		video_url = None
		watch_url = 'http://www.youtube.com/watch?v=%s&gl=US&hl=en' % video_id
		watchvideopage = requests.get(watch_url).content
		for el in ['&el=embedded', '&el=detailpage', '&el=vevo', '']:
			info_url = ('http://www.youtube.com/get_video_info?&video_id=%s%s&ps=default&eurl=&gl=US&hl=en' % (video_id, el))
			infopage = requests.get(info_url).content
			videoinfo = urlparse.parse_qs(infopage)
			if ('url_encoded_fmt_stream_map' or 'fmt_url_map') in videoinfo:
				break
		if ('url_encoded_fmt_stream_map' or 'fmt_url_map') not in videoinfo:
			if 'reason' not in videoinfo:
				error = 'Error: unable to extract fmt_url_map or url_encoded_fmt_stream_map parameter for unknown reason'
				print error
			else:
				reason = unquote_plus(videoinfo['reason'][0])
				error= 'YouTube said:'+reason.decode('utf-8')
				xbmc.executebuiltin('XBMC.Notification(%s)'% error)
				
				print error
			return "False"
		video_fmt_map = {}
		fmt_infomap = {}
		if videoinfo.has_key('url_encoded_fmt_stream_map'):
			tmp_fmtUrlDATA = videoinfo['url_encoded_fmt_stream_map'][0].split(',')
		else:
			tmp_fmtUrlDATA = videoinfo['fmt_url_map'][0].split(',')
		for fmtstring in tmp_fmtUrlDATA:
			fmturl = fmtid = fmtsig = ""
			if videoinfo.has_key('url_encoded_fmt_stream_map'):
				try:
					for arg in fmtstring.split('&'):
						if arg.find('=') >= 0:
							#print arg.split('=')
							key, value = arg.split('=')
							if key == 'itag':
								if len(value) > 3:
									value = value[:2]
								fmtid = value
                                                               # print fmtid
							elif key == 'url':
								fmturl = value
                                                               # print fmturl
							elif key == 'sig':
								fmtsig = value
                                                                #print fmtsig
					        if fmtid != "" and fmturl != "" and fmtsig != ""  and VIDEO_FMT_PRIORITY_MAP.has_key(fmtid):
						  video_fmt_map[VIDEO_FMT_PRIORITY_MAP[fmtid]] = { 'fmtid': fmtid, 'fmturl': unquote_plus(fmturl), 'fmtsig': fmtsig }
						  fmt_infomap[int(fmtid)] = "%s&signature=%s" %(unquote_plus(fmturl), fmtsig)
                                                 # print fmt_infomap[int(fmtid)]
					          fmturl = fmtid = fmtsig = ""
                                        
				except:
					error = "error parsing fmtstring: %s" % fmtstring
					print error
			else:
				(fmtid,fmturl) = fmtstring.split('|')
			if VIDEO_FMT_PRIORITY_MAP.has_key(fmtid) and fmtid != "":
				video_fmt_map[VIDEO_FMT_PRIORITY_MAP[fmtid]] = { 'fmtid': fmtid, 'fmturl': unquote_plus(fmturl) }
				fmt_infomap[int(fmtid)] = unquote_plus(fmturl)
		#print "[youtubeUrl] got",sorted(fmt_infomap.iterkeys())
		if video_fmt_map and len(video_fmt_map):
			#print "[youtubeUrl] found best available video format:",video_fmt_map[sorted(video_fmt_map.iterkeys())[0]]['fmtid']
			best_video = video_fmt_map[sorted(video_fmt_map.iterkeys())[0]]
                        video_url=best_video['fmturl']
			listitem = xbmcgui.ListItem(path=video_url)
			xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
        


  
 
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

if mode == 'video':
	SearchVideo()
elif mode =='album':
	album()
	
elif mode == 'playlist':
	SearchPlaylist()
elif mode == 'playlistvideo':
	playlistvideo(url)	

elif mode == 'play':
    play(url, videoPrio=0)

else:
    categorie()

xbmcplugin.endOfDirectory(pluginhandle)   
