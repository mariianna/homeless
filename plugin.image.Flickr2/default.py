##############################################################################
#
# Flickr2 - Plugin for XBMC
# http://www.flickr.com
#
# Version 1.2
# 
# Coding by Dan Dar3 
# http://dandar3.blogspot.com
#
#
# Credits:
#   * Team XBMC @ XBMC.org                                    [ http://xbmc.org/ ]
#   * Sybren Stüvel <sybren@stuvel.eu> - FlickrAPI 1.3-beta0  [ http://stuvel.eu/projects/flickrapi ]
#   * Bod Redivi <bob@redivi.com>      - simplejson 2.0.9     [ http://undefined.org/python/#simplejson ]
# Changes:
#
#

# main imports
import sys
import os
import time
import xbmcgui
import xbmcplugin

# plugin constants
__plugin__  = "Flickr2"
__author__  = "Dan Dar3"
__url__     = "http://dandar3.blogspot.com"
__date__    = "Saturday, 14 August 2010"
__version__ = "1.2"

#
rootDir  = os.getcwd()
resDir   = xbmc.translatePath(os.path.join(rootDir, 'resources'))
libDir   = xbmc.translatePath(os.path.join(resDir,  'lib'))
imgDir   = xbmc.translatePath(os.path.join(resDir,  'images'))

# imports
sys.path.append (libDir)

import flickrapi
#import elementtree
import simplejson

#
# Main class
#
class Main:
    def __init__(self):
        #
        #
        #
        xbmc.log( "[PLUGIN] %s v%s (%s)" % ( __plugin__, __version__, __date__ ), xbmc.LOGNOTICE )
        
        #
        # Init
        #
        self.DEBUG           = ( True, False ) [ xbmcplugin.getSetting ("debug_log") == "false" ]
        self.API_KEY         = "c809cc574630cae97e52108079ab3f47"
        self.ENGLISH         = xbmc.Language (os.getcwd(), "English")
        self.PREF_PAGE_SIZE  = int (xbmcplugin.getSetting ("page_size")) + 1
        self.PREF_PHOTO_SIZE = (self.ENGLISH.getLocalizedString(30301), self.ENGLISH.getLocalizedString(30302), self.ENGLISH.getLocalizedString(30303), self.ENGLISH.getLocalizedString(30304), self.ENGLISH.getLocalizedString(30305)) [int(xbmcplugin.getSetting("photo_size"))]
        
        #
        # Parameters
        #
        if sys.argv[ 2 ] == "" :
            current_page = 1
        else :
            params = dict(part.split('=') for part in sys.argv[ 2 ][ 1: ].split('&'))
            current_page    = int ( params.get( "page" ) )

        #
        # Get the "interestigness" photos for a date...
        #
        if self.DEBUG : start_time = time.time()
        self.getInterestignessPhotos( current_page )
        if self.DEBUG : xbmc.log("" , xbmc.LOGNOTICE )
        if self.DEBUG : xbmc.log("[Flickr2]  Total execution time = %f" % ( time.time() - start_time ), xbmc.LOGNOTICE )

    #
    # Interestigness
    #
    def getInterestignessPhotos (self, p_page) :
        # Debug
        if self.DEBUG :
            xbmc.log( "[Flickr2]  PREF_PAGE_SIZE  = %u" % self.PREF_PAGE_SIZE , xbmc.LOGNOTICE )
            xbmc.log( "[Flickr2]  PREF_PHOTO_SIZE = %s" % self.PREF_PHOTO_SIZE, xbmc.LOGNOTICE )
            xbmc.log( "[Flickr2]  PAGE            = %u" % p_page              , xbmc.LOGNOTICE )

        # Interestigness
        # http://api.flickr.com/services/rest/?method=flickr.interestingness.getList&api_key=c809cc574630cae97e52108079ab3f47&page=1&per_page=5&extras=original_format&date=2009-02-19
        #
        # Sizes
        # http://api.flickr.com/services/rest/?method=flickr.photos.getSizes&api_key=c809cc574630cae97e52108079ab3f47&photo_id=3292671575

        flickr = flickrapi.FlickrAPI(self.API_KEY)
        rsp = flickr.interestingness_getList(page=p_page, per_page=self.PREF_PAGE_SIZE, format="json")
        
        # Debug
        if self.DEBUG :
            xbmc.log( ""                          , xbmc.LOGNOTICE )
            xbmc.log( "[Flickr2]  %s" % rsp[14:-1], xbmc.LOGNOTICE )
        
        # Parse JSON reply...    
        rsp_dict = simplejson.loads( rsp[14:-1] )

        for photo in rsp_dict[ "photos" ][ "photo" ] :
            # Print photo.items()
            large     = None
            thumbnail = None
            original  = None
            
            if self.DEBUG : start = time.time()
            rsp2      = flickr.photos_getSizes (photo_id = photo[ "id" ], format = "json")
            if self.DEBUG : xbmc.log( ""                          , xbmc.LOGNOTICE )
            if self.DEBUG : xbmc.log( "[Flickr2]  %s" % rsp2[14:-1], xbmc.LOGNOTICE )
            rsp_dict2 = simplejson.loads( rsp2[14:-1] )
            if self.DEBUG : xbmc.log( "[Flickr2]  Execution time (getSizes) = %f" % ( time.time() - start ), xbmc.LOGNOTICE )
            
            for size in rsp_dict2[ "sizes" ][ "size" ] :
                label = size[ "label" ]

                if label == "Thumbnail" :
                    thumbnail = size[ "source" ]
                elif label == "Original" :
                    original  = size[ "source" ]

                if label == self.PREF_PHOTO_SIZE :
                    large = size[ "source" ]
                
            # When could not find prefered size, use the original...
            if large == None :
                large = original
              
            # Debug
            if self.DEBUG :
                xbmc.log( "[Flickr2]  Photo id = %s; thumbnail = %s; large = %s" % ( photo[ "id"], thumbnail, large ), xbmc.LOGNOTICE )            
            
            # add the vide to the list...
            listitem = xbmcgui.ListItem (photo[ "title" ], iconImage="DefaultPicture.png", thumbnailImage=thumbnail)
            ok = xbmcplugin.addDirectoryItem( handle=int(sys.argv[1]), url=large, listitem=listitem, isFolder=False)
            
        # Next page
        listitem = xbmcgui.ListItem (xbmc.getLocalizedString(30501), iconImage = os.path.join(imgDir, 'next-page.png'), thumbnailImage = os.path.join(imgDir, 'next-page.png'))
        ok = xbmcplugin.addDirectoryItem( handle = int(sys.argv[1]), url = "%s?page=%u" % ( sys.argv[0], p_page + 1 ), listitem = listitem, isFolder = True)
            
        # Disable sorting...
        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
            
        # Label (top-right)...
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="%s  (%s)" % ( xbmc.getLocalizedString(30502), xbmc.getLocalizedString(30503) % p_page ) )

        # End of list...
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )        

#
# Main block
#
Main()