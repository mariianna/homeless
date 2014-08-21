import xbmc, xbmcgui, time, threading, datetime, os, urllib, httplib, sys, glob, random, traceback

try: Emulating = xbmcgui.Emulating
except: Emulating = False

# Script constants
__scriptname__ = "XBMC Earth"
__author__ = "MrLight"
__version__ = "0.41"
__date__ = '09-01-2009'
xbmc.output(__scriptname__ + " Version: " + __version__ + " Date: " + __date__)


# Shared resources

BASE_RESOURCE_PATH = os.path.join( os.getcwd().replace( ";", "" ), "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

__language__ = xbmc.Language( os.getcwd() ).getLocalizedString 

from threading import Thread

from googleearth_coordinates import  Googleearth_Coordinates
from xbmcearth_communication import *
import pic


glob_player =  ''



