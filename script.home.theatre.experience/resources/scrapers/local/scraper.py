"""
Local trailer scraper
"""
# TODO: add watched.xml to skip watched trailers

import os
import xbmc
from random import shuffle


class Main:
    # base paths
    BASE_CURRENT_SOURCE_PATH = os.path.join( xbmc.translatePath( "special://profile/" ), "script_data", os.path.basename( os.getcwd() ) )

    def __init__( self, mpaa=None, genre=None, settings=None, movie=None ):
        self.mpaa = mpaa
        self.genre = genre
        self.settings = settings
        self.movie = movie
        self.trailers = []
        self.tmp_trailers = []

    def fetch_trailers( self ):
        # get watched list
        self._get_watched()
        # fetch all trailers recursively
        self._fetch_trailers( [ self.settings[ "trailer_folder" ] ] )
        # get a random number of trailers
        self._shuffle_trailers()
        # save watched list
        self._save_watched()
        # return results
        return self.trailers

    def _fetch_trailers( self, paths ):
        # reset folders list
        folders = []
        # enumerate thru paths and fetch slides recursively
        for path in paths:
            # get the directory listing
            entries = xbmc.executehttpapi( "GetDirectory(%s)" % ( path, ) ).split( "\n" )
            # enumerate through our entries list and separate question, clue, answer
            for entry in entries:
                # remove <li> from item
                entry = entry.replace( "<li>", "" )
                # if folder add to our folder list to recursively fetch slides
                if ( entry.endswith( "/" ) or entry.endswith( "\\" ) ):
                    folders += [ entry ]
                # does this entry match our pattern "-trailer." and is a video file
                elif ( "-trailer." in entry and os.path.splitext( entry )[ 1 ] in xbmc.getSupportedMedia( "video" ) and ( self.movie != os.path.splitext( os.path.basename( entry ).replace( "-trailer", "" ) )[ 0 ] ) ):
                    # add our entry
                    self.tmp_trailers += [ entry ]
        # if there are folders call again (we want recursive)
        if ( folders ):
            self._fetch_trailers( folders )

    def _shuffle_trailers( self ):
        # randomize the groups and create our play list
        shuffle( self.tmp_trailers )
        # reset counter
        count = 0
        # now create our final playlist
        for trailer in self.tmp_trailers:
            # user preference to skip watch trailers
            if ( self.settings[ "trailer_newest_only" ] and xbmc.getCacheThumbName( trailer ) in self.watched ):
                continue
            # add id to watched file TODO: maybe don't add if not user preference
            self.watched += [ xbmc.getCacheThumbName( trailer ) ]
            # add trailer to our final list
            self.trailers += [ self._set_trailer_info( trailer ) ]
            # increment counter
            count += 1
            # if we have enough exit
            if ( count == self.settings[ "trailer_count" ] ):
                break

    def _set_trailer_info( self, trailer ):
        result = ( xbmc.getCacheThumbName( trailer ), # id
                        os.path.basename( trailer ).split( "-trailer." )[ 0 ], # title
                        trailer, # trailer
                        self._get_thumbnail( trailer ), # thumb
                        "", # plot
                        "", # runtime
                        "", # mpaa
                        "", # release date
                        "", # studio
                        "", # genre
                        "", # writer
                        "", # director
                        )
        return result

    def _get_thumbnail( self, path ):
        # check for a thumb based on trailername.tbn
        thumbnail = os.path.splitext( path )[ 0 ] + ".tbn" 
        # if thumb does not exist try stripping -trailer
        if ( not xbmc.executehttpapi( "FileExists(%s)" % ( thumbnail, ) ) == "<li>True" ):
            thumbnail = "%s.tbn" % ( os.path.splitext( path )[ 0 ].replace( "-trailer", "" ), )
            # if thumb does not exist return empty
            if ( not xbmc.executehttpapi( "FileExists(%s)" % ( thumbnail, ) ) == "<li>True" ):
                # set empty string
                thumbnail = None
        # return result
        return thumbnail

    def _get_watched( self ):
        try:
            # base path to watched file
            base_path = os.path.join( self.BASE_CURRENT_SOURCE_PATH, self.settings[ "trailer_scraper" ] + "_watched.txt" )
            # open path
            usock = open( base_path, "r" )
            # read source
            self.watched = eval( usock.read() )
            # close socket
            usock.close()
        except:
            self.watched = []

    def _save_watched( self ):
        try:
            # base path to watched file
            base_path = os.path.join( self.BASE_CURRENT_SOURCE_PATH, self.settings[ "trailer_scraper" ] +"_watched.txt" )
            # if the path to the source file does not exist create it
            if ( not os.path.isdir( os.path.dirname( base_path ) ) ):
                os.makedirs( os.path.dirname( base_path ) )
            # open source path for writing
            file_object = open( base_path, "w" )
            # write xmlSource
            file_object.write( repr( self.watched ) )
            # close file object
            file_object.close()
        except:
            pass
