# -*- coding: utf-8 -*-

"""
    Flickr api client module
"""

# main imports
import sys
import os
import urllib
import md5

try:
    import xbmc
    import xbmcgui
    DEBUG = False
except:
    DEBUG = True

class FlickrClient:
    # base url's
    BASE_URL_REST = u"http://api.flickr.com/services/rest/"
    BASE_URL_AUTH = u"http://api.flickr.com/services/auth/"
    BASE_URL_UPLOAD = u"http://api.flickr.com/services/upload/"
    BASE_URL_REPLACE = u"http://api.flickr.com/services/replace/"

    # developers api key and shared secret
    FLICKR_API_KEY = u"%s" % ( str( [ chr( c ) for c in ( 56, 52, 97, 100, 48, 101, 54, 57, 50, 98, 50, 52, 54, 55, 48, 56, 99, 56, 99, 98, 55, 101, 97, 48, 55, 98, 53, 54, 102, 52, 48, 56, ) ] ).replace( "'", "" ).replace( ", ", "" )[ 1 : -1 ], )
    FLICKR_SHARED_SECRET = u"%s" % ( str( [ chr( c ) for c in ( 48, 57, 55, 53, 99, 56, 55, 97, 50, 101, 57, 52, 99, 56, 51, 101, ) ] ).replace( "'", "" ).replace( ", ", "" )[ 1 : -1 ], )

    def __init__( self, api_key=False, secret=False ):
        # developers api key and shared secret
        self.secret = None
        if ( api_key ):
            self.api_key = self.FLICKR_API_KEY
        if ( secret ):
            self.secret = self.FLICKR_SHARED_SECRET

    def __getattr__( self, method ):
        def method( _method=method, **params ):
            try:
                # json uses null instead of None, true instead of True and false instead of False (should be faster than replace()
                true = True
                false = False
                null = None
                # add api_key to our params dictionary
                params[ "api_key" ] = self.api_key
                # change _method to the format flickr expects and add method to our params dictionary
                params[ "method" ] = _method.replace( "_", "." )
                # add format to our params dictionary (we use json format as it's basically a native python dictionary)
                params[ "format" ] = "json"
                # we don't need the function wrapper
                params[ "nojsoncallback" ] = 1
                # add api_sig to our params dictionary
                if ( self.secret is not None ):
                    params[ "api_sig" ] = self._signature( params )
                # open url
                usock = urllib.urlopen( self.BASE_URL_REST, urllib.urlencode( params ) )
                # read source
                jsonSource = usock.read()
                # close socket
                usock.close()
                # eval jsonSource to a native python dictionary
                return eval( jsonSource.replace( "\\/", "/" ) )
            except:
                # oops return an empty dictionary
                print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
                return {}
        return method

    def _signature( self, params ):
        # add our shared secret to our signature string
        signature = self.secret
        # get our keys and sort them(required by flickr)
        keys = params.keys()
        keys.sort()
        #enumerate thru our keys and concatenate key, value to our signature string
        for key in keys:
            signature += u"%s%s" % ( key, str( params[ key ] ), )
        # return our md5 hash
        return md5.new( signature ).hexdigest()

    def authenticate( self ):
        # request a frob
        frob = self.flickr_auth_getfrob()
        # if successful finish authenticating
        if ( frob[ "stat" ] == "ok" ):
            # create our params dictionary
            params = { "api_key": self.api_key, "perms": "delete", "frob": frob[ "frob" ][ "_content" ] }
            # add api_sig to our params dictionary
            params[ "api_sig" ] = self._signature( params )
            # create our url
            url = u"%s?%s" % ( self.BASE_URL_AUTH, urllib.urlencode( params ), )
            # spam url for xbox and ATV
            print "XBMC Flicker authorization url: %s" % ( url, )
            try:
                # we handle xboix differnetly
                if ( os.environ.get( "OS", "n/a" ) == "xbox" ):
                    ok = xbmcgui.Dialog().yesno( xbmc.getLocalizedString( 30907 ), xbmc.getLocalizedString( 30915 ), "", "", xbmc.getLocalizedString( 30913 ), xbmc.getLocalizedString( 30914 ) )
                elif ( os.environ.get( "OS", "n/a" ) == "OS X" ):
                    # osx needs special handling
                    os.system( "open \"%s\"" % ( url, ) )
                else:
                    # open our webbrowser for user authentication
                    import webbrowser
                    webbrowser.open( url )
            except:
                pass
            # get response from user
            if ( DEBUG ):
                ok = raw_input( "Have you authenticated this application? (Y/N): " )
            else:
                ok = xbmcgui.Dialog().yesno( xbmc.getLocalizedString( 30907 ), xbmc.getLocalizedString( 30912 ), "", "", xbmc.getLocalizedString( 30913 ), xbmc.getLocalizedString( 30914 ) )
            # return token
            if ( ok ):
                # get token
                authtoken = self.flickr_auth_getToken( frob=frob[ "frob" ][ "_content" ] )
                # if successful return token
                if ( authtoken[ "stat" ] == "ok" ):
                    return authtoken[ "auth" ][ "token" ][ "_content" ]
        return ""
