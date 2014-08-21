
__scriptname__ = "NBA.com Videos"
__author__ = 'stacked [http://xbmc.org/forum/member.php?u=26908]'
__svn_url__ = "https://xbmc-addons.googlecode.com/svn/trunk/plugins/video/NBA.com%20Videos"
__date__ = '03-01-2010'
__version__ = "1.0.6"

import xbmc, xbmcgui, xbmcplugin, urllib2, urllib, re, string, sys, os, traceback
HEADER = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.7) Gecko/20091221 Firefox/3.5.7'
THUMBNAIL_PATH = os.path.join(os.getcwd().replace( ";", "" ),'resources','media')

def open_url(url):
	req = urllib2.Request(url)
	req.add_header('User-Agent', HEADER)
	content=urllib2.urlopen(req)
	data=content.read()
	content.close()
	return data


class UserCancelException(Exception):
	pass


def _check_for_update():
	print "NBA.com Videos"+__version__
	url = 'http://code.google.com/p/xbmc-addons/source/browse/trunk/plugins/video/NBA.com%20Videos/default.py'
	req = urllib2.Request(url)
	req.add_header('User-Agent', HEADER)
	f=urllib2.urlopen(req)
	a=f.read()
	f.close()
	ALL = re.compile('<td class="source">__version__ = &quot;(.+?)&quot;<br></td>').findall(a)
	for link in ALL :
		if link.find(__version__) != 0:
			newVersion=link
			dia = xbmcgui.Dialog()
			ok = dia.ok("NBA.com Videos", 'Updates are available on both SVN Repo or XBMC Zone\n\n'+'Current Version: '+__version__+'\n'+'Update Version: '+newVersion)

def showRoot():
	data=[
			('All Videos','channels%2F*|games%2F*|flip_video_diaries',''),
			('Highlights','games%2F*',''),
			('Top Plays','channels%2Ftop_plays',''),
			('Editor\'s Picks','','&editor_pick=yes'),
			('NBA TV','channels%2Fnba_tv',''),
			('TNT OT','channels%2Ftnt_overtime',''),
			('Barkley Zone','channels%2Fbarkley_zone','')
			]
	count=1
	for name,section,extra in data:
		item=xbmcgui.ListItem(str(count)+'. '+name)
		if 'Editor\'s Picks' == name:
			url='http://searchapp.nba.com/nba-search/query.jsp?type=advvideo&season=0910'+extra+'&npp=15'	
		else:
			url='http://searchapp.nba.com/nba-search/query.jsp?type=advvideo&section='+section+'&season=0910'+extra+'&npp=15'
		u=sys.argv[0]+"?mode=1&url="+urllib.quote_plus(url)+"&cat="+urllib.quote_plus(name)+"&save="+urllib.quote_plus(url)
		xbmcplugin.addDirectoryItem(int(sys.argv[1]),u,item,True)
		count=count+1
	item=xbmcgui.ListItem(str(count)+'. Featured')
	u=sys.argv[0]+"?mode=2&url="+urllib.quote_plus(url)+"&cat="+urllib.quote_plus('Featured')+"&save="+urllib.quote_plus(url)
	xbmcplugin.addDirectoryItem(int(sys.argv[1]),u,item,True)
	item=xbmcgui.ListItem(str(count+1)+'. Teams')
	u=sys.argv[0]+"?mode=5&url="+urllib.quote_plus(url)+"&cat="+urllib.quote_plus('Teams')+"&save="+urllib.quote_plus(url)
	xbmcplugin.addDirectoryItem(int(sys.argv[1]),u,item,True)

def get_data(url,page,cat,save):
	saveurl=url
	url=url+'&start='+str(1+(15*(page-1)))
	print url
	data=[
			('Most Recent','recent'),
			('Most Watched','view'),
			('Most Commented','comment'),
			('Highest Rated','rating')
			]
	for name,sort in data:
		item=xbmcgui.ListItem(name)
		urlsort=save+'&sort='+sort+'&start=5'
		u=sys.argv[0]+"?mode=1&url="+urllib.quote_plus(urlsort)+"&cat="+urllib.quote_plus(cat+' / '+name)+"&save="+urllib.quote_plus(save)
		xbmcplugin.addDirectoryItem(int(sys.argv[1]),u,item,True)
	data=open_url(url)
	link=re.compile(',"url":"(.+?)","alt_url"').findall(data)
	titles=re.compile('"title":"(.+?)"').findall(data)
	thumb=re.compile('"thumbnail":{"url":"(.+?)"').findall(data)
	info=re.compile('"excerpt":"(.*?)"}}}').findall(data)
	count=0
	for title in titles:
		if len(info[count]) == 0:
			plot=''
		else:
			plot=' - '+info[count]
		url='http://nba.com'+link[count].replace('/index.html','')+'.xml'
		item=xbmcgui.ListItem(str(count+1+((page-1)*15))+'. '+title+plot, iconImage=thumb[count], thumbnailImage=thumb[count])
		item.setInfo( type="Video", infoLabels={ "Title": title, "Plot": info[count] } )
		u=sys.argv[0]+"?mode=3&url="+urllib.quote_plus(url)+"&name="+urllib.quote_plus(title)
		xbmcplugin.addDirectoryItem(int(sys.argv[1]),u,item)
		count=count+1
	item=xbmcgui.ListItem("Next Page",iconImage="DefaultVideo.png", thumbnailImage=os.path.join(THUMBNAIL_PATH, 'next.png'))
	u=sys.argv[0]+"?mode=1&url="+urllib.quote_plus(saveurl)+"&page="+str(int(page)+1)+"&cat="+urllib.quote_plus(cat)+"&save="+urllib.quote_plus(save)
	xbmcplugin.addDirectoryItem(int(sys.argv[1]),u,item,True)

def get_video_info(url,page,name):
	data=open_url(url)
	title=re.compile('<headline>(<!\[CDATA\[)?(.*?)(\]\]>)?</headline>').findall(data)
	plot=re.compile('<description>(<!\[CDATA\[)?(.*?)(\]\]>)?</description>').findall(data)
	url=re.compile('<file(.*?)type="large"(.*?)>(.+?)</file>').findall(data)
	length=re.compile('<length(.*?)>((.+?)</length>)?').findall(data)
	section=re.compile('<sectionName(.*?)>(.+?)</sectionName>', re.DOTALL).findall(data)
	try:
		playVideo('http://nba.cdn.turner.com/nba/big'+url[0][2], title[0][1], plot[0][1], section[0][1].capitalize())
	except UserCancelException:
		pass
		
def get_feature(url,page,cat):
	data=[
			('Award Nominees','channels%2Faward_nominees'),
			('Play of the Day','channels%2Fplay_of_the_day'),
			('Flip Diaries','flip_video_diaries'),
			('Originals','channels%2Foriginals')
			]
	count=1
	for name,section in data:
		item=xbmcgui.ListItem(str(count)+'. '+name)
		url='http://searchapp.nba.com/nba-search/query.jsp?type=advvideo&section='+section+'&season=0910&npp=15'
		u=sys.argv[0]+"?mode=1&url="+urllib.quote_plus(url)+"&cat="+urllib.quote_plus(name)+"&save="+urllib.quote_plus(url)
		xbmcplugin.addDirectoryItem(int(sys.argv[1]),u,item,True)
		count=count+1

def showTeams(url,page,cat,save):
	nick=url
	team=cat
	data=[
			('All Videos','teams%2F'+nick+'%7Cgames%2F*%7Cchannels%2F*','','&team='+team.replace(' ','%20')),
			('Team Originals','teams%2F'+nick,'&team_category=Team%20Originals',''),
			('Team Highlights','games%2F*%7Cchannels%2F*','','&team='+team.replace(' ','%20'))
			]
	for name,section,category,extra in data:
		item=xbmcgui.ListItem(name)
		url='http://searchapp.nba.com/nba-search/query.jsp?type=advvideo&section='+section+'&season=0910&npp=15'+category+extra
		u=sys.argv[0]+"?mode=1&url="+urllib.quote_plus(url)+"&cat="+urllib.quote_plus(name)+"&save="+urllib.quote_plus(url)
		xbmcplugin.addDirectoryItem(int(sys.argv[1]),u,item,True)
		
def showCategories(url,cat,save):
	url='http://www.nba.com/video/'
	data=open_url(url)
	teams=re.compile('onclick="nbaVideo\.changeTeamSection\(\'teams/(.+?)\',( )?\'All Videos\'\); \$\(\'nbaVidSltBg\'\)\.hide\(\);( )?return false;" href="#">(.+?)</a></li>').findall(data)
	for nick,space1,space2,team in teams:
		li=xbmcgui.ListItem(team)
		u=sys.argv[0]+"?mode=4&name="+urllib.quote_plus(team)+"&url="+urllib.quote_plus(nick)+"&cat="+urllib.quote_plus(team)+"&save="+urllib.quote_plus(save)
		xbmcplugin.addDirectoryItem(int(sys.argv[1]),u,li,True)

def showCategories2():
		nba=['bos', 'njn', 'nyk', 'phi', 'tor', 'chi', 'cle', 'det', 'ind', 'mil', 'atl', 'cha', 'mia', 'orl', 'was', 'dal', 'hou', 'mem', 'noh', 'sas', 'den', 'min', 'por', 'okc', 'uth', 'gsw', 'lac', 'lal', 'pho', 'sac']
		teams=['Boston Celtics', 'New Jersey Nets', 'New York Knicks', 'Philadelphia 76ers', 'Toronto Raptors', 'Chicago Bulls', 'Cleveland Cavaliers', 'Detroit Pistons', 'Indiana Pacers', 'Milwaukee Bucks', 'Atlanta Hawks', 'Charlotte Bobcats', 'Miami Heat', 'Orlando Magic', 'Washington Wizards', 'Dallas Mavericks', 'Houston Rockets', 'Memphis Grizzlies', 'New Orleans Hornets', 'San Antonio Spurs','Denver Nuggets', 'Minnesota Timberwolves', 'Portland Trail Blazers', 'Oklahoma City Thunder', 'Utah Jazz', 'Golden State Warriors', 'Los Angeles Clippers', 'Los Angeles Lakers', 'Phoenix Suns', 'Sacramento Kings' ]         
		x=0
		url="http://www.nba.com/.element/ssi/sect/1.1/video/teams.html"
		req = urllib2.Request(url)
		req.add_header('User-Agent', HEADER)
		f=urllib2.urlopen(req)
		a=f.read()
		f.close()
		p=re.compile('<td><a href="#" onclick="nbaVideo\.showTeamSection\(\'(.+?)\'\);return false"><img src="(.+?)"/><p>(.+?)</p></a></td')
		match=p.findall(a)
		for team,thumb,name in match:
			url = 'http://www.nba.com/.element/ssi/auto/1.1/aps/video/videoplayer/teams/'+team+'/'+team+'.originals1.html'
			# name=teams[x]
			# if (nba[x] == 'noh'):
				# nba[x] = 'nor'
			# thumb = 'http://assets.espn.go.com/i/teamlogos/nba/lrg/trans/'+nba[x]+'.gif'
			li=xbmcgui.ListItem(name, iconImage=thumb, thumbnailImage=thumb)
			u=sys.argv[0]+"?mode=8&name="+urllib.quote_plus(name)+"&url="+urllib.quote_plus(url)
			xbmcplugin.addDirectoryItem(int(sys.argv[1]),u,li,True)
			x=x+1

def TeamO(url,page,name):
	print url
	cat=name
	saveurl=url
	url=url[:-6]+str(page)+'.html'
	# req = urllib2.Request(url)
	# req.add_header('User-Agent', HEADER)
	# content=urllib2.urlopen(req)
	# data=content.read()
	# content.close()
	data=open_url(url)
	time=re.compile('>Play</a> <span class="nbaVidPodTime">(.+?)</span>').findall(data)
	image=re.compile('<img src="(.+?)">').findall(data)
	plot=re.compile('<p>(.*?)</p>').findall(data)
	url_title=re.compile('<a href="javascript:changePlaylist\(\'(.+?)\'\);">(.+?)</a>\n').findall(data)
	count=0
	for url,name in url_title:
		label=str(count+1+((page-1)*12))+') '+name+' - '+plot[count]+' ('+time[count].replace('00:','')+')'
		#url='http://ht.cdn.turner.com/nba/big/'+url.replace('/video/','')+'_nba_576x324.flv'
		thumb = image[count]
		item=xbmcgui.ListItem(label, iconImage=thumb, thumbnailImage=thumb)
		item.setInfo( type="Video", infoLabels={ "Title": name, "Director": 'NBA', "Studio": 'NBA', "Genre": cat, "Plot": plot[count] } )
		u=sys.argv[0]+"?mode=9&name="+urllib.quote_plus(name)+"&url="+urllib.quote_plus(url)+"&plot="+urllib.quote_plus(plot[count])+"&cat="+urllib.quote_plus(cat)
		xbmcplugin.addDirectoryItem(int(sys.argv[1]),u,item)
		count=count+1
	li=xbmcgui.ListItem("Next Page",iconImage="DefaultVideo.png", thumbnailImage=os.path.join(THUMBNAIL_PATH, 'next.png'))
	u=sys.argv[0]+"?mode=8&name="+urllib.quote_plus(name)+"&url="+urllib.quote_plus(saveurl)+"&page="+str(int(page)+1)
	xbmcplugin.addDirectoryItem(int(sys.argv[1]),u,li,True)



def showList(url,page):
		thisurl=url
		req = urllib2.Request(url)
		req.add_header('User-Agent', HEADER)
		f=urllib2.urlopen(req)
		a=f.read()
		f.close()
		p=re.compile('<div class="nbaVideoImageWrapper"><img src="(.+?)"><span class="nbaSpanOverlay"></span></div></a><a href="javascript:changePlaylist(''(.+?)'');" class="nbaVideoGridContentHeader">(.+?)</a><div class="nbaVideoGridTextBlock">(.+?)</div>')
		URLS=p.findall(a)
		x=0
		for thumb, url, url2, name, info in URLS:
			#print url
			save=name
			name = str(int(x+1))+'. '+name
			url=url.replace('(','')
			url=url.replace(')','')
			remove = "'"
			url=url.replace(remove,'')
			url=url.replace('/video/','')
			url=url.replace('.json','')
			url = 'http://nba.cdn.turner.com/nba/big/' + url + '_nba_576x324.flv'
			#print url
			#print "+"
			li=xbmcgui.ListItem(name, iconImage=thumb, thumbnailImage=thumb)
			li.setInfo( type="Video", infoLabels={ "Title": save, "Plot": info } )
			u=sys.argv[0]+"?mode=3&name="+urllib.quote_plus(save)+"&url="+urllib.quote_plus(url)+"&plot="+urllib.quote_plus('')
			xbmcplugin.addDirectoryItem(int(sys.argv[1]),u,li)
			x=x+1

def getDownloadFileName(basename):
	path = xbmcplugin.getSetting('download_path')
	if not path:
		dialog = xbmcgui.Dialog()
		path = dialog.browse(3, 'Choose Download Directory', 'video', '', False, False, '')
	if not path:
		raise UserCancelException('no directory selected')
	filename = xbmc.translatePath(os.path.join(path, basename))
	return filename


def playVideo(url, name, plot, cat):
	thisname=name
	date=url
	date=date.rsplit('/')
	name=date[10]
	name=name[:+32]
	print name
	def Download(url,dest):
			dp = xbmcgui.DialogProgress()
			dp.create('Downloading',thisname,'Filename: '+name)
			urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
	def _pbhook(numblocks, blocksize, filesize, url=None,dp=None):
			try:
					percent = min((numblocks*blocksize*100)/filesize, 100)
					dp.update(percent)
			except:
					percent = 100
					dp.update(percent)
			if dp.iscanceled():
					dp.close()
	flv_file = None
	stream = 'false'
	if (xbmcplugin.getSetting('download') == 'true'):
			dialog = xbmcgui.Dialog()
			flv_file = getDownloadFileName(name)
			Download(url, flv_file)
	elif (xbmcplugin.getSetting('download') == 'false'
	      and xbmcplugin.getSetting('download_ask') == 'true'):
		dia = xbmcgui.Dialog()
		ret = dia.select('What do you want to do?',
				 ['Download & Play', 'Stream', 'Exit'])
		if (ret == 0):
			flv_file = getDownloadFileName(name)
			Download(url, flv_file)
		elif (ret == 1):
			stream = 'true'
		else:
			pass
	elif (xbmcplugin.getSetting('download') == 'false' and xbmcplugin.getSetting('download_ask') == 'false'):
		stream = 'true'
	thumb = xbmc.getInfoImage( "ListItem.Thumb" )
	item = xbmcgui.ListItem(label=thisname,iconImage=thumb,thumbnailImage=thumb)
	item.setInfo( type="Video", infoLabels={ "Title": thisname, "Director": 'NBA', "Studio": 'NBA', "Genre": cat, "Plot": plot } )
	if xbmcplugin.getSetting("dvdplayer") == "true":
		player_type = xbmc.PLAYER_CORE_DVDPLAYER
	else:
		player_type = xbmc.PLAYER_CORE_MPLAYER
	if (flv_file != None and os.path.isfile(flv_file)):
		xbmc.Player(player_type).play(flv_file, item)
	elif (stream == 'true'):
		xbmc.Player(player_type).play(str(url), item)
	xbmc.sleep(200)

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

params=get_params()
mode=None
name=None
url=None
page=1
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
try:
        page=int(params["page"])
except:
        pass
try:
        plot=urllib.unquote_plus(params["plot"])
except:
		pass	
try:
        cat=urllib.unquote_plus(params["cat"])
except:
		pass
try:
        save=urllib.unquote_plus(params["save"])
except:
		pass

if mode==None:
	_check_for_update()
	showRoot()
elif mode==1:
	get_data(url,page,cat,save)
elif mode==2:
	get_feature(url,page,cat)
elif mode==3:
	get_video_info(url,page,name)
elif mode==4:
	showTeams(url,page,cat,save)
elif mode==5:
	showCategories(url,cat,save)
elif mode==6:
	showList2(url,page,cat)
elif mode==7:
	showList3(url)
elif mode==8:
	TeamO(url,page,name)
elif mode==9:
	get_video_info(url,page,name)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
	
