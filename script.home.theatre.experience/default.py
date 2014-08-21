# constants
__script__ = "Home Theater Experience"
__author__ = "nuka1195"
__url__ = "http://code.google.com/p/xbmc-addons/"
__svn_url__ = "http://xbmc-addons.googlecode.com/svn/trunk/scripts/Home%20Theater%20Experience"
__version__ = "1.5.1c"
__svn_revision__ = "$Revision: 1564 $"
__XBMC_Revision__ = "21010"

def _check_compatible():
    try:
        # spam plugin statistics to log
        xbmc.log( "[SCRIPT] '%s: Version - %s-r%s' initialized!" % ( __script__, __version__, __svn_revision__.replace( "$", "" ).replace( "Revision", "" ).replace( ":", "" ).strip() ), xbmc.LOGNOTICE )
        # get xbmc revision
        xbmc_rev = int( xbmc.getInfoLabel( "System.BuildVersion" ).split( " r" )[ -1 ][ : 5 ] )
        # compatible?
        ok = xbmc_rev >= int( __XBMC_Revision__ )
    except:
        # error, so unknown, allow to run
        xbmc_rev = 0
        ok = 2
    # spam revision info
    xbmc.log( "     ** Required XBMC Revision: r%s **" % ( __XBMC_Revision__, ), xbmc.LOGNOTICE )
    xbmc.log( "     ** Found XBMC Revision: r%d [%s] **" % ( xbmc_rev, ( "Not Compatible", "Compatible", "Unknown", )[ ok ], ), xbmc.LOGNOTICE )
    # TODO: maybe remove this notification
    # if not compatible, inform user
    if ( not ok ):
        import xbmcgui
        import os
        # get localized strings
        _ = xbmc.Language( os.getcwd() ).getLocalizedString
        # inform user
        xbmcgui.Dialog().ok( "%s - %s: %s" % ( __script__, _( 32700 ), __version__, ), _( 32701 ) % ( __script__, ), _( 32702 ) % ( __XBMC_Revision__, ), _( 32703 ) )
    #return result
    return ok


if ( __name__ == "__main__" ):
    # only run if compatible
    if ( _check_compatible() ):
        from resources.lib import xbmcscript_player as script
        script.Main()
