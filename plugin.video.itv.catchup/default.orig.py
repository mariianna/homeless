import urllib,urllib2,re,sys,socket,os,md5,datetime,xbmcplugin,xbmcgui, xbmcaddon

# external libs
sys.path.insert(0, os.path.join(os.getcwd(), 'lib'))
import utils, httplib2, socks, httplib, logging, time

from BeautifulSoup import BeautifulSoup
#import BeautifulStoneSoup

# setup cache dir
__scriptname__  = 'ITV'
__scriptid__ = "plugin.video.itv"
__addoninfo__ = utils.get_addoninfo(__scriptid__)
__addon__ = __addoninfo__["addon"]
__settings__   = xbmcaddon.Addon(id=__scriptid__)


DIR_CACHE = xbmc.translatePath(os.path.join( "T:"+os.sep,"plugin_data", __scriptname__,'cache' ))  
if not os.path.isdir(DIR_CACHE):
    try:
        os.makedirs(DIR_CACHE)
    except:
        DIR_CACHE = os.path.join(os.getcwd(),'cache')
        os.makedirs(DIR_CACHE)

DIR_USERDATA   = xbmc.translatePath(__addoninfo__["profile"])
SUBTITLES_DIR  = os.path.join(DIR_USERDATA, 'Subtitles')
IMAGE_DIR      = os.path.join(DIR_USERDATA, 'Images')

if not os.path.isdir(DIR_USERDATA):
    os.makedirs(DIR_USERDATA)
if not os.path.isdir(SUBTITLES_DIR):
    os.makedirs(SUBTITLES_DIR)
if not os.path.isdir(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

def get_proxy():
    proxy_server = None
    proxy_type_id = 0
    proxy_port = 8080
    proxy_user = None
    proxy_pass = None
    try:
        proxy_server = __settings__.getSetting('proxy_server')
        proxy_type_id = __settings__.getSetting('proxy_type')
        proxy_port = int(__settings__.getSetting('proxy_port'))
        proxy_user = __settings__.getSetting('proxy_user')
        proxy_pass = __settings__.getSetting('proxy_pass')
    except:
        pass

    if   proxy_type_id == '0': proxy_type = socks.PROXY_TYPE_HTTP_NO_TUNNEL
    elif proxy_type_id == '1': proxy_type = socks.PROXY_TYPE_HTTP
    elif proxy_type_id == '2': proxy_type = socks.PROXY_TYPE_SOCKS4
    elif proxy_type_id == '3': proxy_type = socks.PROXY_TYPE_SOCKS5

    proxy_dns = True
    
    return (proxy_type, proxy_server, proxy_port, proxy_dns, proxy_user, proxy_pass)

def get_httplib():
    http = None
    try:
        if __settings__.getSetting('proxy_use') == 'true':
            (proxy_type, proxy_server, proxy_port, proxy_dns, proxy_user, proxy_pass) = get_proxy()
            logging.info("Using proxy: type %i rdns: %i server: %s port: %s user: %s pass: %s", proxy_type, proxy_dns, proxy_server, proxy_port, "***", "***")
            http = httplib2.Http(proxy_info = httplib2.ProxyInfo(proxy_type, proxy_server, proxy_port, proxy_dns, proxy_user, proxy_pass))
        else:
 	  logging.info("No Proxy\n")
          http = httplib2.Http()
    except:
        raise
        logging.error('Failed to initialize httplib2 module')

    return http

http = get_httplib()


http.cache = httplib2.FileCache(DIR_CACHE, safe=lambda x: md5.new(x).hexdigest())
       
# what OS?        
environment = os.environ.get( "OS", "xbox" )


############## SUBS #################


def httpget(url):
	resp = ''
	data = ''
	http = get_httplib()
	resp, data = http.request(url, "GET")
	return data


def download_subtitles(url, offset):
    # Download and Convert the TTAF format to srt
    # SRT:
    #1
    #00:01:22,490 --> 00:01:26,494
    #Next round!
    #
    #2
    #00:01:33,710 --> 00:01:37,714
    #Now that we've moved to paradise, there's nothing to eat.
    #
    
    # TT:
    #<p begin="0:01:12.400" end="0:01:13.880">Thinking.</p>
    
    logging.info('subtitles at =%s' % url)
    outfile = os.path.join(SUBTITLES_DIR, 'itv.srt')
    fw = open(outfile, 'w')
    
    if not url:
        fw.write("1\n0:00:00,001 --> 0:01:00,001\nNo subtitles available\n\n")
        fw.close() 
        return
    
    txt = httpget(url)
        
    p= re.compile('^\s*<p.*?begin=\"(.*?)\.([0-9]+)\"\s+.*?end=\"(.*?)\.([0-9]+)\"\s*>(.*?)</p>')
    i=0
    prev = None

    # some of the subtitles are a bit rubbish in particular for live tv
    # with lots of needless repeats. The follow code will collapse sequences
    # of repeated subtitles into a single subtitles that covers the total time
    # period. The downside of this is that it would mess up in the rare case
    # where a subtitle actually needs to be repeated 
    for line in txt.split('\n'):
        entry = None
        m = p.match(line)
        if m:
            start_mil = "%s000" % m.group(2) # pad out to ensure 3 digits
            end_mil   = "%s000" % m.group(4)
            
            ma = {'start'     : m.group(1), 
                  'start_mil' : start_mil[:3], 
                  'end'       : m.group(3), 
                  'end_mil'   : start_mil[:3], 
                  'text'      : m.group(5)}



    
            ma['text'] = ma['text'].replace('&amp;', '&')
            ma['text'] = ma['text'].replace('&gt;', '>')
            ma['text'] = ma['text'].replace('&lt;', '<')
            ma['text'] = ma['text'].replace('<br />', '\n')
            ma['text'] = ma['text'].replace('<br/>', '\n')
            ma['text'] = re.sub('<.*?>', '', ma['text'])
            ma['text'] = re.sub('&#[0-9]+;', '', ma['text'])
            #ma['text'] = ma['text'].replace('<.*?>', '')
    
            if not prev:
                # first match - do nothing wait till next line
                prev = ma
                continue
            
            if prev['text'] == ma['text']:
                # current line = previous line then start a sequence to be collapsed
                prev['end'] = ma['end']
                prev['end_mil'] = ma['end_mil']
            else:
                i += 1
		l = (prev['start']).split(':')
		start_seconds = int(l[0]) * 3600 + int(l[1]) * 60 + int(l[2])
		start_seconds = start_seconds + offset
		m = (prev['end']).split(':')
		end_seconds = int(m[0]) * 3600 + int(m[1]) * 60 + int(m[2])
		end_seconds = end_seconds + offset
	


		start_mins, start_secs = divmod(start_seconds, 60)
		start_hours, start_mins = divmod(start_mins, 60)

                end_mins, end_secs = divmod(end_seconds, 60)
                end_hours, end_mins = divmod(end_mins, 60)

                #entry = "%d\n%s,%s --> %s,%s\n%s\n\n" % (i, prev['start'], prev['start_mil'], prev['end'], prev['end_mil'], prev['text'])
		#if (i==1):
		#	start_hours=00
		#	start_mins=00
		#	start_secs=00

		entry = "%d\n%02d:%02d:%02d,%s --> %02d:%02d:%02d,%s\n%s\n\n" % (i, start_hours, start_mins, start_secs, prev['start_mil'], end_hours, end_mins, end_secs, prev['end_mil'], prev['text'])
                prev = ma
        elif prev:
            i += 1
            l = (prev['start']).split(':')
            start_seconds = int(l[0]) * 3600 + int(l[1]) * 60 + int(l[2])
	    start_seconds = start_seconds + offset
            m = (prev['end']).split(':')
            end_seconds = int(m[0]) * 3600 + int(m[1]) * 60 + int(m[2])
	    end_seconds = end_seconds + offset
            start_mins, start_secs = divmod(start_seconds, 60)
            start_hours, start_mins = divmod(start_mins, 60)

            end_mins, end_secs = divmod(end_seconds, 60)
            end_hours, end_mins = divmod(end_mins, 60)

            #entry = "%d\n%s,%s --> %s,%s\n%s\n\n" % (i, prev['start'], prev['start_mil'], prev['end'], prev['end_mil'], prev['text'])
	    #if(i==1):
	#	start_hours=00
	#	start_mins=00
	#	start_secs=00
            entry = "%d\n%02d:%02d:%02d,%s --> %02d:%02d:%02d,%s\n%s\n\n" % (i, start_hours, start_mins, start_secs, prev['start_mil'], end_hours, end_mins, end_secs, prev['end_mil'], prev['text'])
            
        if entry: fw.write(entry)
    
    fw.close()    
    return outfile

def CATS():
        SHOWS('http://www.itv.com/_data/xml/CatchUpData/CatchUp360/CatchUpMenu.xml')
        #addDir("ITV CATCH-UP  :  A -Z","http://www.itv.com/_data/xml/CatchUpData/CatchUp360/CatchUpMenu.xml",1,'http://itv-images.adbureau.net/itv/catch-up_Sponsor%20button_1x1_Apr08.jpg')
        #addDir("THE BEST OF ITV - CRIME","http://www.itv.com/ClassicTVshows/crime/default.html",4,'http://www.itv.com/img/470x113/TV-Classics-Crime-c7d9e02e-a48e-4e8d-8842-46250b5af367.jpg')
        #addDir("THE BEST OF ITV - PERIOD DRAMA","http://www.itv.com/ClassicTVshows/perioddrama/default.html",4,'http://www.itv.com/img/470x113/TV-Classics-Period-Drama-4a332b58-a8b0-44bc-a444-635b7d6358df.jpg')
        #addDir("THE BEST OF ITV - FAMILY DRAMA","http://www.itv.com/ClassicTVshows/familydrama/default.html",4,'http://www.itv.com/img/470x113/TV-Classics-Family-Drama-768a59ff-2ab2-432d-9d2f-ffe20cec0632.jpg')
        #addDir("THE BEST OF ITV - DOCUMENTARY","http://www.itv.com/ClassicTVshows/documentary/default.html",4,'http://www.itv.com/img/470x113/0891a94b-79ef-4649-8ccf-1ad33f2c7c93.jpg')
        #addDir("THE BEST OF ITV - COMEDY","http://www.itv.com/ClassicTVshows/comedy/default.html",4,'http://www.itv.com/img/470x113/TV-Classics-Comedy-8685d32f-eace-490b-8004-d1d44d4a8b9b.jpg')
        #addDir("THE BEST OF ITV - KIDS","http://www.itv.com/ClassicTVshows/kids/default.html",4,'http://www.itv.com/img/470x113/04741e4a-ba5e-48ee-ae32-50fe7bde69d1.jpg')
        #addDir("THE BEST OF ITV - SOAPS","http://www.itv.com/ClassicTVshows/soaps/default.html",4,'http://www.itv.com/img/470x113/66fb8a0f-db7d-4094-8dcc-119f2c669eaa.jpg')
        #addDir('ITV 1-4 LIVE STREAMS','http://minglefrogletpigletdog.com',6,'http://cdn-ll-73.viddler.com/e2/thumbnail_1_d6938e73.jpg')

def STREAMS():
        streams=[]
        key = get_url('http://www.itv.com/_app/dynamic/AsxHandler.ashx?getkey=please')
        for channel in range(1,5):
                streaminfo = get_url('http://www.itv.com/_app/dynamic/AsxHandler.ashx?key='+key+'&simid=sim'+str(channel)+'&itvsite=ITV&itvarea=SIMULCAST.SIM'+str(channel)+'&pageid=4567756521')
                stream=re.compile('<TITLE>(.+?)</TITLE><REF href="(.+?)" />').findall(streaminfo)
                streams.append(stream[1])
        for name,url in streams:
                addLink(name,url)

def BESTOF(url):
        response = get_url(url).replace('&amp;','&')
        match=re.compile('<li><a href="(.+?)"><img src=".+?" alt=".+?"></a><h4><a href=".+?">(.+?)</a></h4>').findall(response)
        for url,name in match:
                addDir(name,url,5,'')
                
def BESTOFEPS(url):
        response = get_url(url).replace('&amp;','&')
        eps=re.compile('<a [^>]*?title="Play" href=".+?vodcrid=crid://itv.com/(.+?)&DF=0"><img\s* src="(.*?)" alt="(.*?)"').findall(response)
        if eps:
            for url,thumb,name in eps:
                addDir(name,url,3,'http://itv.com/'+thumb,isFolder=False)
            return
        eps=re.compile('<a [^>]*?title="Play" href=".+?vodcrid=crid://itv.com/(.+?)&DF=0">(.+?)</a>').findall(response)
        if not eps: eps=re.compile('href=".+?vodcrid=crid://itv.com/(.+?)&G=.+?&DF=0">(.+?)</a>').findall(response)
        if not eps:
                eps=re.compile('<meta name="videoVodCrid" content="crid://itv.com/(.+?)">').findall(response)
                name=re.compile('<meta name="videoMetadata" content="(.+?)">').findall(response)
                eps=[(eps[0],name[0])]
        for url,name in eps:
                addDir(name,url,3,'',isFolder=False)
        
def SHOWS(url):
        response = get_url(url)
        code=re.sub('&amp;','&',response)
        match=re.compile('<ProgrammeId>(.+?)</ProgrammeId>\r\n      <ProgrammeTitle>(.+?)</ProgrammeTitle>\r\n      <ProgrammeMediaId>.+?</ProgrammeMediaId>\r\n      <ProgrammeMediaUrl>(.+?)</ProgrammeMediaUrl>\r\n      <LastUpdated>.+?</LastUpdated>\r\n      <Url>.+?</Url>\r\n      <EpisodeCount>(.+?)</EpisodeCount>').findall(code)
        for url,name,thumb,epnumb in match:
                if not int(epnumb)<1:
                        addDir(name+' - '+epnumb+' Episodes Available.',url,2,thumb)

def EPS(url):
        response = get_url("http://www.itv.com/_app/Dynamic/CatchUpData.ashx?ViewType=1&Filter=%s&moduleID=115107"%url)
        #print response
        soup = BeautifulSoup(response,convertEntities="html")
        for episode in soup.findAll('div', attrs={'class' : re.compile('^listItem')}):
            thumb = str(episode.div.a.img['src'])
            pid = re.findall('.+?Filter=(.+?)$', str(episode.div.a['href']))[0]
	    image_name = pid + '.jpg'
	    outfile = os.path.join(IMAGE_DIR, image_name)
	    fw = open(outfile, 'w')
	    txt = httpget(thumb)
	    fw.write(txt)
	    fw.close()
            name = str(episode.div.a.img['alt'])
            date = decode_date(str(episode.find('div', 'content').p.contents[0]))
            desc = str(episode.find('p', 'progDesc').contents[0])
            addDir(name+' '+date+'. '+desc ,pid,3,thumb,desc,isFolder=False)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')

def VIDEO(url):
	#print "URL: " + url
	pid = url
	SM_TEMPLATE = """<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
	  <SOAP-ENV:Body>
	    <tem:GetPlaylist xmlns:tem="http://tempuri.org/" xmlns:itv="http://schemas.datacontract.org/2004/07/Itv.BB.Mercury.Common.Types" xmlns:com="http://schemas.itv.com/2009/05/Common">
	      <tem:request>
		<itv:RequestGuid>FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF</itv:RequestGuid>
		<itv:Vodcrid>
		  <com:Id>%s</com:Id>
		  <com:Partition>itv.com</com:Partition>
		</itv:Vodcrid>
	      </tem:request>
	      <tem:userInfo>
		<itv:GeoLocationToken>
		  <itv:Token/>
		</itv:GeoLocationToken>
		<itv:RevenueScienceValue>scc=true; svisit=1; sc4=Other</itv:RevenueScienceValue>
	      </tem:userInfo>
	      <tem:siteInfo>
		<itv:Area>ITVPLAYER.VIDEO</itv:Area>
		<itv:Platform>DotCom</itv:Platform>
		<itv:Site>ItvCom</itv:Site>
	      </tem:siteInfo>
	    </tem:GetPlaylist>
	  </SOAP-ENV:Body>
	</SOAP-ENV:Envelope>
	"""
    

	SoapMessage = SM_TEMPLATE%(url)

	#print SoapMessage

	#construct and send the header

	http = get_httplib()
	

#	webservice = http("mercury.itv.com")
#	webservice.putrequest("POST", "/PlaylistService.svc")
#	webservice.putheader("Host", "mercury.itv.com")
#	webservice.putheader("Referer", "http://www.itv.com/mercury/Mercury_VideoPlayer.swf?v=1.6.479/[[DYNAMIC]]/2")
#	webservice.putheader("Content-type", "text/xml; charset=\"UTF-8\"")
#	webservice.putheader("Content-length", "%d" % len(SoapMessage))
#	webservice.putheader("SOAPAction", "http://tempuri.org/PlaylistService/GetPlaylist")
#	webservice.endheaders()
#	webservice.send(SoapMessage)

	# get the response

#	statuscode, statusmessage, header = webservice.getreply()
	#print "Response: ", statuscode, statusmessage
	#print "headers: ", header
#	res = webservice.getfile().read()



	url = 'http://mercury.itv.com/PlaylistService.svc'
	headers = {"Host":"mercury.itv.com","Referer":"http://www.itv.com/mercury/Mercury_VideoPlayer.swf?v=1.6.479/[[DYNAMIC]]/2","Content-type":"text/xml; charset=\"UTF-8\"","Content-length":"%d" % len(SoapMessage),"SOAPAction":"http://tempuri.org/PlaylistService/GetPlaylist"}
	response, res = http.request(url, 'POST', headers=headers, body=SoapMessage)



	#print res




	
	title1= res.split("<ProgrammeTitle>")
        title2= title1[1].split("</ProgrammeTitle>")


	#print res
	res = re.search('<VideoEntries>.+?</VideoEntries>', res, re.DOTALL).group(0)
	rendition_offset= res.split("rendition-offset=")
	offset_seconds = rendition_offset[1].split(":")
	#print "OFFSET IS", offset_seconds[2]
	offset = int(offset_seconds[2])


	mediafile =  res.split("<MediaFile delivery=")
	cc1 = res.split("ClosedCaptioningURIs>")
	there_are_subtitles=1
	if len(cc1)>1:
		pattern = re.compile(r'\s+')
		cc2 = re.sub(pattern, ' ', cc1[1])
		cc3 = cc2.split(" <URL><![CDATA[")
		cc_url_all = cc3[1].split("]]></URL> </")
		#print "Caption: ", cc_url_all[0]
		#cc_url = cc_url_all[0]
		cc_url_long = (cc_url_all[0].split("xml"))
		cc_url = cc_url_long[0] + "xml"
		print "Subtitles URL ", cc_url
		subtitles_file = download_subtitles(cc_url, offset)
		print "Subtitles at ", subtitles_file
		there_are_subtitles=1
	else:
		print "No Captions\n"
    		outfile = os.path.join(SUBTITLES_DIR, 'itv.srt')
		subtitles_file = outfile
    		fw = open(outfile, 'w')
        	fw.write("1\n0:00:00,001 --> 0:01:00,001\n<font color='Red'>No subtitles available\n</font>\n")
        	fw.close()
		#there_are_subtitles=0

	for index in range(len(mediafile)):
        	print ("MEDIA ENTRY %d %s"),index, mediafile[index]


	quality = int(__settings__.getSetting('video_stream'))
	#print ("QUALITY IS %d\n",quality)
	selected_stream = 4
	
	if (quality == 0):
		selected_stream = index	

	if (quality == 4):
		if(index==4):
			selected_stream = 4
		else:
			selected_stream = index
	
	if (quality == 3):
		if(index>=3):
			selected_stream = 3
		else:
			selected_stream = index
	
        if (quality == 2):
                if(index>=2):
                        selected_stream = 2
                else:
                        selected_stream = index

        if (quality == 1):
                if(index>=1):
                        selected_stream =1 
                else:
                        selected_stream = index
	
	

	#print res

	rtmp = re.compile('(rtmp[^"]+)').findall(res)[0]
	#playpath = re.compile('(mp4:[^\]]+)').findall(res)[0]
	playpath = re.compile('(mp4:[^\]]+)').findall(mediafile[selected_stream])[0]

	#print playpath
	#print urllib.unquote_plus(rtmp)
	rtmp = rtmp.replace('&amp;','&')
	#print "rtmp " + rtmp

	#item = xbmcgui.ListItem('ITV')
	url = rtmp + " swfurl=http://www.itv.com/mercury/Mercury_VideoPlayer.swf playpath=" + playpath + " swfvfy=true"
	listitem = xbmcgui.ListItem(name)
	image_name = pid + '.jpg'
	thumbfile = os.path.join(IMAGE_DIR, image_name)
	listitem.setThumbnailImage(thumbfile)
	listitem.setInfo('video', {'Title': title2[0]})
	play=xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
	play.clear()
	play.add(url,listitem)
	player.play(play)
	if (there_are_subtitles==1):
		player.setSubtitles(subtitles_file)
        #xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(url, item)
        #xbmc.executebuiltin('XBMC.ActivateWindow(fullscreenvideo)')




        #response = get_url("http://www.itv.com/_app/video/GetMediaItem.ashx?vodcrid=crid://itv.com/%s&bitrate=384"%url).replace('&amp;','&')
        #match=re.compile('<LicencePlaylist>(.+?)&Add.+?/LicencePlaylist>').findall(response)
        #response = get_url(match[0])
        #match=re.compile('<Entry><ref href="(.+?)" /><param value="true" name="Prebuffer" /><PARAM NAME="PrgPartNumber" VALUE="(.+?)" /><PARAM NAME="FileName" VALUE="(.+?)" />').findall(response)
        #play=xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        #play.clear()
        #for baseurl,name,wmv in match:
        #    #addLink(name,'%s/%s'%(baseurl,wmv))
        #    liz=xbmcgui.ListItem(name)
        #    liz.setInfo( type="Video", infoLabels={ "Title": name } )
        #    play.add(decode_redirect('%s/%s'%(baseurl,wmv)),liz)
        #player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
        #player.play(play)

def decode_redirect(url):
	
    # some of the the urls passed in are redirects that are not handled by XBMC.
    # These are text files with multiple stream urls

    #if environment in ['xbox', 'linux']:
    #    # xbox xbmc works just fine with redirects
    #    return url

    response = get_url(url).replace('&amp;','&')
    match=re.compile('Ref1\=(http.*)\s').findall(response)

    stream_url = None
    if match:
        stream_url = match[0].rstrip()
    else:
        # no match so pass url to xbmc and see if the url is directly supported 
        stream_url = url

    return stream_url

def decode_date(date):
    # format eg Sat 10 Jan 2009
    (dayname,day,monthname,year) = date.split(' ')
    if not year:
        return date
    month=1
    monthname = monthname.lower()
    lookup = {'jan':1, 'feb':2, 'mar':3, 'apr':4, 'may':5, 'jun':6, 'jul':7, 'aug':8, 'sep':9, 'oct':10, 'nov':11, 'dec':12}
    if lookup.has_key(monthname[:3]):
        month=lookup[monthname[:3]]
    
    try:
        # yes I know the colons are weird but the 2009-01-25 xbox release
        # when in filemode (but not library mode) converts YYYY-MM-DD in (YYYY)
        sep='-'
        if environment == 'xbox': sep=':' 
        ndate = "%04d%s%02d%s%02d" % (int(year),sep,int(month),sep,int(day))
    except:
        # oops funny date, return orgional date
        return date
    #print "Date %s from %s" % (ndate, date)
    return ndate

def get_url(url):
    #try:
        #req = urllib2.Request(url)
        #req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        #return urllib2.urlopen(req).read()
    
    # first try
    http = get_httplib()
    data = None    
    try:
        resp, data = http.request(url, 'GET')
    except: pass
    
    # second try
    if not data:
        try:
            resp, data = http.request(url, 'GET')
        except: 
            dialog = xbmcgui.Dialog()
            dialog.ok('Network Error', 'Failed to fetch URL', url)
            print 'Network Error. Failed to fetch URL %s' % url
            raise
    
    return data


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

      
def addLink(name,url):
        ok=True
        thumbnail_url = url.split( "thumbnailUrl=" )[ -1 ]
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=thumbnail_url)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

def addDir(name,url,mode,iconimage,plot='',isFolder=True):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        print "addDir " + name
        liz=xbmcgui.ListItem(name,iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": plot} )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=isFolder)
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
        print "categories"
        CATS()
elif mode==1:
        print "index of : "+url
        SHOWS(url)
elif mode==2:
        print "Getting Episodes: "+url
        EPS(url)
elif mode==3:
        print "Getting Videofiles: "+url
        VIDEO(url)
elif mode==4:
        print "Getting Videofiles: "+url
        BESTOF(url)
elif mode==5:
        print "Getting Videofiles: "+url
        BESTOFEPS(url)
elif mode==6:
        print "Getting Videofiles: "+url
        STREAMS()



xbmcplugin.endOfDirectory(int(sys.argv[1]))
