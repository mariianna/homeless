"""
    Photos module: fetches a list of photos for a specific category
"""

# main imports
import sys
import os
import xbmc
import xbmcgui
import xbmcplugin

from urllib import quote_plus, unquote_plus

from PicasaAPI.PicasaClient import PicasaClient


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:
    # base paths
    BASE_PLUGIN_THUMBNAIL_PATH = os.path.join( os.getcwd(), "thumbnails" )

    def __init__( self ):
        self._get_settings()
        self._get_strings()
        self._get_authkey()
        self._parse_argv()
        self._get_items()

    def _get_settings( self ):
        self.settings = {}
        self.settings[ "user_email" ] = xbmcplugin.getSetting( "user_email" )
        self.settings[ "access" ] = ( "all", "private", "public", )[ int( xbmcplugin.getSetting( "access" ) ) ]
        self.settings[ "perpage" ] = ( 10, 15, 20, 25, 30, 40, 50, 75, 100, )[ int( xbmcplugin.getSetting( "perpage" ) ) ]
        self.settings[ "thumbsize" ] = ( 72, 144, 160, 200, 288, 320, 400, 512, )[ int( xbmcplugin.getSetting( "thumbsize" ) ) ]
        self.settings[ "user_search_kind" ] = ( "album", "photo", )[ int( xbmcplugin.getSetting( "user_search_kind" ) ) ]
        self.settings[ "saved_searches" ] = ( 10, 20, 30, 40, )[ int( xbmcplugin.getSetting( "saved_searches" ) ) ]
        self.settings[ "fanart_image" ] = xbmcplugin.getSetting( "fanart_image" )
        self.save_search = False

    def _get_strings( self ):
        self.localized_string = {}
        self.localized_string[ 30900 ] = xbmc.getLocalizedString( 30900 )
        self.localized_string[ 30901 ] = xbmc.getLocalizedString( 30901 )
        self.localized_string[ 30902 ] = xbmc.getLocalizedString( 30902 )
        self.localized_string[ 30903 ] = xbmc.getLocalizedString( 30903 )
        self.localized_string[ 30905 ] = xbmc.getLocalizedString( 30905 )

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the self.args object
        exec "self.args = _Info(%s)" % ( unquote_plus( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ) ), )

    def _get_authkey( self ):
        self.authkey = xbmcplugin.getSetting( "authkey" )

    def _get_items( self ):
        # get the photos and/or subcategories and fill the media list
        exec "ok, total = self.%s()" % ( self.args.category, )
        # send notification we're finished, successfully or unsuccessfully
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=ok, updateListing=self.args.update_listing )#, cacheToDisc=not self.args.issearch )
        # if there were photos and this was a search ask to save result as a preset
        if ( ok and total and self.args.issearch and self.save_search ):
            self.save_as_preset()

    def save_as_preset( self ):
        # select correct query
        query = ( self.args.pq, self.args.user_id, )[ self.args.issearch - 1 ]
        # fetch saved presets
        try:
            # read the queries
            presets = eval( xbmcplugin.getSetting( "presets_%s" % ( "photos", "users", )[ self.args.issearch - 1  ], ) )
            # if this is an existing search, move it up
            for count, preset in enumerate( presets ):
                if ( repr( query + " | " )[ : -1 ] in repr( preset ) ):
                    del presets[ count ]
                    break
            # limit to number of searches to save
            if ( len( presets ) >= self.settings[ "saved_searches" ] ):
                presets = presets[ : self.settings[ "saved_searches" ] - 1 ]
        except:
            # no presets found
            presets = []
        # insert our new search
        presets = [ query + " | " + self.query_thumbnail ] + presets
        # save search query
        xbmcplugin.setSetting( "presets_%s" % ( "photos", "users", )[ self.args.issearch - 1  ], repr( presets ) )

    def search_photos( self ):
        # get the query to search for from the user
        self.args.pq = self._get_keyboard( heading=xbmc.getLocalizedString( 30906 ) )
        # if blank or the user cancelled the keyboard return
        if ( not self.args.pq ): return False, 0
        # we need to set the function to photos
        self.args.category = "photos"
        # we need to set the title to our query
        self.args.title = self.args.pq
        # fetch the items
        return self.fetch_photos( kind="photo" )

    def search_users( self ):
        # get the user id to search for from the user
        self.args.user_id = self._get_keyboard( heading=xbmc.getLocalizedString( 30907 ) )
        # if blank or the user cancelled the keyboard return
        if ( not self.args.user_id ): return False, 0
        # we need to set the category to users
        self.args.category = ( "users", "photos", )[ self.settings[ "user_search_kind" ] == "photo" ]
        # we need to set the title to our query
        self.args.title = self.args.user_id
        # TODO: see why punlic search is required here
        # fetch the items
        return self.fetch_photos( user_id=self.args.user_id, kind=self.settings[ "user_search_kind" ], access="public" )

    def recent_photos( self ):
        # get the query to search for from the user
        self.args.pq = ""
        # we need to set the function to photos
        self.args.category = "photos"
        # we need to set the title to our query
        ##self.args.title = self.args.pq
        # fetch the items
        return self.fetch_photos( kind="photo" )

    def users_albums( self ):
        # set author to user name
        self.args.user_id = self.settings[ "user_email" ]
        # we need to set the category to users
        self.args.category = "users"
        # fetch the items
        return self.fetch_photos( user_id=self.args.user_id, kind="album" )

    def users_photos( self ):
        # set author to user name
        self.args.user_id = self.settings[ "user_email" ]
        # we need to set the category to users
        self.args.category = "photos"
        # fetch the items
        return self.fetch_photos( user_id=self.args.user_id, kind="photo" )

    def users_contacts_photos( self ):
        # we need to set the category to users
        self.args.category = "photos"
        # fetch the items
        return self.fetch_photos( user_id=self.args.user_id, kind="photo" )

    def featured_photos( self ):
        # we need to set the category to users
        self.args.category = "photos"
        # fetch the items
        return self.fetch_photos( kind="photo" )

    def photos( self ):
        # we end up here for pages 2 and on
        return self.fetch_photos( user_id=self.args.user_id, album_id=self.args.album_id, kind=self.args.kind, access=self.args.access )

    def users( self ):
        # we end up here for pages 2 and on
        return self.fetch_photos( user_id=self.args.user_id, kind=self.args.kind, access=self.args.access )

    def fetch_photos( self, user_id="", album_id="", photo_id="", kind="", access="" ):
        # Picasa client
        client = PicasaClient()
        # starting item
        start_index = ( self.args.page - 1 ) * self.settings[ "perpage" ] + 1
        # set access
        if ( access == "" ):
            access = self.settings[ "access" ]
        # fetch the items
        exec 'feed = client.%s( user_id=user_id, album_id=album_id, photo_id=photo_id, kind=kind, imgmax="d", thumbsize=self.settings[ "thumbsize" ], authkey=self.authkey, access=access, start__index=start_index, max__results=self.settings[ "perpage" ], q=self.args.pq )'  % ( self.args.category, )
        # if there were results
        if ( feed ):
            # set user icon for user query
            self.user_icon = feed[ "user_icon" ]
            # calculate total pages
            pages = self._get_total_pages( feed[ "totalResults" ] )
            # fill media list
            return self._fill_media_list( feed[ "items" ], self.args.page, pages, self.settings[ "perpage" ], feed[ "totalResults" ], kind=kind, access=access )
        #else return failed
        else:
            return False, 0

    def _get_total_pages( self, total ):
        # calculate the total number of pages
        pages = int( total / self.settings[ "perpage" ] ) + ( total % self.settings[ "perpage" ] > 0 )
        #return value
        return pages

    def _fill_media_list( self, items, page, pages=1, perpage=1, total=1, encoding="utf-8", kind="photo", access="" ):
        try:
            # calculate total items including previous and next
            total_items = len( items ) + ( page < pages ) + ( page > 1 )
            # if there is more than one page and we are not on the last page, we add our next page folder
            if ( page < pages ):
                # calculate the starting video
                startno = page * perpage + 1
                # calculate the ending video
                endno = startno + perpage - 1
                # if there are fewer items than per_page set endno to total
                if ( endno > total ):
                    endno = total
                # create the callback url
                url = '%s?title=%s&category=%s&access=%s&kind=%s&page=%d&pq=%s&issearch=0&update_listing=%d&user_id=%s&album_id=%s&photo_id=%s' % ( sys.argv[ 0 ], quote_plus( repr( self.args.title ) ), repr( self.args.category ), repr( access ), repr( kind ), page + 1, quote_plus( repr( self.args.pq ) ), True, repr( self.args.user_id ), repr( self.args.album_id ), repr( self.args.photo_id ), )
                # TODO: get rid of self.BASE_PLUGIN_THUMBNAIL_PATH
                # we set the thumb so XBMC does not try and cache the next pictures
                thumbnail = os.path.join( self.BASE_PLUGIN_THUMBNAIL_PATH, "next.png" )
                # set the default icon
                icon = "DefaultFolder.png"
                # set stringid
                stringid = 30908 + ( kind == "album" )
                # only need to add label and icon, setInfo() and addSortMethod() takes care of label2
                listitem=xbmcgui.ListItem( label="%s (%d-%d)" % ( xbmc.getLocalizedString( stringid ), startno, endno, ), iconImage=icon, thumbnailImage=thumbnail )
                # add the folder item to our media list
                ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True, totalItems=total_items )
            # if we are on page 2 or more, we add our previous page folder
            if ( page > 1 ):
                # calculate the starting video
                startno = ( page - 2 ) * perpage + 1
                # calculate the ending video
                endno = startno + perpage - 1
                # create the callback url
                url = '%s?title=%s&category=%s&access=%s&kind=%s&page=%d&pq=%s&issearch=0&update_listing=%d&user_id=%s&album_id=%s&photo_id=%s' % ( sys.argv[ 0 ], quote_plus( repr( self.args.title ) ), repr( self.args.category ), repr( access ), repr( kind ), page - 1, quote_plus( repr( self.args.pq ) ), True, repr( self.args.user_id ), repr( self.args.album_id ), repr( self.args.photo_id ), )
                # TODO: get rid of self.BASE_PLUGIN_THUMBNAIL_PATH
                # we set the thumb so XBMC does not try and cache the previous pictures
                thumbnail = os.path.join( self.BASE_PLUGIN_THUMBNAIL_PATH, "previous.png" )
                # set the default icon
                icon = "DefaultFolder.png"
                # set stringid
                stringid = 30908 + ( kind == "album" )
                # only need to add label and icon, setInfo() and addSortMethod() takes care of label2
                listitem=xbmcgui.ListItem( label="%s (%d-%d)" % ( xbmc.getLocalizedString( stringid ), startno, endno, ), iconImage=icon, thumbnailImage=thumbnail )
                # add the folder item to our media list
                ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True, totalItems=total_items )
            # set our thumbnail for queries
            if ( self.user_icon ):
                self.query_thumbnail = self.user_icon
            else:
                self.query_thumbnail = items[ 0 ][ "thumb_url" ]
            # enumerate through the list of pictures and add the item to the media list
            for c, item in enumerate( items ):
                # construct our url
                if ( item[ "photo_url" ] ):
                    # we are a photo, so set it's url to the full image
                    url = item[ "photo_url" ]
                    # we are not a folder
                    isfolder = False
                    # set the default icon
                    icon = "DefaultPicture.png"
                else:
                    # we need to reset page and kind for albums that contain photos
                    if ( item[ "album_id" ] and kind == "album" ):
                        # we switch to photos since that's what an album holds
                        kind = "photo"
                        # set page to #1
                        page = 1
                        # set our category to photos
                        self.args.category = "photos"
                    url = "%s?title=%s&category=%s&access=%s&kind=%s&page=%d&pq=%s&issearch=0&update_listing=%d&user_id=%s&album_id=%s&photo_id=%s" % ( sys.argv[ 0 ], quote_plus( repr( item[ "title" ] ) ), repr( self.args.category ), repr( access ), repr( kind ), page, repr( "" ), False, repr( item[ "user_id" ] ), repr( item[ "album_id" ] ), repr( item[ "photo_id" ] ), )
                    # no photo_url, must be an album
                    isfolder = True
                    # set the default icon
                    icon = "DefaultFolder.png"
                # we add total items if this is an album, we add author if it is a photo
                if ( item[ "photo_url" ] ):
                    title = item[ "title" ]
                else:
                    title = "%s (%d)" % ( item[ "title" ], item[ "numphotos" ], )
                # only need to add label, icon and thumbnail, setInfo() and addSortMethod() takes care of label2
                listitem=xbmcgui.ListItem( label=title, iconImage=icon, thumbnailImage=item[ "thumb_url" ] )
                # add the different infolabels we want to sort by
                listitem.setInfo( type="Pictures", infoLabels={ "Title": title } )
                # we add additional properties and infolabels for photos
                if ( item[ "photo_url" ] ):
                    listitem.setInfo( type="Pictures", infoLabels={ "Date": "%s-%s-%s" % ( item[ "photo_datetime" ][ 8 : 10 ], item[ "photo_datetime" ][ 5 : 7 ], item[ "photo_datetime" ][  : 4 ], ), "Size": item[ "photo_size" ], "exif:exiftime": item[ "photo_datetime" ], "exif:resolution": "%d,%d" % ( item[ "photo_width" ], item[ "photo_height" ], ) } )
                    # skins display these with ListItem.Property(User)...
                    listitem.setProperty( "User", item[ "author" ] )
                    listitem.setProperty( "Description", item[ "summary" ] )
                    listitem.setProperty( "DateTaken", item[ "photo_datetime" ] )
                # add the video to the media list
                ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=isfolder, totalItems=total_items )
                # if user cancels, call raise to exit loop
                if ( not ok ): raise
        except:
            # oops print error message
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            ok = False
        # if successful and user did not cancel, add all the required sort methods
        if ( ok ):
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_SIZE )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
            # set content
            xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content="pictures" )
            # set our plugin category
            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=self.args.title )
            # if skin has fanart image use it
            fanart_image = os.path.join( sys.modules[ "__main__" ].__plugin__, self.args.category + "-fanart.png" )
            if ( xbmc.skinHasImage( fanart_image ) ):
                xbmcplugin.setPluginFanart( handle=int( sys.argv[ 1 ] ), image=fanart_image )
            # set our fanart from user setting
            elif ( self.settings[ "fanart_image" ] ):
                xbmcplugin.setPluginFanart( handle=int( sys.argv[ 1 ] ), image=self.settings[ "fanart_image" ] )
        return ok, total_items

    def _get_keyboard( self, default="", heading="", hidden=False ):
        """ shows a keyboard and returns a value """
        self.save_search = True
        keyboard = xbmc.Keyboard( default, heading, hidden )
        keyboard.doModal()
        if ( keyboard.isConfirmed() ):
            return unicode( keyboard.getText(), "utf-8" )
        return default
