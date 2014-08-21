#
# Imports
#
#import os
#import md5
#import time
#import array
#import httplib
#import xbmc
#import xml.dom.minidom
#import xml.sax.saxutils as SaxUtils

import sys
import os
import xmlrpclib
from utilities import LOG, LOG_INFO, toOpenSubtitles_two
import md5
import time
import array
import httplib
import xbmc
import xml.dom.minidom
import xml.sax.saxutils as SaxUtils
import base64
import gui


#
# Integer => Hexadecimal
#
def dec2hex(n, l=0):
    # return the hexadecimal string representation of integer n
    s = "%X" % n
    if (l > 0) :
        while len(s) < l:
            s = "0" + s 
    return s

#
# Hexadecimal => integer
#
def hex2dec(s):
    # return the integer value of a hexadecimal string s
    return int(s, 16)

#
# String => Integer
#
def toInteger (string):
    try:
        return int( string )
    except :
        return 0

#
# Calculate MD5 partial video hash (not used)...
#
def calculateMD5VideoHash(filename):
    #
    # Check file...
    #
    if not os.path.isfile(filename) :
        return ""
     
    if os.path.getsize(filename) < 5 * 1024 * 1024 :
        return ""

    #
    # Calculate MD5 hash of the first 5 MB of video data...
    #
    f = open(filename, mode="rb")
    buffer = f.read( 5 * 1024 * 1024 )
    f.close()
    
    # Calculate MD5 hash...
    md5hash = md5.new()
    md5hash.update(buffer)
    
    # Return value (hex)
    return md5hash.hexdigest()

#
# Calculate Sublight video hash...
#
def calculateVideoHash(filename, isPlaying = True):
    #
    # Check file...
    #
    if not os.path.isfile(filename) :
        return ""
    
    if os.path.getsize(filename) < 5 * 1024 * 1024 :
        return ""

    #
    # Init
    #
    sum = 0
    hash = ""
    
    #
    # Byte 1 = 00 (reserved)
    #
    number = 0
    sum = sum + number
    hash = hash + dec2hex(number, 2) 
    
    #
    # Bytes 2-3 (video duration in seconds)
    #
    
    # Playing video...
    if isPlaying == True :
        seconds = int( xbmc.Player().getTotalTime() )
    # Selected video...
    else :
        player = xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER)
        player.play(filename)
        counter = 0
        while not player.isPlaying() and counter < 3 :
            time.sleep(1)
            counter = counter + 1
        seconds = int(player.getTotalTime())
        player.stop()
    
    # 
    sum = sum + (seconds & 0xff) + ((seconds & 0xff00) >> 8)
    hash = hash + dec2hex(seconds, 4)
    
    #
    # Bytes 4-9 (video length in bytes)
    #
    filesize = os.path.getsize(filename)
    
    sum = sum + (filesize & 0xff) + ((filesize & 0xff00) >> 8) + ((filesize & 0xff0000) >> 16) + ((filesize & 0xff000000) >> 24)
    hash = hash + dec2hex(filesize, 12) 
    
    #
    # Bytes 10-25 (md5 hash of the first 5 MB video data)
    #
    f = open(filename, mode="rb")
    buffer = f.read( 5 * 1024 * 1024 )
    f.close()
    
    md5hash = md5.new()
    md5hash.update(buffer)
    
    array_md5 = array.array('B')
    array_md5.fromstring(md5hash.digest())
    for b in array_md5 :
        sum = sum + b

    hash = hash + md5hash.hexdigest()
    
    #
    # Byte 26 (control byte)
    # 
    hash = hash + dec2hex(sum % 256, 2)
    hash = hash.upper()
    
    return hash

#
# Detect movie title and year from file name...
#
def getMovieTitleAndYear( filename ):
    name = os.path.splitext( filename )[0]

    cutoffs = ['dvdrip', 'dvdscr', 'cam', 'r5', 'limited',
               'xvid', 'h264', 'x264', 'h.264', 'x.264',
               'dvd', 'screener', 'unrated', 'repack', 'rerip', 
               'proper', '720p', '1080p', '1080i', 'bluray', 'hdtv']

    # Clean file name from all kinds of crap...
    for char in ['[', ']', '_', '(', ')','.','-']:
        name = name.replace(char, ' ')
    
    # if there are no spaces, start making beginning from dots...
#    if name.find('.') == -1:
#        name = name.replace('.', ' ')
#    if name.find('-') == -1:
#        name = name.replace('-', ' ')
    
    # remove extra and duplicate spaces!
    name = name.strip()
    while name.find('  ') != -1:
        name = name.replace('  ', ' ')
        
    # split to parts
    parts = name.split(' ')
    year = ""
    cut_pos = 256
    for part in parts:
        # check for year
        if part.isdigit():
            n = int(part)
            if n>1930 and n<2050:
                year = part
                if parts.index(part) < cut_pos:
                    cut_pos = parts.index(part)
                
        # if length > 3 and whole word in uppers, consider as cutword (most likelly a group name)
        if len(part) > 3 and part.isupper() and part.isalpha():
            if parts.index(part) < cut_pos:
                cut_pos = parts.index(part)
                
        # check for cutoff words
        if part.lower() in cutoffs:
            if parts.index(part) < cut_pos:
                cut_pos = parts.index(part)
        
    # make cut
    name = ' '.join(parts[:cut_pos])
    return name, year

#
# Convert from plugin language id => Sublight language
#
def toSublightLanguage(id):
    languages = { "0" : "None",
                  "alb" : "Albanian",
                  "ara" : "Arabic",
                  "arm" : "Belarusian",
                  "bos" : "BosnianLatin",
                  "bul" : "Bulgarian",
                  "cat" : "Catalan",
                  "chi" : "Chinese",
                  "hrv" : "Croatian",
                  "cze" : "Czech",
                  "dan" : "Danish",
                  "dut" : "Dutch",
                  "eng" : "English",
                  "est" : "Estonian",
                  "fin" : "Finnish",
                  "fre" : "French",
                  "ger" : "German",
                  "ell" : "Greek",
                  "heb" : "Hebrew",
                  "hin" : "Hindi",
                  "hun" : "Hungarian",
                  "ice" : "Icelandic",
                  "ind" : "Indonesian",
                  "23" : "Irish",
                  "ita" : "Italian",
                  "jpn" : "Japanese",
                  "kor" : "Korean",
                  "lav" : "Latvian",
                  "lit" : "Lithuanian",
                  "mac" : "Macedonian",
                  "nor" : "Norwegian",
                  "31" : "Persian",
                  "pol" : "Polish",
                  "por" : "Portuguese",
                  "pob" : "PortugueseBrazil",
                  "rum" : "Romanian",
                  "rus" : "Russian",
                  "scc" : "SerbianLatin",
                  "slo" : "Slovak",
                  "slv" : "Slovenian",
                  "spa" : "Spanish",
                  "41" : "SpanishArgentina",
                  "swe" : "Swedish",
                  "tha" : "Thai",
                  "tur" : "Turkish",
                  "ukr" : "Ukrainian",
                  "vie" : "Vietnamese",
                }
    return languages[ id ]
    
#
# SublightWebService class
#
class SublightWebService :
    def __init__ (self):
        self.SOAP_HOST                  = "www.sublight.si"
        self.SOAP_SUBTITLES_API_URL     = "/API/WS/Sublight.asmx"
        self.SOAP_SUBLIGHT_UTILITY_URL  = "/SublightUtility.asmx"
        
        self.LOGIN_ANONYMOUSLY_ACTION   = "http://www.sublight.si/LogInAnonymous4"
        self.SEARCH_SUBTITLES_ACTION    = "http://www.sublight.si/SearchSubtitles3"
        self.GET_DOWNLOAD_TICKET_ACTION = "http://www.sublight.si/GetDownloadTicket2"
        self.DOWNLOAD_BY_ID_ACTION      = "http://www.sublight.si/DownloadByID4"
        self.LOGOUT_ACTION              = "http://www.sublight.si/LogOut"
        
    #
    # Perform SOAP request...
    #
    def SOAP_POST (self, SOAPUrl, SOAPAction, SOAPRequestXML):
            # Handles making the SOAP request
            h = httplib.HTTPConnection(self.SOAP_HOST)
            headers = {
                'Host'           : self.SOAP_HOST,
                'Content-Type'   :'text/xml; charset=utf-8',
                'Content-Length' : len(SOAPRequestXML),
                'SOAPAction'     : '"%s"' % SOAPAction,
            }
            h.request ("POST", SOAPUrl, body=SOAPRequestXML, headers=headers)
            r = h.getresponse()
            d = r.read()
            h.close()
            
            ##if r.status != 200:
               ## LOG( LOG_INFO,'Error connecting: %s, %s' % (r.status, r.reason))
            return d
    
    #
    # LoginAnonymous3
    #
    def LogInAnonymous(self):
        # Build request XML...
        requestXML = """<?xml version="1.0" encoding="utf-8"?>
                        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" 
                                       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                                       xmlns:xsd="http://www.w3.org/2001/XMLSchema">
                          <soap:Body>
                            <LogInAnonymous4 xmlns="http://www.sublight.si/">
                              <clientInfo>
				<ClientId>OpenSubtitles_OSD</ClientId>
				<ApiKey>b44bc9b9-91f4-45be-8a49-c9b18ca86566</ApiKey>
			      </clientInfo>
                            </LogInAnonymous4>
                          </soap:Body>
                        </soap:Envelope>"""
        
        # Call SOAP service...
        resultXML = self.SOAP_POST (self.SOAP_SUBTITLES_API_URL, self.LOGIN_ANONYMOUSLY_ACTION, requestXML)
        
        # Parse result
        resultDoc = xml.dom.minidom.parseString(resultXML)
        xmlUtils  = XmlUtils()
        sessionId = xmlUtils.getText( resultDoc, "LogInAnonymous4Result" )
        
        # Return value
        return sessionId


    #
    # LogOut
    #
    def LogOut(self, sessionId):
        # Build request XML...
        requestXML = """<?xml version="1.0" encoding="utf-8"?>
                        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" 
                                       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                                       xmlns:xsd="http://www.w3.org/2001/XMLSchema">
                          <soap:Body>
                            <LogOut xmlns="http://www.sublight.si/">
                              <session>%s</session>
                            </LogOut>
                          </soap:Body>
                        </soap:Envelope>""" % ( sessionId )
                          
        # Call SOAP service...
        resultXML = self.SOAP_POST (self.SOAP_SUBTITLES_API_URL, self.LOGOUT_ACTION, requestXML)
        
        # Parse result
        resultDoc = xml.dom.minidom.parseString(resultXML)
        xmlUtils  = XmlUtils()
        result    = xmlUtils.getText( resultDoc, "LogOutResult" )
        
        # Return value
        return result
    
    #
    # SearchSubtitles
    #
    def SearchSubtitles(self, sessionId, videoHash, title, year, season, episode,language1, language2, language3):
        title = SaxUtils.escape(title)    
        # Build request XML...
        requestXML = """<?xml version="1.0" encoding="utf-8"?>
                        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
                                       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                                       xmlns:xsd="http://www.w3.org/2001/XMLSchema">
                          <soap:Body>
                            <SearchSubtitles3 xmlns="http://www.sublight.si/">
                              <session>%s</session>
                              <videoHash>%s</videoHash>
                              <title>%s</title>
                              %s
                              %s
                              %s
                              <languages>
                                %s
                                %s
                                %s
                              </languages>
                              <genres>
                                <Genre>Movie</Genre>
                                <Genre>Cartoon</Genre>
                                <Genre>Serial</Genre>
                                <Genre>Documentary</Genre>
                                <Genre>Other</Genre>
                                <Genre>Unknown</Genre>
                              </genres>
                              <rateGreaterThan xsi:nil="true" />
                            </SearchSubtitles3>
                          </soap:Body>
                        </soap:Envelope>""" % ( sessionId, 
                                                videoHash,
                                                title,
                                                ( "<year>%s</year>" % year, "<year xsi:nil=\"true\" />" ) [ year == "" ],
						( "<season>%s</season>" % season, "<season xsi:nil=\"true\" />" ) [ season == "" ],                                                  
						( "<episode>%s</episode>" % episode, "<episode xsi:nil=\"true\" />" ) [ episode == "" ],
						  "<SubtitleLanguage>%s</SubtitleLanguage>" % language1,
                                                ( "<SubtitleLanguage>%s</SubtitleLanguage>" % language2, "" ) [ language2 == "None" ],
                                                ( "<SubtitleLanguage>%s</SubtitleLanguage>" % language3, "" ) [ language3 == "None" ] )
        
        # Call SOAP service...
        resultXML = self.SOAP_POST (self.SOAP_SUBTITLES_API_URL, self.SEARCH_SUBTITLES_ACTION, requestXML)
        # Parse result
        resultDoc = xml.dom.minidom.parseString(resultXML)
        xmlUtils  = XmlUtils() 
        result    = xmlUtils.getText(resultDoc, "SearchSubtitles3Result")
        subtitles = []      
        if (result == "true") :
            # Releases...
            releases = dict()
            releaseNodes = resultDoc.getElementsByTagName("Release")
            if releaseNodes != None :
                for releaseNode in releaseNodes :
                    subtitleID  = xmlUtils.getText( releaseNode, "SubtitleID" )
                    releaseName = xmlUtils.getText( releaseNode, "Name" )
                    if releaseName > "" :
                        releases[ subtitleID ] = releaseName
            # Subtitles...
            subtitleNodes = resultDoc.getElementsByTagName("Subtitle")
            for subtitleNode in subtitleNodes:
                title         = xmlUtils.getText( subtitleNode, "Title" )
                year          = xmlUtils.getText( subtitleNode, "Year" )
                try:
                    release   = releases.get( subtitleID, ("%s (%s)" % ( title, year  ) ) )
                except :
                    release   = "%s (%s)" % ( title, year )
                language      = xmlUtils.getText( subtitleNode, "Language" )
                subtitleID    = xmlUtils.getText( subtitleNode, "SubtitleID" )
                mediaType     = xmlUtils.getText( subtitleNode, "MediaType" )
                numberOfDiscs = xmlUtils.getText( subtitleNode, "NumberOfDiscs" ) 
                downloads     = xmlUtils.getText( subtitleNode, "Downloads" )
                isLinked      = xmlUtils.getText( subtitleNode, "IsLinked" )
                rate          = float(xmlUtils.getText( subtitleNode, "Rate" ))              

                subtitles.append( { "title" : title, "year" : year, "release" : release, "language" : language, "subtitleID" : subtitleID, "mediaType" : mediaType, "numberOfDiscs" : numberOfDiscs, "downloads" : downloads, "isLinked" : isLinked, "rate" : rate } )            
            
        # Return value
        return subtitles        
    
    #
    # GetDownloadTicket
    #
    def GetDownloadTicket(self, sessionID, subtitleID):
        # Build request XML...
        requestXML = """<?xml version="1.0" encoding="utf-8"?>
                        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" 
                                       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                                       xmlns:xsd="http://www.w3.org/2001/XMLSchema">
                          <soap:Body>
                            <GetDownloadTicket2 xmlns="http://www.sublight.si/">
                              <session>%s</session>
                              <id>%s</id>
                            </GetDownloadTicket2>
                          </soap:Body>
                        </soap:Envelope>""" % ( sessionID, subtitleID )
                        
        # Call SOAP service...
        resultXML = self.SOAP_POST (self.SOAP_SUBTITLES_API_URL, self.GET_DOWNLOAD_TICKET_ACTION, requestXML)
        
        # Parse result
        resultDoc = xml.dom.minidom.parseString(resultXML)
        xmlUtils  = XmlUtils()
        result    = xmlUtils.getText( resultDoc, "GetDownloadTicket2Result" )
        
        ticket = ""
        if result == "true" :
            ticket = xmlUtils.getText( resultDoc, "ticket" )
            que    = xmlUtils.getText( resultDoc, "que" )
            
        # Return value
        return ticket, que
    
    #
    # DownloadByID4 
    #
    def DownloadByID(self, sessionID, subtitleID, ticketID):
        # Build request XML...
        requestXML = """<?xml version="1.0" encoding="utf-8"?>
                        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" 
                                       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                                       xmlns:xsd="http://www.w3.org/2001/XMLSchema">
                          <soap:Body>
                            <DownloadByID4 xmlns="http://www.sublight.si/">
                              <sessionID>%s</sessionID>
                              <subtitleID>%s</subtitleID>
                              <codePage>1250</codePage>
                              <removeFormatting>false</removeFormatting>
                              <ticket>%s</ticket>
                            </DownloadByID4>
                          </soap:Body>
                        </soap:Envelope>""" % ( sessionID, subtitleID, ticketID )

        # Call SOAP service...
        resultXML = self.SOAP_POST (self.SOAP_SUBTITLES_API_URL, self.DOWNLOAD_BY_ID_ACTION, requestXML)
        
        # Parse result
        resultDoc = xml.dom.minidom.parseString(resultXML)
        xmlUtils  = XmlUtils()
        result    = xmlUtils.getText( resultDoc, "DownloadByID4Result" )
        
        base64_data = ""
        if result == "true" :
            base64_data = xmlUtils.getText( resultDoc, "data" )
        
        # Return value
        return base64_data
        
#
#
#
class XmlUtils :
    def getText (self, nodeParent, childName ):
        # Get child node...
        node = nodeParent.getElementsByTagName( childName )[0]
        
        if node == None :
            return None
        
        # Get child text...
        text = ""
        for child in node.childNodes:
            if child.nodeType == child.TEXT_NODE :
                text = text + child.data
        return text
