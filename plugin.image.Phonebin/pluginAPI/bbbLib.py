"""
 Supporting shared functions for Plugin
"""

import os, sys, os.path, re
from urllib import quote_plus, unquote_plus, urlcleanup, FancyURLopener, urlretrieve
from string import find
import codecs
import xbmc, xbmcgui

__plugin__ = sys.modules[ "__main__" ].__plugin__

global dialogProgress
dialogProgress = xbmcgui.DialogProgress()

#################################################################################################################
def log(msg, loglevel=xbmc.LOGDEBUG):
	try:
		xbmc.log("[%s]: %s" % (__plugin__, msg), loglevel)
	except: pass
log("Module: %s loaded!" % __name__)

#################################################################################################################
def logError(msg=""):
	log("ERROR: %s %s" % (msg, sys.exc_info()[ 1 ]))

#################################################################################################################
def messageOK(title='', line1='', line2='',line3=''):
	xbmcgui.Dialog().ok(title ,line1,line2,line3)

#################################################################################################################
def handleException(msg=''):
	import traceback
	traceback.print_exc()
	messageOK(__plugin__ + " ERROR!", msg, str(sys.exc_info()[ 1 ]) )

#################################################################################################################
def loadFileObj( filename, dataType={} ):
	log( "loadFileObj() " + filename)
	try:
		file_handle = open( xbmc.translatePath(filename), "r" )
		loadObj = eval( file_handle.read() )
		file_handle.close()
	except:
		loadObj = None
	return loadObj

#################################################################################################################
def saveFileObj( filename, saveObj ):
	log( "saveFileObj() " + filename)
	try:
		file_handle = open( xbmc.translatePath(filename), "w" )
		file_handle.write( repr( saveObj ) )
		file_handle.close()
		return True
	except:
		handleException( "_save_file_obj()" )
		return False

#################################################################################################################
# delete a single file
def deleteFile(filename):
	try:
		os.remove(xbmc.translatePath(filename))
		log("deleteFile() deleted: " + filename)
	except: pass

#################################################################################################################
def encodeText(text):
	""" convert chars to make suitable for url """
#	return repr( quote_plus(text.replace("'", '"')) )
	try:
		return  repr( quote_plus(text.replace("'", '"').encode('utf-8')) )
	except:
		logError("encodeText()")
	return repr(text.replace("'", '"'))


#################################################################################################################
# if success: returns the page given in url as a string
# else: return -1 for Exception None for HTTP timeout, '' for empty page otherwise page data
#################################################################################################################
def fetchURL(url, file='', params=None, headers={}, isBinary=False, encodeURL=True):
	log("> bbbLib.fetchURL() %s isBinary=%s encodeURL=%s" % (url, isBinary, encodeURL))
	if encodeURL:
		safe_url = quote_plus(url,'/:&?=+#@')
	else:
		safe_url = url

	success = False
	data = None
	if not file:
		# create temp file
		file = xbmc.translatePath( "special://temp/temp.html" )

	# remove destination file if exists already
	deleteFile(file)

	# fetch from url
	try:
		opener = FancyURLopener()

		# add headers if supplied
		if not headers.has_key('User-Agent') and not headers.has_key('User-agent'):
			headers['User-Agent'] = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
		for name, value  in headers.items():
			opener.addheader(name, value)

		fn, resp = opener.retrieve(safe_url, file, data=params)
#		print fn, resp

		content_type = resp.get("Content-Type",'').lower()
		# fail if expecting an image but not correct type returned
		if isBinary and (find(content_type,"text") != -1):
			raise "Not Binary"

		opener.close()
		del opener
		urlcleanup()
	except IOError, errobj:
		ErrorCode(errobj)
	except "Not Binary":
		log("Returned Non Binary content")
	except:
		handleException("fetchURL()")
	else:
		if not isBinary:
			data = readFile(file)		# read retrieved file
			if (not data) or ( "404 Not Found" in data ):
				data = ''
		else:
			data = fileExist(file)		# check image file exists

	if not data:
		deleteFile(file)
	else:
		success = True

	log( "< fetchURL success=%s" % success)
	return data

#################################################################################################################
def ErrorCode(e):
	log("> ErrorCode()")
	print "except=%s" % e
	if hasattr(e, 'code'):
		code = e.code
	else:
		code = ''
		if not isinstance(e, str):
			try:
				code = e[0]
			except:
				code = 'Unknown'
	title = 'Error, Code: %s' % code

	if hasattr(e, 'reason'):
		txt = e.reason
	else:
		try:
			txt = e[1]
		except:
			txt = 'Unknown reason'
	messageOK(title, str(txt))
	log("< ErrorCode()")

#################################################################################################################
def readFile(filename):
	try:
		f = xbmc.translatePath(filename)
		log("bbbLib.readFile() " + f)
		return file(f).read()
	except:
		return ""

#################################################################################################################
def fileExist(filename):
	try:
		osFN = xbmc.translatePath(filename)
		if os.path.isfile(osFN) and os.path.getsize(osFN) > 0:
			return True
	except:
		print str( sys.exc_info()[ 1 ] )
	return False

#################################################################################################################
def searchRegEx(data, regex, flags=re.MULTILINE+re.IGNORECASE+re.DOTALL, firstMatchOnly=True):
	try:
		value = ""
		match = re.search(regex, data, flags)
		if match:
			if firstMatchOnly:
				value = match.group(1)
			else:
				value = match.groups()
	except:
		value = ""
	return value

#################################################################################################################
def findAllRegEx(data, regex, flags=re.MULTILINE+re.IGNORECASE+re.DOTALL):
	try:
		matchList = re.compile(regex, flags).findall(data)
	except:
		matchList = []

	if matchList:
		sz = len(matchList)
	else:
		sz = 0
	log("findAllRegEx() matches=%s" % sz)
	return matchList

##############################################################################################################    
def playMedia(source, li=None, windowed=False):
	log("> playMedia()")
	isPlaying = False

	try:
		if li:
			log("player source fn/url with li")
			xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).play(source, li, windowed)
		else:
			log("player source PlayList")
			xbmc.Player().play(source, windowed=windowed)
		isPlaying = xbmc.Player().isPlaying()
	except:
		traceback.print_exc()
		log('xbmc.Player().play() failed trying xbmc.PlayMedia() ')
		try:
			cmd = 'xbmc.PlayMedia(%s)' % source
			xbmc.executebuiltin(cmd)
			isPlaying = True
		except:
			handleException('playMedia()')
	log("< playMedia() " % isPlaying)
	return isPlaying

