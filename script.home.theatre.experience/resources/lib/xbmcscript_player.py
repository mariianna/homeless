###########################################################
"""
    Main Player Module:
    - plays # of optional Movie Theater intro videos
    - plays optional trivia slide show w/ optional music, intro/outro videos/still images
    - plays # of optional random trailers w/ optional intro/outro videos
    - plays highlighted video w/ optional intro/outro videos, rating video and dolby/dts video
    - plays # optional Movie Theater outro videos
"""
############################################################
# main imports
import sys
import os
import xbmcgui
import xbmc

# language method
_L_ = xbmc.Language( scriptPath=os.getcwd() ).getLocalizedString
# settings method
_S_ = xbmc.Settings( path=os.getcwd() ).getSetting

# set proper message
try:
    message = ( 32530, 32540, )[ sys.argv[ 1 ] == "ClearWatchedTrailers" ]
except:
    message = 32520

pDialog = xbmcgui.DialogProgress()
pDialog.create( sys.modules[ "__main__" ].__script__, _L_( message )  )
pDialog.update( 0 )

from urllib import quote_plus
from random import shuffle


class Main:
    # base paths
    BASE_CACHE_PATH = os.path.join( xbmc.translatePath( "special://profile" ), "Thumbnails", "Video" )
    BASE_CURRENT_SOURCE_PATH = os.path.join( xbmc.translatePath( "special://profile/" ), "script_data", os.path.basename( os.getcwd() ) )

    def __init__( self ):
        # if an arg was passed check it for ClearWatchedTrivia or ClearWatchedTrailers
        import traceback
        try:
            if ( sys.argv[ 1 ] == "ClearWatchedTrivia" or sys.argv[ 1 ] == "ClearWatchedTrailers" ):
                self._clear_watched_items( sys.argv[ 1 ] )
            elif ( sys.argv[ 1 ] == "ViewChangelog" ):
                self._view_changelog()
            elif ( sys.argv[ 1 ] == "ViewReadme" ):
                self._view_readme()
        except:
            try:
                #traceback.print_exc()
                # create the playlist
                mpaa = self._create_playlist()
                # play the trivia slide show
                self._play_trivia( mpaa=mpaa )
            except:
                traceback.print_exc()

    def _clear_watched_items( self, clear_type ):
        xbmc.log( "_clear_watched_items( %s )", ( clear_type, ), xbmc.LOGNOTICE )
        # initialize base_path
        base_paths = []
        # clear trivia or trailers
        if ( clear_type == "ClearWatchedTrailers" ):
            # trailer settings, grab them here so we don't need another _S_() object
            settings = { "trailer_amt_db_file":  xbmc.translatePath( _S_( "trailer_amt_db_file" ) ) }
            # handle AMT db special
            from resources.scrapers.amt_database import scraper as scraper
            Scraper = scraper.Main( settings=settings )
            # update trailers
            Scraper.clear_watched()
            # set base watched file path
            base_paths += [ os.path.join( self.BASE_CURRENT_SOURCE_PATH, "amt_current_watched.txt" ) ]
            base_paths += [ os.path.join( self.BASE_CURRENT_SOURCE_PATH, "local_watched.txt" ) ]
        else:
            # set base watched file path
            base_paths = [ os.path.join( self.BASE_CURRENT_SOURCE_PATH, "trivia_watched.txt" ) ]
        try:
            # set proper message
            message = ( 32531, 32541, )[ sys.argv[ 1 ] == "ClearWatchedTrailers" ]
            # remove watched status file(s)
            for base_path in base_paths:
                # remove file if it exists
                if ( os.path.isfile( base_path ) ):
                    os.remove( base_path )
        except:
            # set proper message
            message = ( 32532, 32542, )[ sys.argv[ 1 ] == "ClearWatchedTrailers" ]
        # close main dialog
        pDialog.close()
        # inform user of result
        ok = xbmcgui.Dialog().ok( _L_( 32000 ), _L_( message ) )

    def _view_changelog( self ):
        xbmc.log( "_view_changelog()", xbmc.LOGNOTICE )

    def _view_readme( self ):
        xbmc.log( "_view_readme()", xbmc.LOGNOTICE )

    def _create_playlist( self ):
        # get the queued video info
        mpaa, audio, genre, movie = self._get_queued_video_info()
        # TODO: try to get a local thumb for special videos?
        # get Dolby/DTS videos
        if ( _S_( "audio_videos_folder" ) ):
            self._get_special_items(    playlist=self.playlist,
                                                    items=1 * ( _S_( "audio_videos_folder" ) != "" ),
                                                    path=xbmc.translatePath( _S_( "audio_videos_folder" ) ) + { "dca": "DTS", "ac3": "Dolby" }.get( audio, "Other" ) + xbmc.translatePath( _S_( "audio_videos_folder" ) )[ -1 ],
                                                    genre=_L_( 32606 ),
                                                    ##thumbnail=xbmc.translatePath( _S_( "audio_videos_folder" ) ) + { "dca": "DTS", "ac3": "Dolby" }.get( audio, "Other" ) + xbmc.translatePath( _S_( "audio_videos_folder" ) )[ -1 ] + "folder.jpg",
                                                    index=0
                                                )
        # get rating video
        self._get_special_items(    playlist=self.playlist,
                                                items=1 * ( _S_( "rating_videos_folder" ) != "" ), 
                                                path=xbmc.translatePath( _S_( "rating_videos_folder" ) ) + mpaa + ".avi",
                                                genre=_L_( 32603 ),
                                                index=0
                                            )
        # get feature presentation intro videos
        self._get_special_items(    playlist=self.playlist,
                                                items=( 0, 1, 1, 2, 3, 4, 5, )[ int( _S_( "fpv_intro" ) ) ], 
                                                path=( xbmc.translatePath( _S_( "fpv_intro_file" ) ), xbmc.translatePath( _S_( "fpv_intro_folder" ) ), )[ int( _S_( "fpv_intro" ) ) > 1 ],
                                                genre=_L_( 32601 ),
                                                index=0
                                            )
        # get trailers
        trailers = self._get_trailers(  items=( 0, 1, 2, 3, 4, 5, 10, )[ int( _S_( "trailer_count" ) ) ],
                                                   mpaa=mpaa,
                                                   genre=genre,
                                                   movie=movie
                                                )
        # get coming attractions outro videos
        self._get_special_items(    playlist=self.playlist,
                                                items=( 0, 1, 1, 2, 3, 4, 5, )[ int( _S_( "cav_outro" ) ) ] * ( len( trailers ) > 0 ), 
                                                path=( xbmc.translatePath( _S_( "cav_outro_file" ) ), xbmc.translatePath( _S_( "cav_outro_folder" ) ), )[ int( _S_( "cav_outro" ) ) > 1 ],
                                                genre=_L_( 32608 ),
                                                index=0
                                            )
        # enumerate through our list of trailers and add them to our playlist
        for trailer in trailers:
            # get trailers
            self._get_special_items(    playlist=self.playlist,
                                                    items=1,
                                                    path=trailer[ 2 ],
                                                    genre=trailer[ 9 ] or _L_( 32605 ),
                                                    title=trailer[ 1 ],
                                                    thumbnail=trailer[ 3 ],
                                                    plot=trailer[ 4 ],
                                                    runtime=trailer[ 5 ],
                                                    mpaa=trailer[ 6 ],
                                                    release_date=trailer[ 7 ],
                                                    studio=trailer[ 8 ] or _L_( 32604 ),
                                                    writer=trailer[ 10 ],
                                                    director=trailer[ 11 ],
                                                    index=0
                                                )
        # get coming attractions intro videos
        self._get_special_items(    playlist=self.playlist,
                                                items=( 0, 1, 1, 2, 3, 4, 5, )[ int( _S_( "cav_intro" ) ) ] * ( len( trailers ) > 0 ), 
                                                path=( xbmc.translatePath( _S_( "cav_intro_file" ) ), xbmc.translatePath( _S_( "cav_intro_folder" ) ), )[ int( _S_( "cav_intro" ) ) > 1 ],
                                                genre=_L_( 32600 ),
                                                index=0
                                            )
        # get movie theater experience intro videos
        self._get_special_items(    playlist=self.playlist,
                                                items=( 0, 1, 1, 2, 3, 4, 5, )[ int( _S_( "mte_intro" ) ) ], 
                                                path=( xbmc.translatePath( _S_( "mte_intro_file" ) ), xbmc.translatePath( _S_( "mte_intro_folder" ) ), )[ int( _S_( "mte_intro" ) ) > 1 ],
                                                genre=_L_( 32607 ),
                                                index=0
                                            )
        # get feature presentation outro videos
        self._get_special_items(    playlist=self.playlist,
                                                items=( 0, 1, 1, 2, 3, 4, 5, )[ int( _S_( "fpv_outro" ) ) ], 
                                                path=( xbmc.translatePath( _S_( "fpv_outro_file" ) ), xbmc.translatePath( _S_( "fpv_outro_folder" ) ), )[ int( _S_( "fpv_outro" ) ) > 1 ],
                                                genre=_L_( 32602 ),
                                            )
        # get movie theater experience outro videos
        self._get_special_items(    playlist=self.playlist,
                                                items=( 0, 1, 1, 2, 3, 4, 5, )[ int( _S_( "mte_outro" ) ) ], 
                                                path=( xbmc.translatePath( _S_( "mte_outro_file" ) ), xbmc.translatePath( _S_( "mte_outro_folder" ) ), )[ int( _S_( "mte_outro" ) ) > 1 ],
                                                genre=_L_( 32607 ),
                                            )
        return mpaa

    def _get_queued_video_info( self ):
        try:
            xbmc.log( "_get_queued_video_info()", xbmc.LOGNOTICE )
            # clear then queue the currently selected video
            xbmc.executebuiltin( "Playlist.Clear" )
            xbmc.executebuiltin( "Action(Queue,%d)" % ( xbmcgui.getCurrentWindowId() - 10000, ) )
            xbmc.log( "Action(Queue,%d)" % ( xbmcgui.getCurrentWindowId() - 10000, ), xbmc.LOGNOTICE )
            # we need to sleep so the video gets queued properly
            xbmc.sleep( 300 )
            # create a video playlist
            self.playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
            # get movie name
            movie_title = self.playlist[ 0 ].getdescription()
            # this is used to skip trailer for current movie selection
            movie = os.path.splitext( os.path.basename( self.playlist[ 0 ].getfilename() ) )[ 0 ]
            # format our records start and end
            xbmc.executehttpapi( "SetResponseFormat()" )
            xbmc.executehttpapi( "SetResponseFormat(OpenField,)" )
            # TODO: verify the first is the best audio
            # setup the sql, we limit to 1 record as there can be multiple entries in streamdetails
            sql = "SELECT movie.c12, movie.c14, streamdetails.strAudioCodec FROM movie, streamdetails WHERE movie.idFile=streamdetails.idFile AND streamdetails.iStreamType=1 AND c00='%s' LIMIT 1" % ( movie_title.replace( "'", "''", ), )
            xbmc.log( "SQL: %s" % ( sql, ), xbmc.LOGNOTICE )
            # query database for info dummy is needed as there are two </field> formatters
            mpaa, genre, audio, dummy = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % quote_plus( sql ), ).split( "</field>" )
            # TODO: add a check and new sql for videos queued from files mode, or try an nfo
            # calculate rating
            mpaa = mpaa.split( " " )[ 1 - ( len( mpaa.split( " " ) ) == 1 ) ]
            mpaa = ( mpaa, "NR", )[ mpaa not in ( "G", "PG", "PG-13", "R", "NC-17", "Unrated", ) ]
        except:
            mpaa = audio = genre = movie = ""
        # spew queued video info to log
        xbmc.log( "-" * 70, xbmc.LOGNOTICE )
        xbmc.log( "Title: %s" % ( movie_title, ), xbmc.LOGNOTICE )
        xbmc.log( "Path: %s" % ( movie, ), xbmc.LOGNOTICE )
        xbmc.log( "Genre: %s" % ( genre, ), xbmc.LOGNOTICE )
        xbmc.log( "MPAA: %s" % ( mpaa, ), xbmc.LOGNOTICE )
        xbmc.log( "Audio: %s" % ( audio, ), xbmc.LOGNOTICE )
        if ( _S_( "audio_videos_folder" ) ):
            xbmc.log( "- Folder: %s" % ( xbmc.translatePath( _S_( "audio_videos_folder" ) ) + { "dca": "DTS", "ac3": "Dolby" }.get( audio, "Other" ) + xbmc.translatePath( _S_( "audio_videos_folder" ) )[ -1 ], ), xbmc.LOGNOTICE )
        xbmc.log( "-" * 70, xbmc.LOGNOTICE )
        # return results
        return mpaa, audio, genre, movie

    def _get_special_items(   self, playlist, items, path, genre, title="", thumbnail=None, plot="",
                                                runtime="", mpaa="", release_date="0 0 0", studio="", writer="",
                                                director="", index=-1, media_type="video"
                                            ):
        # return if not user preference
        if ( not items ):
            return
        # if path is a file check if file exists
        if ( os.path.splitext( path )[ 1 ] and not path.startswith( "http://" ) and not ( xbmc.executehttpapi( "FileExists(%s)" % ( path, ) ) == "<li>True" ) ):
            return
        # set default paths list
        self.tmp_paths = [ path ]
        # if path is a folder fetch # videos/pictures
        if ( path.endswith( "/" ) or path.endswith( "\\" ) ):
            # initialize our lists
            self.tmp_paths = []
            self._get_items( [ path ], media_type )
            shuffle( self.tmp_paths )
        # enumerate thru and add our videos/pictures
        for count in range( items ):
            # set our path
            path = self.tmp_paths[ count ]
            # format a title (we don't want the ugly extension)
            title = title or os.path.splitext( os.path.basename( path ) )[ 0 ]
            # create the listitem and fill the infolabels
            listitem = self._get_listitem( title=title,
                                                        url=path,
                                                        thumbnail=thumbnail,
                                                        plot=plot,
                                                        runtime=runtime,
                                                        mpaa=mpaa,
                                                        release_date=release_date,
                                                        studio=studio or _L_( 32604 ),
                                                        genre=genre or _L_( 32605 ),
                                                        writer=writer,
                                                        director=director
                                                    )
            # add our video/picture to the playlist or list
            if ( isinstance( playlist, list ) ):
                playlist += [ ( path, listitem, ) ]
            else:
                playlist.add( path, listitem, index=index )

    def _get_items( self, paths, media_type ):
        # reset folders list
        folders = []
        # enumerate thru paths and fetch videos/pictures recursively
        for path in paths:
            # get the directory listing
            entries = xbmc.executehttpapi( "GetDirectory(%s)" % ( path, ) ).split( "\n" )
            # enumerate through our entries list and check for valid media type
            for entry in entries:
                # remove <li> from item
                entry = entry.replace( "<li>", "" )
                # if folder add to our folder list to recursively fetch videos/pictures
                if ( entry.endswith( "/" ) or entry.endswith( "\\" ) ):
                    folders += [ entry ]
                # is this a valid video/picture file
                elif ( entry and ( ( media_type.startswith( "video" ) and os.path.splitext( entry )[ 1 ] in xbmc.getSupportedMedia( "video" ) ) or
                    ( media_type.endswith( "picture" ) and os.path.splitext( entry )[ 1 ] in xbmc.getSupportedMedia( "picture" ) ) ) ):
                    # add our entry
                    self.tmp_paths += [ entry ]
        # if there are folders call again (we want recursive)
        if ( folders ):
            self._get_items( folders, media_type )

    def _get_trailers( self, items, mpaa, genre, movie ):
        # return if not user preference
        if ( not items ):
            return []
        # update dialog
        pDialog.update( -1, _L_( 32500 ) )
        # trailer settings, grab them here so we don't need another _S_() object
        settings = { "trailer_amt_db_file":  xbmc.translatePath( _S_( "trailer_amt_db_file" ) ),
                            "trailer_folder":  xbmc.translatePath( _S_( "trailer_folder" ) ),
                            "trailer_rating": _S_( "trailer_rating" ),
                            "trailer_limit_query": _S_( "trailer_limit_query" ) == "true",
                            "trailer_play_mode": int( _S_( "trailer_play_mode" ) ),
                            "trailer_hd_only": _S_( "trailer_hd_only" ) == "true",
                            "trailer_quality": int( _S_( "trailer_quality" ) ),
                            "trailer_unwatched_only": _S_( "trailer_unwatched_only" ) == "true",
                            "trailer_newest_only": _S_( "trailer_newest_only" ) == "true",
                            "trailer_count": ( 0, 1, 2, 3, 4, 5, 10, )[ int( _S_( "trailer_count" ) ) ],
                            "trailer_scraper": ( "amt_database", "amt_current", "local", )[ int( _S_( "trailer_scraper" ) ) ]
                        }
        # get the correct scraper
        exec "from resources.scrapers.%s import scraper as scraper" % ( settings[ "trailer_scraper" ], )
        Scraper = scraper.Main( mpaa, genre, settings, movie )
        # fetch trailers
        trailers = Scraper.fetch_trailers()
        # return results
        return trailers

    def _get_listitem( self, title="", url="", thumbnail=None, plot="", runtime="", mpaa="", release_date="0 0 0", studio=_L_( 32604 ), genre="", writer="", director=""):
        # check for a valid thumbnail
        thumbnail = self._get_thumbnail( ( thumbnail, url, )[ thumbnail is None ] )
        # set the default icon
        icon = "DefaultVideo.png"
        # only need to add label, icon and thumbnail, setInfo() and addSortMethod() takes care of label2
        listitem = xbmcgui.ListItem( title, iconImage=icon, thumbnailImage=thumbnail )
        # release date and year
        try:
            parts = release_date.split( " " )
            year = int( parts[ 2 ] )
        except:
            year = 0
        # add the different infolabels we want to sort by
        listitem.setInfo( type="Video", infoLabels={ "Title": title, "Plot": plot, "PlotOutline": plot, "RunTime": runtime, "MPAA": mpaa, "Year": year, "Studio": studio, "Genre": genre, "Writer": writer, "Director": director } )
        # return result
        return listitem

    def _get_thumbnail( self, url ):
        print url
        # if the cached thumbnail does not exist create the thumbnail based on filepath.tbn
        filename = xbmc.getCacheThumbName( url )
        thumbnail = os.path.join( self.BASE_CACHE_PATH, filename[ 0 ], filename )
        print filename
        # if cached thumb does not exist try auto generated
        if ( not os.path.isfile( thumbnail ) ):
            thumbnail = os.path.join( self.BASE_CACHE_PATH, filename[ 0 ], "auto-" + filename )
        # if cached thumb does not exist set default
        if ( not os.path.isfile( thumbnail ) ):
            thumbnail = "DefaultVideo.png"
        # return result
        return thumbnail

    def _play_trivia( self, mpaa ):
        # if user cancelled dialog return
        if ( pDialog.iscanceled() ):
            pDialog.close()
            return
        # if trivia path and time to play the trivia slides
        if ( _S_( "trivia_folder" ) and int( _S_( "trivia_total_time" ) ) > 0 ):
            # update dialog with new message
            pDialog.update( -1, _L_( 32510 ) )
            # initialize intro/outro lists
            playlist_intro = []
            playlist_outro = []
            # get trivia intro videos
            self._get_special_items(    playlist=playlist_intro,
                                                    items=( 0, 1, 1, 2, 3, 4, 5, )[ int( _S_( "trivia_intro" ) ) ], 
                                                    path=( xbmc.translatePath( _S_( "trivia_intro_file" ) ), xbmc.translatePath( _S_( "trivia_intro_folder" ) ), )[ int( _S_( "trivia_intro" ) ) > 1 ],
                                                    genre=_L_( 32609 ),
                                                    media_type="video/picture"
                                                )
            # get trivia outro videos
            self._get_special_items(    playlist=playlist_outro,
                                                    items=( 0, 1, 1, 2, 3, 4, 5, )[ int( _S_( "trivia_outro" ) ) ], 
                                                    path=( xbmc.translatePath( _S_( "trivia_outro_file" ) ), xbmc.translatePath( _S_( "trivia_outro_folder" ) ), )[ int( _S_( "trivia_outro" ) ) > 1 ],
                                                    genre=_L_( 32610 ),
                                                    media_type="video/picture"
                                                )
            # trivia settings, grab them here so we don't need another _S_() object
            settings = {  "trivia_total_time": ( 0, 5, 10, 15, 20, 30, 45, 60 )[ int( _S_( "trivia_total_time" ) ) ],
                                "trivia_folder":  xbmc.translatePath( _S_( "trivia_folder" ) ),
                                "trivia_slide_time": ( 5, 10, 15, 20, 30, )[ int( _S_( "trivia_slide_time" ) ) ],
                                "trivia_intro_playlist": playlist_intro,
                                "trivia_outro_playlist": playlist_outro,
                                "trivia_music_file":  xbmc.translatePath( _S_( "trivia_music_file" ) ),
                                "trivia_music_volume": int( _S_( "trivia_music_volume" ).replace( "%", "" ) ),
                                "trivia_unwatched_only": _S_( "trivia_unwatched_only" ) == "true"
                            }
            # set the proper mpaa rating user preference
            mpaa = (  _S_( "trivia_rating" ), mpaa, )[ _S_( "trivia_limit_query" ) == "true" ]
            print "MPAA", mpaa
            # import trivia module and execute the gui
            from resources.lib.xbmcscript_trivia import Trivia as Trivia
            ui = Trivia( "script-HTExperience-trivia.xml", os.getcwd(), "default", False, settings=settings, playlist=self.playlist, dialog=pDialog, mpaa=mpaa )
            #ui.doModal()
            del ui
            # we need to activate the video window
            xbmc.executebuiltin( "XBMC.ActivateWindow(2005)" )
        else:
            # no trivia slide show so play the video
            pDialog.close()
            # play the video playlist
            xbmc.Player().play( self.playlist )
