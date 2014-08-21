# LRC Lyrics script revision:  - built with build.bat version 1.0 #

# main import's 
import sys
import os
import xbmc
import xbmcaddon

# Script constants 
__newscriptname__ = "LRC Lyrics"
__scriptname__ = "XBMC Lyrics"
__author__ = "XBMC Lyrics Team"
__url__ = "http://code.google.com/p/xbmc-scripting/"
__svn_url__ = "http://xbmc-scripting.googlecode.com/svn/trunk/"
__credits__ = "XBMC TEAM, freenode/#xbmc-scripting"
__version__ = "1.3.0"
__svn_revision__ = ""

# Shared resources 
BASE_RESOURCE_PATH = os.path.join( os.getcwd(), "resources" )
__addonID__ = "script.xbmc-korea.lyrics"
__settings__ = xbmcaddon.Addon( id=__addonID__ )
__language__ = __settings__.getLocalizedString

# Main team credits 
__credits_l1__ = __language__( 910 )#"Head Developer & Coder"
__credits_r1__ = "Taxigps"
__credits_l2__ = __language__( 911 )#"Original author"
__credits_r2__ = "Nuka1195 & EnderW"
__credits_l3__ = __language__( 912 )#"Original skinning"
__credits_r3__ = "Smuto"

# additional credits 
__add_credits_l1__ = __language__( 1 )#"Xbox Media Center"
__add_credits_r1__ = "Team XBMC"
__add_credits_l2__ = __language__( 913 )#"Unicode support"
__add_credits_r2__ = "Spiff"
__add_credits_l3__ = __language__( 914 )#"Language file"
__add_credits_r3__ = __language__( 2 )#"Translators name"


# Start the main gui or settings gui 
if ( __name__ == "__main__" ):
    import resources.lib.gui as gui
    ui = gui.GUI( "script-%s-main.xml" % __scriptname__.replace( " ", "_" ), os.getcwd(), "Default" )
    ui.doModal()
    del ui
    sys.modules.clear()
    
