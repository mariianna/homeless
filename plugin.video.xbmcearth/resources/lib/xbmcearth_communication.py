#User-Agent: XBMC/8.10 (compatible; MSIE 6.0; Windows NT 5.1; WinampMPEG/5.09)
import xbmc, datetime, tarfile, os, glob, urllib, httplib, sys, os.path, time, datetime, urllib2
from threading import Thread
from string import Template

TEMPFOLDER = os.path.join( os.getcwd().replace( ";", "" ), "temp\\" )	

class Xbmcearth_communication:
	sTargetServer = ""
	sTargetUrl = ""
	sData = []
	def get_Query_Place(self, url, key, place):
		header = {
			"Host":"maps.google.com",
			"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11",
			"Accept":"*/*",
			"Accept-Language":"de-de,de;q=0.8,en-us;q=0.5,en;q=0.3",
			"Accept-Charset":"ISO-8859-1,utf-8;q=0.7,*;q=0.7",
			"Keep-Alive":"300",
			"Proxy-Connection":"keep-alive",
			"Referer": url}
		place = urllib.quote(place) 
		params = '?q=' + place + '&output=kml&key='+ key 
		body = ''
		self.sTargetUrl = "http://maps.google.com/maps"
		if self._request("GET",params,header, body)!=True:
			return False
		data = self.sData
		fName = file
		f = open(TEMPFOLDER + "query.kml", 'wb')
		f.write(data)
		f.close()
		return self.sData

	def get_Route(self, url, saddr, daddr):
		try:
			os.mkdir(TEMPFOLDER+"Route")
		except: pass
		header = {
			"Host":"maps.google.com",
			"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11",
			"Accept":"*/*",
			"Accept-Language":"de-de,de;q=0.8,en-us;q=0.5,en;q=0.3",
			"Accept-Charset":"ISO-8859-1,utf-8;q=0.7,*;q=0.7",
			"Keep-Alive":"300",
			"Proxy-Connection":"keep-alive",
			"Referer": url}
		if xbmc.getLanguage() == 'German':
			lang = 'de'
		else:
			lang = 'en'
		saddr = urllib.quote(saddr) 
		daddr = urllib.quote(daddr) 
		params = '?f=d&source=s_d&saddr=\"' + saddr + '\"&daddr=\"' + daddr + '\"&hl='+ lang +'&geocode=&mra=ls&output=kml' 
		body = ''
		self.sTargetUrl = "http://maps.google.com/maps"
		if self._request("GET",params,header, body)!=True:
			return False
		data = self.sData
		fName = file
		f = open(TEMPFOLDER + "Route\\route.kml", 'wb')
		f.write(data)
		f.close()
		return self.sData
	
	def get_Panoramio(self, url, param):
		header = {
			"Host":"www.panoramio.com",
			"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11",
			"Accept":"*/*",
			"Accept-Language":"de-de,de;q=0.8,en-us;q=0.5,en;q=0.3",
			"Accept-Charset":"ISO-8859-1,utf-8;q=0.7,*;q=0.7",
			"Keep-Alive":"300",
			"Proxy-Connection":"keep-alive",
			"Referer": url} 
		params = param
		#-print params
		body = ''
		self.sTargetUrl = "http://www.panoramio.com/map/get_panoramas.php"
		if self._request("GET",params,header, body)!=True:
			return False
		data = self.sData
		fName = file
		f = open(TEMPFOLDER + "panoramio.xml", 'wb')
		f.write(data)
		f.close()
		return self.sData
		
	def get_Flickr(self, url, param):
		header = {
			"Host":"api.flickr.com",
			"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11",
			"Accept":"*/*",
			"Accept-Language":"de-de,de;q=0.8,en-us;q=0.5,en;q=0.3",
			"Accept-Charset":"ISO-8859-1,utf-8;q=0.7,*;q=0.7",
			"Keep-Alive":"300",
			"Proxy-Connection":"keep-alive",
			"Referer": url} 
		params = param
		body = ''
		self.sTargetUrl = "http://api.flickr.com/services/rest"
		if self._request("GET",params,header, body)!=True:
			return False
		data = self.sData
		fName = file
		f = open(TEMPFOLDER + "flickr.xml", 'wb')
		f.write(data)
		f.close()
		return self.sData

	def get_Locr(self, url, param):
		header = {
			"Host":"www.locr.com",
			"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11",
			"Accept":"*/*",
			"Accept-Language":"de-de,de;q=0.8,en-us;q=0.5,en;q=0.3",
			"Accept-Charset":"ISO-8859-1,utf-8;q=0.7,*;q=0.7",
			"Keep-Alive":"300",
			"Proxy-Connection":"keep-alive",
			"Referer": url} 
		params = param
		body = ''
		self.sTargetUrl = "http://www.locr.com/api/get_photos_json.php"
		if self._request("GET",params,header, body)!=True:
			return False
		data = self.sData
		fName = file
		f = open(TEMPFOLDER + "locr.xml", 'wb')
		f.write(data)
		f.close()
		return self.sData
		
	def get_Youtube(self, url, param):
		header = {
			"Host":"gdata.youtube.com",
			"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11",
			"Accept":"*/*",
			"Accept-Language":"de-de,de;q=0.8,en-us;q=0.5,en;q=0.3",
			"Accept-Charset":"ISO-8859-1,utf-8;q=0.7,*;q=0.7",
			"Keep-Alive":"300",
			"Proxy-Connection":"keep-alive",
			"Referer": url} 
		params = param
		body = ''
		self.sTargetUrl = "http://gdata.youtube.com/feeds/api/videos"
		if self._request("GET",params,header, body)!=True:
			return False
		data = self.sData
		fName = file
		f = open(TEMPFOLDER + "youtube.xml", 'wb')
		f.write(data)
		f.close()
		return self.sData
		
	def get_Weather(self, url, param):
		if xbmc.getLanguage() == 'German':
			header = {
				"Host":"www.google.com",
				"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11",
				"Accept":"*/*",
				"Accept-Language":"de-de,de",
				"Accept-Charset":"ISO-8859-1,utf-8;q=0.7,*;q=0.7",
				"Keep-Alive":"300",
				"Proxy-Connection":"keep-alive",
				"Referer": url} 
		else:
			header = {
				"Host":"www.google.com",
				"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11",
				"Accept":"*/*",
				"Accept-Language":"en-en,en",
				"Accept-Charset":"ISO-8859-1,utf-8;q=0.7,*;q=0.7",
				"Keep-Alive":"300",
				"Proxy-Connection":"keep-alive",
				"Referer": url} 
		params = param
		body = ''
		self.sTargetUrl = "http://www.google.com/ig/api"
		print self.sTargetUrl + params
		if self._request("GET",params,header, body)!=True:
			return False
		data = self.sData
		fName = file
		f = open(TEMPFOLDER + "weather.xml", 'wb')
		f.write(data)
		f.close()
		return self.sData
	
	def get_Youtube_html(self, url, param):
		header = {
			"Host":"www.youtube.com",
			"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11",
			"Accept":"*/*",
			"Accept-Language":"de-de,de;q=0.8,en-us;q=0.5,en;q=0.3",
			"Accept-Charset":"ISO-8859-1,utf-8;q=0.7,*;q=0.7",
			"Keep-Alive":"300",
			"Proxy-Connection":"keep-alive",
			"Referer": url} 
		params = param
		body = ''
		self.sTargetUrl = "http://www.youtube.com/watch"
		if self._request("GET",params,header, body)!=True:
			return False
		data = self.sData
		fName = file
		f = open(TEMPFOLDER + "youtube.html", 'wb')
		f.write(data)
		f.close()
		return self.sData
		
	def stream_Youtube(self, v_url):
		request = urllib2.Request(v_url) 
		proxy=[urllib2.ProxyHandler({'http':'inetproxy.global.bdfgroup.net:8080'})]
		opener=urllib2.build_opener(proxy)
		opener = urllib2.build_opener(SRH) 
		f = opener.open(request) 
		vid_url = f.url 
		return vid_url
		
	def get_Webcams(self, url, param):
		header = {
			"Host":"api.webcams.travel",
			"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11",
			"Accept":"*/*",
			"Accept-Language":"de-de,de;q=0.8,en-us;q=0.5,en;q=0.3",
			"Accept-Charset":"ISO-8859-1,utf-8;q=0.7,*;q=0.7",
			"Keep-Alive":"300",
			"Proxy-Connection":"keep-alive",
			"Referer": url} 
		params = param
		body = ''
		self.sTargetUrl = "http://api.webcams.travel/rest"
		if self._request("GET",params,header, body)!=True:
			return False
		data = self.sData
		fName = file
		f = open(TEMPFOLDER + "webcams.xml", 'wb')
		f.write(data)
		f.close()
		return self.sData

	def get_Google_Analytics(self, url, pagetitle, page, window):
		self.window=window
		if xbmc.getCondVisibility('system.platform.windows'):
			header = {
				"Host":"www.google-analytics.com",
				"User-Agent":"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
				"Accept":"*/*",
				"UA-CPU": "x86",
				"Accept-Language":"de",
				"Connection": "Keep-Alive",
				"NovINet": "v1.0",
				"Referer": "http://www.xbmcmaps.de/"} 
		elif xbmc.getCondVisibility('system.platform.linux'):
			header = {
				"Host":"www.google-analytics.com",
				"User-Agent":"Mozilla/5.0 (X11; U; Linux i586; en-US; rv:1.7.3) Gecko/20040924 Epiphany/1.4.4 (Ubuntu)",
				"Accept":"*/*",
				"UA-CPU": "x86",
				"Accept-Language":"de",
				"Connection": "Keep-Alive",
				"NovINet": "v1.0",
				"Referer": "http://www.xbmcmaps.de/"}
		elif xbmc.getCondVisibility('system.platform.xbox'):
			header = {
				"Host":"www.google-analytics.com",
				"User-Agent":"Mozilla/4.0 (compatible; MSIE 5.0; Windows NT 5.0)",
				"Accept":"*/*",
				"UA-CPU": "x86",
				"Accept-Language":"de",
				"Connection": "Keep-Alive",
				"NovINet": "v1.0",
				"Referer": "http://www.xbmcmaps.de/"}	
		else:
			header = {
				"Host":"www.google-analytics.com",
				"User-Agent":"Mozilla/5.0 (Macintosh; PPC Mac OS X)",
				"Accept":"*/*",
				"UA-CPU": "x86",
				"Accept-Language":"de",
				"Connection": "Keep-Alive",
				"NovINet": "v1.0",
				"Referer": "http://www.xbmcmaps.de/"}	
		self.connect("www.google-analytics.com")
		import random
		utmn_rnd =        str(random.randint(1000000000,9999999999))
		utmhid_rnd = str(random.randint(1000000000,9999999999))
		
		params = "?utmwv=1.3&utmn=$utmn&utmcs=iso-8859-1&utmsr=$utmsr&utmsc=32-bit&utmfl=9.0%20r47&utmul=de&utmje=1&utmdt=$utmdt&utmhn=$utmhn&utmhid=$utmhid&utmr=-&utmp=$utmp&utmac=$utmac"
		params = params + "&utmcc=__utma%3D$utma1.$utma2.$utma3.$utma4.$utma5.$utma6%3B%2B__utmz%3D$utmz1.$utmz2.1.1.utmccn%3D(direct)%7Cutmcsr%3D(direct)%7Cutmcmd%3D(none)%3B%2B"
		params = Template(params)
		params = params.substitute(utmn = utmn_rnd, utmsr=str(self.window.getWidth())+'x'+str(self.window.getHeight()), utmdt = pagetitle, utmhn = self.window.set.settings["analytics"]["url"], utmp = page, utmhid = utmhid_rnd, utmac = self.window.set.settings["analytics"]["utmac"],	utma1 = self.window.set.settings["analytics"]["cookie_number"], utma2 = self.window.set.settings["analytics"]["random"], utma3 = self.window.set.settings["analytics"]["first_use"], utma4 = self.window.set.settings["analytics"]["last_use"], utma5 = self.window.set.settings["analytics"]["now"], utma6 = self.window.set.settings["analytics"]["count"], utmb = self.window.set.settings["analytics"]["random"], utmc = self.window.set.settings["analytics"]["random"], utmz1 = self.window.set.settings["analytics"]["cookie_number"], utmz2 = self.window.set.settings["analytics"]["first_use"])		
		body = ''
		self.sTargetUrl = "http://www.google-analytics.com/__utm.gif"
		if self._request("GET",params,header, body)!=True:
			return False
		data = self.sData
		return self.sData
		
		
	def get_Maps_JS(self, url, key):
		#http://maps.google.com/maps?file=api&v=2&key=ABQIAAAAnyP-GOJDhG7H7ozm0RRsCBSiQ_eECfBHgA9cMSxRoMYUiueUzxSinT-_iJIghikcXgs_lmKq8_i5pQ
		#GET /maps?file=api&v=2&key=ABQIAAAAnyP-GOJDhG7H7ozm0RRsCBSiQ_eECfBHgA9cMSxRoMYUiueUzxSinT-_iJIghikcXgs_lmKq8_i5pQ HTTP/1.1
		#Host: maps.google.com
		#User-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11
		#Accept: */*
		#Accept-Language: de-de,de;q=0.8,en-us;q=0.5,en;q=0.3
		#Accept-Encoding: gzip,deflate
		#Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7
		#Keep-Alive: 300
		#Connection: keep-alive
		#Referer: http://www.informatik.uni-jena.de/~sack/test.htm
		#Cookie: PREF=ID=20f16b2c860a0bb0:TM=1200137261:LM=1200137261:S=KrXC-VU3vnlqGSna; NID=7=W2xBZleMgTCTpgpF1f_RQrvziIveCJt9_GK09Zx293A7hh_8R-ACdz7RxRc6hzWzrRyYfEfjLMA1jTObCLokylOVPlf_AkZ9iAvh2PLbgXVac5ahb1FOiuz6cu2kq1c7
		
		header = {
			"Host":"maps.google.com",
			"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11",
			"Accept":"*/*",
			"Accept-Language":"de-de,de;q=0.8,en-us;q=0.5,en;q=0.3",
			"Accept-Charset":"ISO-8859-1,utf-8;q=0.7,*;q=0.7",
			"Keep-Alive":"300",
			"Proxy-Connection":"keep-alive",
			"Referer": url}
		params = '?file=api&v=2&key='+ key
		body = ''
		self.sTargetUrl = "http://maps.google.com/maps"
		if self._request("GET",params,header, body)!=True:
			return False
		data = self.sData
		fName = file
		#TEMPFOLDER = "Q:\\temp\\"
		f = open(TEMPFOLDER + "maps1.js", 'wb')
		f.write(data)
		f.close()
		return self.sData
	
	def get_Maps_Copyright(self, url, key, spn, t, z, vp, ev, v):
		#GET /maps?spn=0.008115,0.021458&t=k&z=15&key=ABQIAAAAnyP-GOJDhG7H7ozm0RRsCBSiQ_eECfBHgA9cMSxRoMYUiueUzxSinT-_iJIghikcXgs_lmKq8_i5pQ&vp=50.927032,11.601734&ev=p&v=24 HTTP/1.1
		#Accept: */*
		#Referer: http://www.informatik.uni-jena.de/~sack/test.htm
		#Accept-Language: de
		#UA-CPU: x86
		#Accept-Encoding: gzip, deflate
		#User-Agent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; InfoPath.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)
		#Host: maps.google.com
		#Connection: Keep-Alive

		header = {
			"Host":"maps.google.com",
			"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11",
			"Accept":"*/*",
			"Accept-Language":"de-de,de;q=0.8,en-us;q=0.5,en;q=0.3",
			"Accept-Charset":"ISO-8859-1,utf-8;q=0.7,*;q=0.7",
			"Keep-Alive":"300",
			"Proxy-Connection":"keep-alive",
			"Referer":  url}
		params = '?spn='+ spn +'&t='+ t +'&z='+ z +'&key=' + key + '&vp=' + vp + '&ev=' + ev + '&v=' + v
		body = ''
		self.sTargetUrl = "http://maps.google.com/maps"
		if self._request("GET",params,header, body)!=True:
			return False
		#data = self.sData
		#fName = file
		#TEMPFOLDER = "Q:\\temp\\"
		#f = open(TEMPFOLDER + "maps1.js", 'wb')
		#f.write(data)
		#f.close()
		return self.sData 		

	def connect (self, targetserver, targetport=80):
		self.sTargetServer=targetserver
		self.sTargetPort = targetport
		#self.sTargetServer="inetproxy.global.bdfgroup.net"
		#self.sTargetPort = 8080
		self.connection = httplib.HTTPConnection(self.sTargetServer, self.sTargetPort)	
	
	def close(self):
		self.connection.close()
	
	def _request(self, action, params, header, body ):
		try:
			self.connection.request(action, self.sTargetUrl+params, body, header)
		except:
			print "Connection Error"
			return False
		response = self.connection.getresponse()
		if response.status != 200 and response.status != 302:
			print response.status, response.reason
			return False
		else:
			#print response.status, response.reason
			data = response.read()
			if data != '':
				self.sData = data
			else:
				return False
		return True
		
	def _Dump(self):
		name = datetime.datetime.now().strftime('%Y%m%d%H%M%S'+timezone)
		while os.path.exists(name+'.html'):
			name = datetime.datetime.now().strftime('%Y%m%d%H%M%S'+timezone)
		outfile= open(name+'.html','w+')
		outfile.write(self.sData)
		outfile.close()


class get_file(Thread):
	
	def __init__ (self,params,FileName,referer_url,imgBlocks="",function='',window='',result='',cache=1):
		Thread.__init__(self)
		self.parms = params[params.find('?'):len(params)]
		self.referer_url = referer_url
		self.filename = FileName
		self.path = ""
		self.sTargetUrl = params[0:params.find('?')]
		self.host = params[params.find('//')+2:params.find('/',params.find('//')+2)]
		self.tarname = FileName[0:FileName.rfind('\\')].replace('\\','_')
		self.tarfilename = FileName[FileName.find('\\')+1:len(FileName)]
		self.imgBlocks = imgBlocks
		self.function = function
		self.window = window
		self.result = result
		self.cache = cache
		self.connect(self.host)
		
	def run(self):	
		folders = self.tarname.split('_')
		try:
			os.mkdir(TEMPFOLDER + folders[0])
		except: pass
		try:
			os.mkdir(TEMPFOLDER + folders[0] + '\\' + folders[1])
		except: pass
		if not os.path.exists(TEMPFOLDER + self.filename) or self.cache == 0:
			#try:
			#	tar = tarfile.open(TEMPFOLDER + self.tarname + ".tar", "r")
			#	tar_file = tar.getmember(self.tarfilename)
			#	today = datetime.datetime.now()
			#	mtime = int(time.mktime(today.timetuple()))
			#	tar_file.mtime = mtime
			#	tar.extract(tar_file,TEMPFOLDER + self.tarname.replace('_','\\'))
			#except:
			header = {
				"Host": self.host,
				"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11",
				"Accept":"*/*",
				"Accept-Language":"de-de,de;q=0.8,en-us;q=0.5,en;q=0.3",
				"Accept-Charset":"ISO-8859-1,utf-8;q=0.7,*;q=0.7",
				"Keep-Alive":"300",
				"Proxy-Connection":"keep-alive",
				"Referer":  self.referer_url}
			params = self.parms
			body = ''
			
			if self._request("GET",params,header, body)!=True:
				return
			data = self.sData
			fName = file
			f = open(TEMPFOLDER + self.filename, 'wb')
			f.write(data)
			f.close()
			#	try:
			#		tar = tarfile.open(TEMPFOLDER + self.tarname + ".tar", "a")
			#	except:
			#		tar = tarfile.open(TEMPFOLDER + self.tarname + ".tar", "w")
			#	tar.add(TEMPFOLDER + self.filename, self.tarfilename)
			#	tar.close()
		else:
			f = TEMPFOLDER + self.filename
			today = datetime.datetime.now()
			atime = int(time.mktime(today.timetuple()))
			mtime = atime
			times = (atime,mtime)
			os.utime(f, times)
		if self.imgBlocks != "":
			self.path = TEMPFOLDER + self.filename
			self.imgBlocks.setVisible(True)
			self.imgBlocks.setImage(self.path)
		if self.function != '':
			self.function(self.result)
		return
	
	def _request(self, action, params, header, body ):
		try:
			self.connection.request(action, self.sTargetUrl+params, body, header)
		except:
			print "Connection Error"
			return False
		response = self.connection.getresponse()
		if response.status != 200:
			print response.status, response.reason
			return False
		else:
			#-print response.status, response.reason
			data = response.read()
			if data != '':
				self.sData = data
			else:
				return False
		return True	
	
	def connect (self, targetserver):
		self.sTargetServer=targetserver
		self.sTargetPort = "80"
		#self.sTargetServer="inetproxy.global.bdfgroup.net"
		#self.sTargetPort = 8080
		self.connection = httplib.HTTPConnection(self.sTargetServer, self.sTargetPort)	
		
class SRH(urllib2.HTTPRedirectHandler): 
	def http_error_302(self, req, fp, code, msg, headers): 
		result = urllib2.HTTPRedirectHandler.http_error_302( self, req, fp, code, msg, headers) 
		result.status = code 
		return result 
	def http_error_303(self, req, fp, code, msg, headers): 
		result = urllib2.HTTPRedirectHandler.http_error_302( self, req, fp, code, msg, headers) 
		result.status = code 
		return result 
		
