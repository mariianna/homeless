#
# Imports
#
import sys
import xbmc
import xbmcgui
import xbmcplugin
import urllib

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
        self.DEBUG = False
        
        #
        # Parse parameters...
        #
        params = dict(part.split('=') for part in sys.argv[ 2 ][ 1: ].split('&'))
        video = urllib.unquote_plus( params[ "video" ] ) 

        # Settings
        self.video_players = { "0" : xbmc.PLAYER_CORE_AUTO,
                               "1" : xbmc.PLAYER_CORE_DVDPLAYER,
                               "2" : xbmc.PLAYER_CORE_MPLAYER }
        self.video_player = xbmcplugin.getSetting ("video_player")

        #
        # Play video...
        #
        self.playVideo( video )
    
    #
    # Play video...
    #
    def playVideo( self, video ) :
        #
        # Get current list item details...
        #
        title     = unicode( xbmc.getInfoLabel( "ListItem.Title"   ), "utf-8" )
        thumbnail =          xbmc.getInfoImage( "ListItem.Thumb"   )
        studio    = unicode( xbmc.getInfoLabel( "ListItem.Studio"  ), "utf-8" )
        plot      = unicode( xbmc.getInfoLabel( "ListItem.Plot"    ), "utf-8" )
        director  = unicode( xbmc.getInfoLabel( "ListItem.Director"), "utf-8" )       

        #    
        # Play video...
        #
        playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
        playlist.clear()
 
        listitem = xbmcgui.ListItem( title, iconImage="DefaultVideo.png", thumbnailImage=thumbnail )
        listitem.setInfo( "video", { "Title": title, "Studio" : studio, "Plot" : plot, "Director" : director } )
        playlist.add( video, listitem )
        
        # Play video...
        xbmcPlayer = xbmc.Player( self.video_players[ self.video_player ] )
        xbmcPlayer.play(playlist)   

#
# The End
#