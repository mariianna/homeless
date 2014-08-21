#
# Imports
#
import os
import sys
import xbmc
import xbmcgui
import xbmcplugin
import urllib
import elementtree.ElementTree as ElementTree
from microsoft_pdc_utils import HTTPCommunicator

#
# Main class
#
class Main:
    #
    # Init
    #
    def __init__( self ) :
        #
        # Constants
        #
        self.DEBUG         = False
        
        #
        # Parameters
        #
        params = dict(part.split('=', 1) for part in sys.argv[ 2 ][ 1: ].split('&'))
        self.trackId = urllib.unquote_plus( params[ "category" ] )
        
        #
        # Settings
        #
        self.english      = xbmc.Language (os.getcwd(), "English") 
        self.video_format = (self.english.getLocalizedString(30301), 
                             self.english.getLocalizedString(30302), 
                             self.english.getLocalizedString(30303),
                             self.english.getLocalizedString(30304)) [int( xbmcplugin.getSetting ("video_format") )]        
        
        
        
        #
        # Get the video sessions...
        #
        self.getSessions()
    
    #
    # Get videos...
    #
    def getSessions( self ) :
        # 
        # Get XML...
        #         
        httpCommunicator = HTTPCommunicator()
        url              = "http://videoak.microsoftpdc.com/pdc_schedule/Schedule.xml"
        xmlData          = httpCommunicator.get( url )
                          
        # Debug
        if (self.DEBUG) :
            f = open(os.path.join( xbmc.translatePath( "special://profile" ), "plugin_data", "video", sys.modules[ "__main__" ].__plugin__, "sessions.xml" % self.current_page), "w")
            f.write( htmlData )
            f.close()

        #
        # Parse response...
        # 
        rootElement     = ElementTree.fromstring( xmlData, ElementTree.XMLParser(encoding="utf-8") )
        
        #
        # Get speakers...
        #
        speakers = {}
        speakerElements = rootElement.findall("Speakers/Speaker")
        for speakerElement in speakerElements :
            speakerId    = speakerElement.get("id")
            speakerName  = speakerElement.get("FullName")
            speakerAbout = speakerElement.text
            if speakerAbout == None :
                speakerAbout = "" 
            speakers[ speakerId ] = { "Name" : speakerName, "About" : speakerAbout }
        
        #
        # Get sessions...
        #
        sessionElements = rootElement.findall("Sessions/Session")
        
        for sessionElement in sessionElements :
            title     = sessionElement.find("FullTitle").text
            thumbnail = sessionElement.get("ThumbnailUrl")
            trackId   = sessionElement.get("TrackId")
            
            # Filter by TrackId (session category)...
            if self.trackId != "" and self.trackId != trackId :
                continue
            
            # Pick preferred video format...
            videos = []
            downloadableContentElement = sessionElement.find("DownloadableContent")
            contentElements            = downloadableContentElement.findall("Content")
            for contentElement in contentElements :
                contentTitle = contentElement.get("Title")
                video        = contentElement.get("Url")
                
                if contentTitle.endswith( self.video_format ) :
                    videos.insert(0, video)
                else :
                    videos.append(video)
            
            # No videos? Skip entry...
            if len( videos ) == 0 :
                continue
            else :
                video = videos[0]
            
            # Presenters (speakers)...
            presenters = []
            presenterElements = sessionElement.findall("Presenters/Presenter")
            for presenterElement in presenterElements :
                presenterId = presenterElement.get("id")
                presenter   = speakers[ presenterId ]
                if presenter != None :
                    presenters.append(presenter)            
            
            # Genre (speakers)...
            director = ""
            for presenter in presenters :
                if director != "" :
                    director = director + ", " + presenter[ "Name" ] 
                else :
                    director = director + presenter[ "Name" ]
                        
            # Plot...
            plot = sessionElement.find("FullDescription").text.strip() + os.linesep
            for presenter in presenters :
                plot = plot + os.linesep             \
                     + "* " + presenter[ "Name"  ]
                if presenter[ "About" ] != None and presenter[ "About" ] != "" :
                    plot = plot + os.linesep + presenter[ "About" ] + os.linesep                     
                        
            # Add list entry...
            listitem        = xbmcgui.ListItem( title, iconImage="DefaultVideo.png", thumbnailImage=thumbnail )
            listitem.setInfo( "video", { "Title" : title, "Studio" : "Microsoft PDC", "Director" : director, "Plot" : plot } )
            url             = "%s?action=play&video=%s" % ( sys.argv[ 0 ], urllib.quote_plus( video ) )
            xbmcplugin.addDirectoryItem( handle=int(sys.argv[ 1 ]), url=url, listitem=listitem, isFolder=False)            

        # Disable sorting...
        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
        
        # End of directory...
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )
