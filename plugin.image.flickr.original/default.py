"""
    Plugin for viewing content from flickr.com
"""

# main imports
import sys
import xbmc

# plugin constants
__plugin__ = "flickr"
__author__ = "nuka1195"
__url__ = "http://code.google.com/p/xbmc-addons/"
__svn_url__ = "http://xbmc-addons.googlecode.com/svn/trunk/plugins/pictures/flickr"
__version__ = "1.5.4"
__svn_revision__ = "$Revision: 1539 $"
__XBMC_Revision__ = "19001"

def _check_compatible():
    try:
        # spam plugin statistics to log
        xbmc.log( "[PLUGIN] '%s: Version - %s-r%s' initialized!" % ( __plugin__, __version__, __svn_revision__.replace( "$", "" ).replace( "Revision", "" ).replace( ":", "" ).strip() ), xbmc.LOGNOTICE )
        # get xbmc revision
        xbmc_rev = int( xbmc.getInfoLabel( "System.BuildVersion" ).split( " r" )[ -1 ] )
        # compatible?
        ok = xbmc_rev >= int( __XBMC_Revision__ )
    except:
        # error, so unknown, allow to run
        xbmc_rev = 0
        ok = 2
    # spam revision info
    xbmc.log( "     ** Required XBMC Revision: r%s **" % ( __XBMC_Revision__, ), xbmc.LOGNOTICE )
    xbmc.log( "     ** Found XBMC Revision: r%d [%s] **" % ( xbmc_rev, ( "Not Compatible", "Compatible", "Unknown", )[ ok ], ), xbmc.LOGNOTICE )
    # if not compatible, inform user
    if ( not ok ):
        import xbmcgui
        xbmcgui.Dialog().ok( "%s - %s: %s" % ( __plugin__, xbmc.getLocalizedString( 30700 ), __version__, ), xbmc.getLocalizedString( 30701 ) % ( __plugin__, ), xbmc.getLocalizedString( 30702 ) % ( __XBMC_Revision__, ), xbmc.getLocalizedString( 30703 ) )
    #return result
    return ok


if ( __name__ == "__main__" ):
    if ( not sys.argv[ 2 ] ):
        # check for compatibility, only need to check this once, continue if ok
        if ( _check_compatible() ):
            from FlickrAPI import xbmcplugin_categories as plugin
    elif ( "category='presets_photos'" in sys.argv[ 2 ] ):
        from FlickrAPI import xbmcplugin_categories as plugin
    elif ( "category='presets_groups'" in sys.argv[ 2 ] ):
        from FlickrAPI import xbmcplugin_categories as plugin
    elif ( "category='presets_users'" in sys.argv[ 2 ] ):
        from FlickrAPI import xbmcplugin_categories as plugin
    elif ( "authorize=True" in sys.argv[ 2 ] ):
        from FlickrAPI import xbmcplugin_categories as plugin
    else:
        from FlickrAPI import xbmcplugin_pictures as plugin

    try:
        plugin.Main()
    except:
        pass
