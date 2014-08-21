"""
    Plugin Maker: This plugin will create a directory listing of media files.
"""

# main imports
import os
import sys
import xbmc
import xbmcgui
import xbmcplugin

import datetime
from urllib import quote_plus, unquote_plus

from resources.lib import wol

# plugin constants
__plugin__ = "Plugin Maker"
__author__ = "nuka1195"
__credits__ = "Team XBMC/ozNick"
__version__ = "1.2"


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:
    # base paths
    BASE_CACHE_PATH = xbmc.translatePath( "P:\\Thumbnails" )
    # music media extensions
    MEDIA_EXT = ( xbmc.getSupportedMedia( "music" ), )
    # video media extensions
    MEDIA_EXT += ( xbmc.getSupportedMedia( "video" ), )

    def __init__( self ):
        self._get_settings()
        self._send_wol()
        if ( sys.argv[ 2 ] ):
            self._parse_argv()
        self._get_items( self.args.path )

    def _get_settings( self ):
        self.settings = {}
        self.settings[ "path" ] = self._get_path_list( xbmcplugin.getSetting( "path" ) )
        self.settings[ "content" ] = xbmcplugin.getSetting( "content" )
        self.settings[ "macaddress" ] = xbmcplugin.getSetting( "macaddress" )
        self.settings[ "port" ] = int( xbmcplugin.getSetting( "port" ) )
        self.settings[ "retries" ] = int( xbmcplugin.getSetting( "retries" ) ) + 1
        self.media_type = ( "video" in os.getcwd() )
        # we need to set self.args.path
        self.args = _Info( path=self.settings[ "path" ] )

    def _get_path_list( self, paths ):
        # we do not want the slash at end
        if ( paths.endswith( "\\" ) or paths.endswith( "/" ) ):
            paths = paths[ : -1 ]
        # if this is not a multipath return it as a list
        if ( not paths.startswith( "multipath://" ) ): return [ paths ]
        # we need to parse out the separate paths in a multipath share
        fpaths = []
        # multipaths are separated by a forward slash(why not a pipe)
        path_list = paths[ 12 : ].split( "/" )
        # enumerate thru our path list and unquote the url
        for path in path_list:
        # we do not want the slash at end
            if ( path.endswith( "\\" ) or path.endswith( "/" ) ):
                path = path[ : -1 ]
            # add our path
            fpaths += [ path ]
        return fpaths

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the self.args object
        exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ), )
        # we want this to be a list
        self.args.path = [ self.args.path ]

    def _get_items( self, path ):
        try:
            ok = self._get_list()
            # if successful and user did not cancel, add all the required sort methods and set the content
            if ( ok ):
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_SIZE )
                # set content
                xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content=self.settings[ "content" ] )
        except:
            # oops print error message
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            ok = False
        # send notification we're finished, successfully or unsuccessfully
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=ok )

    def _get_list( self ):
        items = []
        for path in self.args.path:
            items += self._get_file_list( path )
        return self._fill_media_list( items )

    def _get_file_list( self, path ):
        #    if ( os.path.supports_unicode_filenames or os.environ.get( "OS", "n/a" ) == "win32"  or os.environ.get( "OS", "n/a" ) == "xbox" ):
        try:
            items = []
            # get the directory listing
            entries = xbmc.executehttpapi( "GetDirectory(%s)" % ( unquote_plus( path ), ) ).split( "\n" )
            # enumerate through our items list and add the full name to our entries list
            for entry in entries:
                if ( entry ):
                    # fix path
                    file_path = self._clean_file_path( entry )
                    # get the item info
                    title, isMedia, isFolder = self._get_file_info( file_path )
                    # add our entry to our items list
                    if ( isMedia or isFolder ):
                        items += [ ( file_path, title, isFolder, ) ]
        except:
            # oops print error message
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
        return items

    def _clean_file_path( self, path ):
        # replace <li>
        path = path.replace( "<li>", "" )
        # remove slash at end
        if ( path.endswith( "/" ) or path.endswith( "\\" ) ):
            path = path[ : -1 ]
        # make it a unicode object
        path = unicode( path, "utf-8" )
        # return final rsult
        return path

    def _get_file_info( self, file_path ):
        try:
            # parse item for title
            title, ext = os.path.splitext( os.path.basename( file_path ) )
            # TODO: verify .zip can be a folder also
            # is this a folder?
            isFolder = ( ext == ".rar" or os.path.isdir( self._fix_stacked_path( file_path ) ) )
            # if it's a folder keep extension in title
            title += ( "", ext, )[ isFolder ]
            # default isMedia to false
            isMedia = False
            # if this is a file, check to see if it's a valid media file
            if ( not isFolder ):
                # if it is a media file add it to our items list
                isMedia = ( ext and ext.lower() in self.MEDIA_EXT[ self.media_type ] )
            return title, isMedia, isFolder
        except:
            # oops print error message
            ##print repr( file_path )
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            return "", False, False

    def _fill_media_list( self, items ):
        try:
            ok = True
            # enumerate through the list and add the item to our media list
            for item in items:
                # add the item
                ok = self._add_item( item, len( items ) )
                # if there was an error or the user cancelled, raise an exception
                if ( not ok ): raise
        except:
            # listing failed for some reason
            ok = False
        return ok

    def _add_item( self, item, total ):
        ok = True
        add = True
        # backslashes cause issues when passed in the url, so replace them
        url = item[ 0 ]
        # if it is a folder handle it different
        if ( item[ 2 ] ):
            # create our url
            url = '%s?path=%s&isFolder=%d' % ( sys.argv[ 0 ], repr( quote_plus( url ) ), item[ 2 ], )
            # if a folder.jpg exists use that for our thumbnail
            thumbnail = os.path.join( item[ 0 ], "%s.jpg" % ( item[ 1 ], ) )
            if ( not os.path.isfile( thumbnail ) ): thumbnail = ""
            icon = "DefaultFolder.png"
            # only need to add label and icon, setInfo() and addSortMethod() takes care of label2
            listitem=xbmcgui.ListItem( label=item[ 1 ], iconImage=icon )
        else:
            # we only want the first path in a stack:// file item
            fpath = self._fix_stacked_path( item[ 0 ] )
            # call _get_thumbnail() for the path to the cached thumbnail
            thumbnail = self._get_thumbnail( fpath )
            # set the default icon
            icon = "Default%s.png" % ( "Audio", "Video", )[ self.media_type ]
            try:
                # get the date of the file
                date = datetime.datetime.fromtimestamp( os.path.getmtime( fpath.encode( "utf-8" ) ) ).strftime( "%d-%m-%Y" )
                # get the size of the file
                size = long( os.path.getsize( fpath.encode( "utf-8" ) ) )
                # only need to add label and thumbnail, setInfo() and addSortMethod() takes care of label2
                listitem = xbmcgui.ListItem( label=item[ 1 ], iconImage=icon, thumbnailImage=thumbnail.encode( "utf-8" ) )
                # set an overlay if one is practical
                overlay = ( xbmcgui.ICON_OVERLAY_NONE, xbmcgui.ICON_OVERLAY_RAR, xbmcgui.ICON_OVERLAY_ZIP, )[ item[ 0 ].endswith( ".rar" ) + ( 2 * item[ 0 ].endswith( ".zip" ) ) ]
                # add the different infolabels we want to sort by
                listitem.setInfo( type=( "music", "video", )[ self.media_type ], infoLabels={ "Title": item[ 1 ], "Date": date, "Size": size, "Overlay": overlay } )
            except:
                # oops print error message
                add = False
                ##print repr( item[ 1 ] )
                print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
        if ( add ):
            # add the item to the media list
            ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=item[ 2 ], totalItems=total )
        return ok

    def _fix_stacked_path( self, path ):
        # we need to strip stack:// and return only the first path
        if ( path.startswith( "stack://" ) ):
            path = path[ 8 : ].split( " , " )[ 0 ]
        return path

    def _get_thumbnail( self, path ):
        fpath = path
        # if this is a smb path, we need to eliminate username/password
        if ( path.startswith( "smb://" ) and "@" in path ):
            # split the path into useable parts
            share_string_list = path.split( "/" )
            # strip username/password
            share_string_list[ 2 ] = share_string_list[ 2 ].split( "@" )[ 1 ]
            # concatenate the list back together
            fpath = "/".join( share_string_list )
        # make the proper cache filename and path so duplicate caching is unnecessary
        filename = xbmc.getCacheThumbName( fpath )
        thumbnail = os.path.join( self.BASE_CACHE_PATH, ( "Music", "Video", )[ self.media_type ], filename[ 0 ], filename )
        # if the cached thumbnail does not exist check for a tbn file
        if ( not os.path.isfile( thumbnail ) ):
            # create filepath to a local tbn file
            thumbnail = os.path.splitext( path )[ 0 ] + ".tbn"
            # if there is no local tbn file leave blank
            if ( not os.path.isfile( thumbnail.encode( "utf-8" ) ) ):
                thumbnail = ""
        return thumbnail

    def _send_wol( self ):
        # send wol to mac(s)
        if ( self.settings[ "macaddress" ] ):
            # split our mac addresses
            macs = self.settings[ "macaddress" ].split( "|" )
            # enumerate thru the mac addresses and send wol
            for mac in macs:
                wol.WakeOnLan( mac )
            # enumerate thru the paths and check if a host exists and is alive
            for path in self.settings[ "path" ]:
                # check if computer is alive
                hostname, alive = wol.CheckHost( path, self.settings[ "port" ], self.settings[ "retries" ] )


if ( __name__ == "__main__" ):
    Main()