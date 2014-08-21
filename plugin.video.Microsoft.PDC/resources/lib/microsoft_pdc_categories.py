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
from   microsoft_pdc_utils import HTTPCommunicator

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
        # Get the categories...
        #
        self.getCategories()
    
    #
    # Get categories...
    #
    def getCategories( self ) :
        # 
        # Get XML...
        #         
        httpCommunicator = HTTPCommunicator()
        url              = "http://videoak.microsoftpdc.com/pdc_schedule/Schedule.xml"
        xmlData          = httpCommunicator.get( url )
                          
        #
        # Parse response...
        # 
        rootElement   = ElementTree.fromstring( xmlData, ElementTree.XMLParser(encoding="utf-8") )
        trackElements = rootElement.findall("Tracks/Track")
        
        categories = []
        categories.append( { "Name" : "All sessions", "Id" : "" } )
        
        for trackElement in trackElements :
            categoryName  = trackElement.get("Name")
            categories.append( { "Name" : categoryName, "Id" : categoryName } )

        # Add entries...
        for category in categories :
            listitem        = xbmcgui.ListItem( category["Name"] )
            url             = '%s?action=sessions&category=%s' % ( sys.argv[ 0 ], urllib.quote_plus( category["Id"] ) ) 
            xbmcplugin.addDirectoryItem( handle=int(sys.argv[ 1 ]), url=url, listitem=listitem, isFolder=True)            

        # Disable sorting...
        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
        
        # End of directory...
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )
