#############################################################################
#
# Navi-X Playlist browser (additional library functions)
# by rodejo (rodejo16@gmail.com)
#############################################################################

from string import *
import sys, os.path
import urllib
import urllib2
import re, random, string
import xbmc, xbmcgui, xbmcaddon
import re, os, time, datetime, traceback
import shutil
import zipfile
import socket
from settings import *

try: Emulating = xbmcgui.Emulating
except: Emulating = False

dialog=xbmcgui.DialogProgress()

######################################################################
# Description: Playlist item class. 
######################################################################
#class CMediaItem:
#    def __init__(self, id='0', type='unknown', version=plxVersion, name='', thumb='default', URL=''):
#        self.id = id        #identifier
#        self.type = type    #type (playlist, image, video, audio, text)
#        self.version = version #playlist version
#        self.name = name    #name as displayed in list view
#        self.thumb = thumb  #URL to thumb image or 'default'
#        self.URL = URL      #URL to playlist entry
######################################################################
class CMediaItem:
    def __init__(self, \
                  type='unknown', \
                  version=plxVersion, \
                  name='', \
                  description='', \
                  date='', \
                  thumb='default', \
                  icon='default', \
                  URL='', \
                  DLloc='', \
                  player='default', \
                  processor='', \
                  playpath='', \
                  swfplayer='', \
                  pageurl='', \
                  background='default'):
        self.type = type    #(required) type (playlist, image, video, audio, text)
        self.version = version #(optional) playlist version
        self.name = name    #(required) name as displayed in list view
        self.description = description    #(optional) description of this item
        self.date = date    #(optional) release date of this item (yyyy-mm-dd)
        self.thumb = thumb  #(optional) URL to thumb image or 'default'
        self.icon = icon  #(optional) URL to icon image or 'default'
        self.URL = URL      #(required) URL to playlist entry
        self.DLloc = DLloc  #(optional) Download location
        self.player = player #(optional) player core to use for playback
        self.processor = processor #(optional) URL to mediaitem processing server 
        self.playpath = playpath #(optional) 
        self.swfplayer = swfplayer #(optional)
        self.pageurl = pageurl #(optional)
        self.background = background #(optional) background image
        
######################################################################
# Description: Playlist item class. 
######################################################################
class CHistorytem:
    def __init__(self, index=0, mediaitem=CMediaItem()):
        self.index = index
        self.mediaitem = mediaitem

#class CHistorytem2:
#    def __init__(self, URL='', index=0, type='unknown'):
#        self.URL = URL        
#        self.index = index
#        self.type = type
 

######################################################################
# Description: Get the file extension of a URL
# Parameters : filename=local path + file name
# Return     : -
######################################################################
def getFileExtension(filename):
    ext_pos = filename.rfind('.') #find last '.' in the string
    if ext_pos != -1:
        ext_pos2 = filename.rfind('?', ext_pos) #find last '.' in the string
        if ext_pos2 != -1:
            return filename[ext_pos+1:ext_pos2]
        else:
            return filename[ext_pos+1:]
    else:
        return ''

######################################################################
# Description: Get the socket timeout time
# Parameters : -
# Return     : -
######################################################################
def socket_getdefaulttimeout():
    return socket.getdefaulttimeout()

######################################################################
# Description: Set the socket timeout time
# Parameters : time in seconds
# Return     : -
######################################################################
def socket_setdefaulttimeout(url_open_timeout):
    if platform == "xbox":
        socket.setdefaulttimeout(url_open_timeout)
        
######################################################################
# Description: Trace function for debugging
# Parameters : string: text string to trace
# Return     : -
######################################################################
def Trace(string):
    f = open(RootDir + "trace.txt", "a")
    f.write(string + '\n')
    f.close()

    
######################################################################
# Description: Display popup error message
# Parameters : string: text string to trace
# Return     : -
######################################################################
def Message(string):
    dialog = xbmcgui.Dialog()
    dialog.ok("Error", string)  
          
######################################################################
# Description: Retrieve the platform Navi-X is running on.
# Parameters : -
# Return     : string containing the platform.
######################################################################  
def get_system_platform():
    platform = "unknown"
    if xbmc.getCondVisibility( "system.platform.linux" ):
        platform = "linux"
    elif xbmc.getCondVisibility( "system.platform.xbox" ):
        platform = "xbox"
    elif xbmc.getCondVisibility( "system.platform.windows" ):
        platform = "windows"
    elif xbmc.getCondVisibility( "system.platform.osx" ):
        platform = "osx"
#    Trace("Platform: %s"%platform)
    return platform

######################################################################
# Description: Retrieve remote HTML.
# Parameters : URL
# Return     : string containing the page contents.
######################################################################  
##def get_HTML(url):
##    headers = { 'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.4) Gecko/2008102920 Firefox/3.0.4',
##                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
##    req = urllib2.Request(url=url, headers=headers)
##    response = urllib2.urlopen(req)
##    link=response.read()
##    response.close()
##    return link   
##
def get_HTML(url,referer='',cookie=''):
    headers = { 'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.4) Gecko/2008102920 Firefox/3.0.4',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Referer': referer,
                'Cookie': cookie}
    try:
        oldtimeout=socket_getdefaulttimeout()
        socket_setdefaulttimeout(url_open_timeout)
        req = urllib2.Request(url=url, headers=headers)
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
    except IOError:         
        link = ""
    
    socket_setdefaulttimeout(oldtimeout)
    
    return link
     
######################################################################
# Description: Retrieve remote information.
# Parameters : URL, retrieval parameters
# Return     : string containing the page contents.
######################################################################  
def getRemote(url,args={}):
    rdefaults={
        'agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.4) Gecko/2008102920 Firefox/3.0.4',
        'referer': '',
        'cookie': '',
        'method': 'get',
        'action': 'read',
        'postdata': '',
        'headers': {}
    }

    for ke in rdefaults:
        try:
            args[ke]
        except KeyError:
            args[ke]=rdefaults[ke]

    if url.find(nxserver_URL) != -1:
        from CServer import nxserver
        if args['cookie']>'':
            args['cookie']=args['cookie']+'; '
        args['cookie']=args['cookie']+'; nxid='+nxserver.user_id

    try:
        hdr={'User-Agent':args['agent'], 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Referer':args['referer'], 'Cookie':args['cookie']}
    except:
        print "Unexpected error:", sys.exc_info()[0]

    for ke in args['headers']:
        try:
            hdr[ke]=args['headers'][ke]
        except:
            print "Unexpected error:", sys.exc_info()[0]

    try:
        if args['method'] == 'get':
            req=urllib2.Request(url=url, headers=hdr)
        else:
            req=urllib2.Request(url, args['postdata'], hdr)

        cookieprocessor=urllib2.HTTPCookieProcessor()
        opener=urllib2.build_opener(cookieprocessor)
        urllib2.install_opener(opener)
        response=urllib2.urlopen(req)

        cookies={}
        for c in cookieprocessor.cookiejar:
            cookies[c.name]=c.value

        oret={
      	    'headers':response.info(),
      	    'geturl':response.geturl(),
      	    'cookies':cookies
        }
        if args['action'] == 'read':
            oret['content']=response.read()
        
        rkeys=['content','geturl']
        for rkey in rkeys:
            try:
                oret[rkey]
            except KeyError:
                oret[rkey]=''
        rkeys=['cookies','headers']
        for rkey in rkeys:
            try:
                oret[rkey]
            except KeyError:
                oret[rkey]={}

        response.close()
    except IOError:         
        oret = {
            'content': str(sys.exc_info()[0]),
      	    'headers':'',
      	    'geturl':'',
      	    'cookies':''
        }
    except ValueError:
        print "*** Value Error *** "+str(sys.exc_info()[0])
        oret = {
            'content': str(sys.exc_info()[0]),
      	    'headers':'',
      	    'geturl':'',
      	    'cookies':''
        }

    return oret

######################################################################
# Description: Retrieve NIPL cookies, or "nookies" for specific
#              processor URL. Also handles expiration
# Parameters : URL
# Return     : dictionary containing values of non-expired nookies
######################################################################  
def NookiesRead(url):
    pfilename=ProcessorLocalFilename(url)
    if pfilename=='':
        return {}
    nookiefile=nookieCacheDir+pfilename
    if not os.path.exists(nookiefile):
        return {}
    try:
        f=open(nookiefile, 'r')
    except IOError:
        return {}

    re_parse=re.compile('^(\d+):([^=]+)=(.*)$');
    now=time.time()
    oret={};
    for line in f:
        if line=='':
            continue
        match=re_parse.search(line)
        exp=match.group(1)
        #key='nookie.'+match.group(2)
        key=match.group(2)
        val=match.group(3)
        f_exp=float(exp)
        if f_exp>0 and f_exp<now:
            continue
        oret[key]={'value':val,'expires':exp}
    f.close()
    return oret

######################################################################
# Description: Store nookie for specific processor URL
# Parameters : URL, name, value, expires
# Notes      : expiration format: 0, [n](m|h|d)
#                 0: never, 5m: 5 minutes, 1h: 1 hour, 2d: 2 days
# Return     : -
######################################################################  
def NookieSet(url, name, value, expires):
    pfilename=ProcessorLocalFilename(url)
    if pfilename=='':
        return
    nookiefile=nookieCacheDir+pfilename

    nookies=NookiesRead(url)

    # set expiration timestamp
    if expires=='0':
        int_expires=0
    else:
        now=int(time.time())
        re_exp=re.compile('^(\d+)([mhd])$');
        match=re_exp.search(expires)
        mult={'m':60, 'h':3600, 'd':86400}
        int_expires=now + int(match.group(1)) * mult[match.group(2)]

    # set specified nookie
    nookies[name]={'value':value,'expires':str(int_expires)}

    # compile all non-empty nookies into output string
    str_out=''
    for ke in nookies:
        if nookies[ke]['value']=='':
            continue
        str_out=str_out+nookies[ke]['expires']+':'+ke+'='+nookies[ke]['value']+"\n"
    if str_out>'':
        f=open(nookiefile, 'w')
        f.write(str_out)    
        f.close()
    else:
        os.remove(nookiefile)
    
######################################################################
# Description: Generate unique filename based on processor URL
# Parameters : URL
# Return     : string containing local filename
######################################################################  
def ProcessorLocalFilename(url):
    re_procname=re.compile('([^/]+)$')
    match=re_procname.search(url)
    if match is None:
        return ''

    fn_raw="%X"%(reduce(lambda x,y:x+y, map(ord, url))) + "~" + match.group(1)
    return fn_raw[:42]

######################################################################
# Description: Creates an addon.xml file (needed for Dharma)
# Parameters : name: shortcut name
#            : path: short pathname in the scripts folder
# Return     : -
######################################################################
def CreateAddonXML(name, path):
    sum = 0
    #calculate hash of name
    for i in range(len(name)):
        sum = sum + (ord(name[i]) * i)
    sum_str = str(sum)

    try:
        f=open(initDir + 'addon.xml', 'r')
        data = f.read()
        data = data.splitlines()
        f.close()
        
        f=open(path + 'addon.xml', 'w')
        for m in data:
            line = m
            if m.find("name=") != -1:
                line = line + '"' + name + '"'
            elif m.find("id=") != -1:
                line = line + '"scrip.navi-x' + sum_str + '"' 
            f.write(line + '\n')
        f.close()     
    except IOError:
        pass

 
######################################################################
# Description: Controls the info text label on the left bottom side
#              of the screen.
# Parameters : folder=path to local folder
# Return     : -
######################################################################
def SetInfoText(text='', window=0, setlock=False):      
    if text == '':
        dialog.close()
     
    if text != '':
        try:
           dialog.create("Loading", text)
        except:
           dialog.update("Loading",text)


        
#retrieve the platform.
platform = get_system_platform()

