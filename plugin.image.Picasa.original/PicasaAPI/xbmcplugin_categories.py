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


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:
    # base paths
    BASE_PLUGIN_THUMBNAIL_PATH = os.path.join( os.getcwd(), "thumbnails" )

    def __init__( self ):
        # parse sys.argv
        self._parse_argv()
        # authenticate user
        self.authenticate()
        if ( not sys.argv[ 2 ] ):
            self.get_categories()
        else:
            self.get_categories( False )

    def _parse_argv( self ):
        if ( not sys.argv[ 2 ] ):
            self.args = _Info( title="" )
        else:
            # call _Info() with our formatted argv to create the self.args object
            exec "self.args = _Info(%s)" % ( unquote_plus( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ) ), )

    def authenticate( self ):
        # if this is first run open settings
        self.openSettings()
        # authentication is not permanent, so do this only when first launching plugin
        if ( not sys.argv[ 2 ] ):
            # get the users settings
            password = xbmcplugin.getSetting( "user_password" )
            # we can only authenticate if both email and password are entered
            if ( self.email and password ):
                # our client api
                from PicasaAPI.PicasaClient import PicasaClient
                client = PicasaClient()
                # make the authentication call
                authkey = client.authenticate( self.email, password )
                # if authentication succeeded, save it for later
                if ( authkey ):
                    xbmcplugin.setSetting( "authkey", authkey )

    def openSettings( self ):
        try:
            # is this the first time plugin was run and user has not set email
            if ( not sys.argv[ 2 ] and xbmcplugin.getSetting( "user_email" ) == "" and xbmcplugin.getSetting( "runonce" ) == "" ):
                # set runonce
                xbmcplugin.setSetting( "runonce", "1" )
                # sleep for xbox so dialogs don't clash. (TODO: report this as a bug?)
                if ( os.environ.get( "OS", "n/a" ) == "xbox" ):
                    xbmc.sleep( 2000 )
                # open settings
                xbmcplugin.openSettings( sys.argv[ 0 ] )
        except:
            # new methods not in build
            pass
        # we need to get the users email
        self.email = xbmcplugin.getSetting( "user_email" )

    def get_categories( self, root=True ):
        try:
            # default categories
            if ( root ):
                categories = (
                                        ( xbmc.getLocalizedString( 30950 ), "users_albums", "", "", True, 0, "album", "", "", True, ),
                                        ( xbmc.getLocalizedString( 30951 ), "presets_photos", "", "", True, 0, "photo", "", "", False, ),
                                        ( xbmc.getLocalizedString( 30952 ), "presets_users", "", "", True, 0, "album", "", "", False, ),
                                        ( xbmc.getLocalizedString( 30955 ), "users_photos", "", "", True, 0, "photo", "", "", True, ),
                                        ( xbmc.getLocalizedString( 30956 ), "users_contacts", "", "", True, 0, "user", "", "", True, ),
                                        ( xbmc.getLocalizedString( 30957 ), "featured_photos", "", "", True, 0, "photo", "", "", False, ),
                                        ( xbmc.getLocalizedString( 30958 ), "recent_photos", "", "", True, 0, "photo", "", "", False, ),
                                    )
            # photo preset category
            elif ( "category='presets_photos'" in sys.argv[ 2 ] ):
                categories = self.get_presets()
            # user preset category
            elif ( "category='presets_users'" in sys.argv[ 2 ] ):
                categories = self.get_presets( True )
            # user preset category
            elif ( "category='users_contacts'" in sys.argv[ 2 ] ):
                categories = self.get_users_contacts()
            # fill media list
            ok = self._fill_media_list( categories )
        except:
            # oops print error message
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            ok = False
        # set cache to disc
        cacheToDisc = ( ok and not ( "category='presets_photos'" in sys.argv[ 2 ] or "category='presets_users'" in sys.argv[ 2 ] ) )
        # send notification we're finished, successfully or unsuccessfully
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=ok, cacheToDisc=cacheToDisc )

    def get_users_contacts( self ):
        # get client
        from PicasaAPI.PicasaClient import PicasaClient
        client = PicasaClient()
        # initialize our category tuple
        categories = ()
        # get settings
        user_id = xbmcplugin.getSetting( "user_email" )
        perpage = ( 10, 15, 20, 25, 30, 40, 50, 75, 100, )[ int( xbmcplugin.getSetting( "perpage" ) ) ]
        thumbsize = ( 72, 144, 160, 200, 288, 320, 400, 512, )[ int( xbmcplugin.getSetting( "thumbsize" ) ) ]
        access = ( "all", "private", "public", )[ int( xbmcplugin.getSetting( "access" ) ) ]
        # starting item
        start_index = ( self.args.page - 1 ) * perpage + 1
        # fetch the items
        feed = client.users_contacts( user_id=user_id, album_id="", photo_id="", pq="", kind="user", imgmax="d", thumbsize=thumbsize, authkey=xbmcplugin.getSetting( "authkey" ), access=access, start__index=start_index, max__results=perpage, q="" )
        # if there were results
        if ( feed ):
            #{'items': [{'thumb_url': u'http://lh3.ggpht.com/_NMYCpWBWM8Y/AAAAW8QQU-U/AAAAAAAAAAA/BPOH5yeOD1M/s64-c/gotoidan.jpg', 'nickname': u'Idan', 'user': u'gotoidan'}], 'totalResults': 1}
            # enumerate thru and add user
            for user in feed[ "items" ]:
                # add user to our dictionary
                categories += ( ( user[ "nickname" ].encode( "utf-8" ), "users_contacts_photos", "", user[ "user" ].encode( "utf-8" ), True, 0, "photo", access, user[ "thumb_url" ], False, ), )
        # return results
        return categories

    def get_presets( self, ptype=False ):
        # set category
        category = ( "photos", "users", )[ ptype ]
        # initialize our category tuple
        categories = ()
        # add our new search item
        if ( ptype ):
            categories += ( ( xbmc.getLocalizedString( 30953 ), "search_users", "", "", True, 2, "album", "", "", False, ), )
        else:
            categories += ( ( xbmc.getLocalizedString( 30954 ), "search_photos", "", "", True, 1, "photo", "", "", False, ), )
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
                # set photo query and user query to empty
                pq = username = u""
                # set thumbnail
                thumbnail = query.split( " | " )[ 1 ].encode( "utf-8" )
                # if this is the user presets set username else set photo query
                if ( ptype ):
                    username = query.split( " | " )[ 0 ].encode( "utf-8" )
                else:
                    pq = query.split( " | " )[ 0 ].encode( "utf-8" )
                # set category
                category = ( "photos", "users", )[ int( xbmcplugin.getSetting( "user_search_kind" ) ) == 0 and ptype ]
                # set kind
                kind = ( "album", "photo", )[ category == "photos" ]
                # set access
                access = ( "all", "private", "public", )[ int( xbmcplugin.getSetting( "access" ) ) ]
                access = ( access, "public", )[ category == "photos" ]
                # add preset to our dictionary
                categories += ( ( query.split( " | " )[ 0 ].encode( "utf-8" ), category, pq, username, True, 0, kind, access, thumbnail, False, ), )
            except:
                # oops print error message
                print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
        return categories

    def _fill_media_list( self, categories ):
        try:
            ok = True
            # enumerate through the tuple of categories and add the item to the media list
            for ( ltitle, method, pq, username, isfolder, issearch, kind, access, thumbnail, login_required, ) in categories:
                # if a user id is required for category and none supplied, skip category
                if ( login_required and self.email == "" ): continue
                # set the callback url
                url = '%s?title=%s&category=%s&access=%s&kind=%s&page=1&user_id=%s&album_id=%s&photo_id=%s&pq=%s&issearch=%d&update_listing=%d' % ( sys.argv[ 0 ], quote_plus( repr( ltitle ) ), repr( method ), repr( access ), repr( kind ), quote_plus( repr( username ) ), repr( "" ), repr( "" ), quote_plus( repr( pq ) ), issearch, False, )
                # check for a valid custom thumbnail for the current category
                thumbnail = thumbnail or self._get_thumbnail( method )
                # set the default icon
                icon = "DefaultFolder.png"
                # only need to add label, icon and thumbnail, setInfo() and addSortMethod() takes care of label2
                listitem=xbmcgui.ListItem( ltitle, iconImage=icon, thumbnailImage=thumbnail )
                # add the item to the media list
                ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=isfolder, totalItems=len( categories ) )
                # if user cancels, call raise to exit loop
                if ( not ok ): raise
            # we do not want to sort queries list
            if ( "category='presets_photos'" in sys.argv[ 2 ] or "category='presets_users'" in sys.argv[ 2 ] ):
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
