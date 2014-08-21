"""
This script will creates a video plugin that lists a sepecific directory.
"""
# main imports
import os
import xbmcgui

from urllib import unquote_plus
import shutil

# Script constants
__scriptname__ = "Plugin Maker"
__author__ = "nuka1195"
__url__ = "http://code.google.com/p/xbmc-scripting/"
__svn_url__ = "http://xbmc-scripting.googlecode.com/svn/trunk/Plugin%20Maker"
__credits__ = "XBMC TEAM, freenode/#xbmc-scripting"
__version__ = "1.2"
__svn_revision__ = 0


class Main:
    def __init__( self ):
        # user selects plugin type
        plugin_type = xbmcgui.Dialog().yesno( __scriptname__, "What type of plugin is this?", "", "", "Video", "Music" )
        # browse for the directory
        path = self.get_browse_dialog( heading="Browse for %s directory" % ( ( "video", "music", )[ plugin_type ], ), shares=( "video", "music", )[ plugin_type ] )
        if ( path ):
            self.create_plugin( path, ( "video", "music", )[ plugin_type ] )

    def get_browse_dialog( self, default="", heading="", dlg_type=0, shares="files", mask="", use_thumbs=False, treat_as_folder=False ):
        """ shows a browse dialog and returns a value
            - 0 : ShowAndGetDirectory
            - 1 : ShowAndGetFile
            - 2 : ShowAndGetImage
            - 3 : ShowAndGetWriteableDirectory
        """
        dialog = xbmcgui.Dialog()
        value = dialog.browse( dlg_type, heading, shares, mask, use_thumbs, treat_as_folder, default )
        return value

    def create_plugin( self, path, plugin_type ):
        plugin = os.path.join( os.getcwd(), "plugin.py" )
        basename = unquote_plus( path )
        if ( path.startswith( "multipath://" ) ):
            basename = os.path.basename( basename[ : -2 ] )
        else:
            basename = os.path.basename( basename[ : -1 ] )
        plugin_name = self.get_keyboard( default=basename + " plugin", heading="Enter plugin name" )
        # we use "U:\\" for linux, windows and osx for platform mode
        root = xbmc.translatePath( ( "U:\\plugins", "Q:\\plugins", )[ os.environ.get( "OS", "xbox" ) == "xbox" ] )
        plugin_path = os.path.join( root, plugin_type, plugin_name )
        if ( not os.path.isdir( plugin_path ) ):
            os.makedirs( plugin_path )
        try:
            # TODO: copy a generic thumb also or browse for thumb
            # TODO: remove an old plugin with same name
            shutil.copy( plugin, os.path.join( plugin_path, "default.py" ) )
            shutil.copytree( os.path.join( os.getcwd(), "resources" ), os.path.join( plugin_path, "resources" ) )
            ok = self.create_settings( os.path.join( plugin_path, "resources", "settings.xml" ), path, plugin_type )
            if ( not ok ): raise
        except:
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            ok = xbmcgui.Dialog().ok( __scriptname__, "Copying plugin to new plugin folder failed!" )

    def get_keyboard( self, default="", heading="", hidden=False ):
        """ shows a keyboard and returns a value """
        keyboard = xbmc.Keyboard( default, heading, hidden )
        keyboard.doModal()
        if ( keyboard.isConfirmed() ):
            return keyboard.getText()
        return default

    def create_settings( self, filepath, sourcepath, plugin_type ):
        try:
            ok = True
            content_strings = ( "movies|tvshows|seasons|episodes|musicvideos", "songs|artists|albums", )
            text = """<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n<settings>\n\t<setting id="path" type="folder" source="%s" label="30000" default="%s" />\n\t<setting id="content" type="enum" values="%s" label="30010" default="%s" />\n\t<setting id="macaddress" type="text" label="30020" default="" />\n\t<setting id="port" type="labelenum" values="135|136|137|138|139|445" label="30030" default="139" enable="!eq(-1,)" /><setting id="retries" type="enum" values="1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25" label="30040" default="6" enable="!eq(-2,)" />\n</settings>""" % ( plugin_type, sourcepath, content_strings[ plugin_type == "music" ], content_strings[ plugin_type == "music" ].split( "|" )[ 0 ] )
            # write new settings file
            file_object = open( filepath, "w" )
            file_object.write( text )
            file_object.close()
        except:
            ok = xbmcgui.Dialog().ok( __scriptname__, "Creating settings.xml file failed!" )
        return ok


if ( __name__ == "__main__" ):
    Main()
