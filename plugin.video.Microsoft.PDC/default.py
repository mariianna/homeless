##############################################################################
#
# Microsoft PDC - XBMC video plugin
# http://www.microsoftpdc.com
#
# Version 1.0
# 
# Coding by Dan Dar3 
# http://dandar3.blogspot.com
#
#
# Credits:
#   * MicrosoftPDC.com                                                  [http://www.microsoftpdc.com]
#   * Team XBMC4Xbox @ XBMC4Xbox.org                                    [http://xbmc4xbox.org/]
#   * Fredrik Lundh <fredrik@pythonware.com> - ElementTree              [http://www.pythonware.com]
#   * Eric Lawrence <e_lawrence@hotmail.com>     - Fiddler Web Debugger [http://www.fiddler2.com]
#

# 
# Constants
#
__plugin__  = "Microsoft PDC"
__author__  = "Dan Dar3"
__url__     = "http://dandar3.blogspot.com"
__date__    = "25 December 2010"
__version__ = "1.0"

#
# Imports
#
import os
import sys

LIB_DIR = xbmc.translatePath( os.path.join( os.getcwd(), 'resources', 'lib' ) )
sys.path.append (LIB_DIR)

#
# Sessions (list)
#
if ( "action=sessions" in sys.argv[ 2 ] ):
    import microsoft_pdc_sessions as plugin
#
#
#
elif ( "action=play" in sys.argv[ 2 ] ):
    import microsoft_pdc_play as plugin
#
# Categories (list)
#
else :
    xbmc.log( "[PLUGIN] %s v%s (%s)" % ( __plugin__, __version__, __date__ ), xbmc.LOGNOTICE )
    import microsoft_pdc_categories as plugin

plugin.Main()
