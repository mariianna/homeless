"""
    Category module: list of categories to use as folders
"""

# main imports
import sys
import os
import xbmc
import xbmcgui
import xbmcplugin

from urllib import quote_plus, unquote_plus

from FlickrAPI.FlickrClient import FlickrClient


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:
    # base paths
    BASE_PLUGIN_THUMBNAIL_PATH = os.path.join( os.getcwd(), "thumbnails" )

    def __init__( self ):
        # parse sys.argv
        self._parse_argv()
        # only authorize if user selected from settings
        if ( hasattr( self.args, "authorize" ) ):
            self._authorize()
        else:
            # get user
            ok = self._get_user()
            # set the main default categories
            if ( ok ):
                ok = self._get_root_categories( sys.argv[ 2 ] == "" )
            # set cache to disc
            cacheToDisc = ( ok and not ( "category='presets_users'" in sys.argv[ 2 ] or "category='presets_photos'" in sys.argv[ 2 ] or "category='presets_groups'" in sys.argv[ 2 ] ) )
            # send notification we're finished, successfully or unsuccessfully
            xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=ok, cacheToDisc=cacheToDisc )

    def _parse_argv( self ):
        if ( not sys.argv[ 2 ] ):
            self.args = _Info( title="" )
        else:
            # call _Info() with our formatted argv to create the self.args object
            #exec "self.args = _Info(%s)" % ( unquote_plus( sys.argv[ 2 ][ 1 : ] ).replace( "&", ", " ).replace( "\\u0027", "'" ).replace( "\\u0022", '"' ).replace( "\\u0026", "&" ), )
            exec "self.args = _Info(%s)" % ( unquote_plus( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ) ), )

    def _get_user( self ):
        try:
            self.user_id = ""
            self.user_nsid = ""
            # if this is first run open settings and authorize
            self._run_once()
            # get the users id and token
            userid = xbmcplugin.getSetting( "user_id" )
            self.authtoken = xbmcplugin.getSetting( "authtoken" )
            # if user did not edit settings, return
            if ( userid == "" ): return True
            # flickr client
            client = FlickrClient( True )
            # find the user Id of the person
            if ( "@" in userid ):
                user = client.flickr_people_findByEmail( find_email=userid )
            else:
                user = client.flickr_people_findByUsername( username=userid )
            # if user id is valid and no error occurred return True
            ok = user[ "stat" ] != "fail"
            # if successful, set our user id and nsid
            if ( ok ):
                self.user_id = user[ "user" ][ "id" ]
                self.user_nsid = user[ "user" ][ "nsid" ]
        except:
            # oops print error message
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            ok = False
        # if an error or an invalid id was entered, notify the user
        if ( not ok ):
            xbmcgui.Dialog().ok( xbmc.getLocalizedString( 30900 ), xbmc.getLocalizedString( 30901 ), xbmc.getLocalizedString( 30902 ) )
        return ok

    def _run_once( self ):
        # is this the first time plugin was run and user has not set email
        if ( not sys.argv[ 2 ] and xbmcplugin.getSetting( "user_id" ) == "" and xbmcplugin.getSetting( "runonce" ) != "1" and xbmcplugin.getSetting( "runonce" ) != "2" ):
            # set runonce
            xbmcplugin.setSetting( "runonce", "1" )
            # sleep for xbox so dialogs don't clash. (TODO: report this as a bug?)
            if ( os.environ.get( "OS", "n/a" ) == "xbox" ):
                xbmc.sleep( 2000 )
            # open settings
            xbmcplugin.openSettings( sys.argv[ 0 ] )
        # check again to see if authentication is necessary
        if ( not sys.argv[ 2 ] and xbmcplugin.getSetting( "user_id" ) != "" and xbmcplugin.getSetting( "runonce" ) != "2" and xbmcplugin.getSetting( "authtoken" ) =="" ):
            # set runonce
            xbmcplugin.setSetting( "runonce", "2" )
            # sleep for xbox so dialogs don't clash. (TODO: report this as a bug?)
            if ( os.environ.get( "OS", "n/a" ) == "xbox" ):
                xbmc.sleep( 2000 )
            # ask user if they want to authorize
            ok = xbmcgui.Dialog().yesno( xbmc.getLocalizedString( 30907 ), xbmc.getLocalizedString( 30908 ), "", xbmc.getLocalizedString( 30909 ), xbmc.getLocalizedString( 30910 ), xbmc.getLocalizedString( 30911 ) )
            # authorize
            if (ok ):
                self._authorize()

    def _authorize( self ):
        # flickr client
        client = FlickrClient( api_key=True, secret=True )
        # authenticate
        authtoken = client.authenticate()
        # write it to the settings file
        if ( authtoken ):
            xbmcplugin.setSetting( "authtoken", authtoken )

    def _get_root_categories( self, root=True ):
        try:
            # default categories
            if ( root ):
                categories = (
                                    ( xbmc.getLocalizedString( 30950 ), "flickr_photosets_getList", True, "", "", "", 0, "", False, ),
                                    ( xbmc.getLocalizedString( 30951 ), "flickr_photos_getRecent", False, "", "", "", 0, "", False, ),
                                    ( xbmc.getLocalizedString( 30952 ), "flickr_people_getPublicPhotos", True, "", "", "", 0, "", False, ),
                                    ( xbmc.getLocalizedString( 30953 ), "flickr_interestingness_getList", False, "", "", "", 0, "", False, ),
                                    ( ( xbmc.getLocalizedString( 30961 ), xbmc.getLocalizedString( 30954 ), )[ self.authtoken == "" ], "flickr_favorites_getPublicList", True, "", "", "", 0, "", False, ),
                                    ( xbmc.getLocalizedString( 30955 ), "flickr_photos_getContactsPublicPhotos", True, "", "", "", 0, "", False, ),
                                    ( xbmc.getLocalizedString( 30956 ), "flickr_people_getPublicGroups", True, "", "", "", 0, "", False, ),
                                    ( xbmc.getLocalizedString( 30959 ), "presets_groups", False, "", "", "", 0, "", False, ),
                                    ( xbmc.getLocalizedString( 30960 ), "presets_photos", False, "", "", "", 0, "", False, ),
                                    ( xbmc.getLocalizedString( 30963 ), "presets_users", False, "", "", "", 0, "", False, ),
                                    )
            # photo preset category
            elif ( "category='presets_photos'" in sys.argv[ 2 ] ):
                categories = self.get_presets( 0 )
            # group preset category
            elif ( "category='presets_groups'" in sys.argv[ 2 ] ):
                categories = self.get_presets( 1 )
            # group preset category
            elif ( "category='presets_users'" in sys.argv[ 2 ] ):
                categories = self.get_presets( 2 )
            # fill media list
            ok = self._fill_media_list( categories )
        except:
            # oops print error message
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            ok = False
        return ok

    def get_presets( self, ptype ):
        # set category
        category = ( "photos", "groups", "users", )[ ptype ]
        # initialize our category tuple
        categories = ()
        # add our new search item
        if ( ptype == 0 ):
            categories += ( ( xbmc.getLocalizedString( 30958 ), "flickr_photos_search", False, "", "", "", 1, "", False, ), )
        elif ( ptype == 1 ):
            categories += ( ( xbmc.getLocalizedString( 30957 ), "flickr_groups_search", False, "", "", "", 2, "", False, ), )
        elif ( ptype == 2 ):
            categories += ( ( xbmc.getLocalizedString( 30962 ), "flickr_users_search", False, "", "", "", 3, "", False, ), )
        # fetch saved presets
        try:
            # read the queries
            presets = eval( xbmcplugin.getSetting( "presets_%s" % ( category, ) ) )
            # sort items
            presets.sort()
        except:
            # no presets found
            presets = []
        # enumerate through the presets list and read the query
        for query in presets:
            try:
                # set photo query and group query to empty
                pq = gq = uq = u""
                # set thumbnail
                thumbnail = query.split( " | " )[ 2 ].encode( "utf-8" )
                # set group query, photo query or user query
                if ( ptype == 0 ):
                    pq = query.split( " | " )[ 1 ].encode( "utf-8" )
                elif ( ptype == 1 ):
                    gq = query.split( " | " )[ 1 ].encode( "utf-8" )
                elif ( ptype == 2 ):
                    uq = query.split( " | " )[ 1 ].encode( "utf-8" )
                # add preset to our dictionary
                categories += ( ( query.split( " | " )[ 0 ].encode( "utf-8" ), categories[ 0 ][ 1 ], False, pq, gq, uq, 0, thumbnail, False, ), )
            except:
                # oops print error message
                print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
        return categories

    def _fill_media_list( self, categories ):
        try:
            ok = True
            # enumerate through the list of categories and add the item to the media list
            for ( ltitle, method, userid_required, pq, gq, uq, issearch, thumbnail, authtoken_required, ) in categories:
                # if a user id is required for category and none supplied, skip category
                if ( userid_required and self.user_id == "" ): continue
                if ( authtoken_required and self.authtoken == "" ): continue
                # set the callback url with all parameters
                url = '%s?title=%s&category=%s&userid=%s&usernsid=%s&photosetid=""&photoid=""&groupid=""&primary=""&secret=""&server=""&photos=0&page=1&prevpage=0&pq=%s&gq=%s&uq=%s&issearch=%d&update_listing=%d&' % ( sys.argv[ 0 ], quote_plus( repr( ltitle ) ), repr( method ), repr( self.user_id ), repr( self.user_nsid ), quote_plus( repr( pq ) ), quote_plus( repr( gq ) ), quote_plus( repr( uq ) ), issearch, False, )
                # check for a valid custom thumbnail for the current method
                thumbnail = thumbnail or self._get_thumbnail( method )
                # set the default icon
                icon = "DefaultFolder.png"
                # only need to add label, icon and thumbnail, setInfo() and addSortMethod() takes care of label2
                listitem=xbmcgui.ListItem( ltitle, iconImage=icon, thumbnailImage=thumbnail )
                # add the item to the media list
                ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True, totalItems=len( categories ) )
                # if user cancels, call raise to exit loop
                if ( not ok ): raise
            # we do not want to sort queries list
            if ( "category='presets_photos'" in sys.argv[ 2 ] or "category='presets_groups'" in sys.argv[ 2 ] or "category='presets_users'" in sys.argv[ 2 ] ):
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
            # set our plugin category
            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=self.args.title )
            # set our fanart from user setting
            if ( xbmcplugin.getSetting( "fanart_image" ) ):
                xbmcplugin.setPluginFanart( handle=int( sys.argv[ 1 ] ), image=xbmcplugin.getSetting( "fanart_image" ) )
        except:
            # user cancelled dialog or an error occurred
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            ok = False
        return ok

    def _get_thumbnail( self, title ):
        # create the full thumbnail path for skins directory
        thumbnail = os.path.join( sys.modules[ "__main__" ].__plugin__, title + ".png" )
        # use a plugin custom thumbnail if a custom skin thumbnail does not exists
        if ( not xbmc.skinHasImage( thumbnail ) ):
            # create the full thumbnail path for plugin directory
            thumbnail = os.path.join( self.BASE_PLUGIN_THUMBNAIL_PATH, title + ".png" )
            # use a default thumbnail if a custom thumbnail does not exists
            if ( not os.path.isfile( thumbnail ) ):
                thumbnail = "DefaultFolder.png"
        return thumbnail
