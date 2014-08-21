
import sys
import os
import xbmcgui
import xbmc
import urllib

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__version__ = sys.modules[ "__main__" ].__version__
BASE_RESOURCE_PATH = os.path.join( os.getcwd().replace( ";", "" ), "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
__language__ = xbmc.Language( os.getcwd() ).getLocalizedString 

from xbmcearth_communication import *
from global_data import *

class GUI( xbmcgui.WindowXMLDialog ):
	xbmcearth_communication = Xbmcearth_communication()
	""" Settings module: used for changing settings """
	def __init__( self, *args, **kwargs ):
		xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
		self.MainWindow = kwargs[ "mainWindow" ]
		self.doModal()
		
	def onInit( self ):
		self.getControl( 500 ).setLabel( __language__( 10009 ) )
		self.getControl( 501 ).setLabel( __language__( 10010 ) )
		self.getControl( 100 ).setLabel( self.MainWindow.set.settings["fav"][0]["name"] )
		self.getControl( 101 ).setLabel( self.MainWindow.set.settings["fav"][1]["name"]  )
		self.getControl( 102 ).setLabel( self.MainWindow.set.settings["fav"][2]["name"]  )
		self.getControl( 103 ).setLabel( __language__( 10011 ) )
		self.getControl( 1000 ).setLabel( "set" )
		self.getControl( 1001 ).setLabel( "set" )
		self.getControl( 1002 ).setLabel( "set" )
		pass
		
	def onClick( self, controlId ):
		if controlId == 99:
			self._close_dialog()
		elif controlId == 100:
			self.MainWindow.lon  = self.MainWindow.set.settings["fav"][0]["lon"]
			self.MainWindow.lat  = self.MainWindow.set.settings["fav"][0]["lat"]
			self.MainWindow.zoom = self.MainWindow.set.settings["fav"][0]["zoom"]
			self.xbmcearth_communication.get_Google_Analytics( referer_url,  urllib.quote("Goto Favorite 1 - " + str(self.MainWindow.set.settings["fav"][0]["name"])), urllib.quote("/xbmc_earth/goto_favorite1.html"),self.MainWindow)
			self.MainWindow.drawSAT()
		elif controlId == 101:
			self.MainWindow.lon  = self.MainWindow.set.settings["fav"][1]["lon"]
			self.MainWindow.lat  = self.MainWindow.set.settings["fav"][1]["lat"]
			self.MainWindow.zoom = self.MainWindow.set.settings["fav"][1]["zoom"]
			self.xbmcearth_communication.get_Google_Analytics( referer_url,  urllib.quote("Goto Favorite 2 - " + str(self.MainWindow.set.settings["fav"][1]["name"])), urllib.quote("/xbmc_earth/goto_favorite2.html"),self.MainWindow)
			self.MainWindow.drawSAT()
		elif controlId == 102:
			self.MainWindow.lon  = self.MainWindow.set.settings["fav"][2]["lon"]
			self.MainWindow.lat  = self.MainWindow.set.settings["fav"][2]["lat"]
			self.MainWindow.zoom = self.MainWindow.set.settings["fav"][2]["zoom"]
			self.xbmcearth_communication.get_Google_Analytics( referer_url,  urllib.quote("Goto Favorite 3 - " + str(self.MainWindow.set.settings["fav"][2]["name"])), urllib.quote("/xbmc_earth/goto_favorite3.html"),self.MainWindow)
			self.MainWindow.drawSAT()
		elif controlId == 1000:
			keyboard = xbmc.Keyboard()
			keyboard.setHeading(__language__( 10006 ))
			keyboard.doModal()
			if keyboard.isConfirmed():
				self.MainWindow.set.settings["fav"][0]["name"] = keyboard.getText()
				self.MainWindow.set.settings["fav"][0]["lon"] = self.MainWindow.lon
				self.MainWindow.set.settings["fav"][0]["lat"] = self.MainWindow.lat
				self.MainWindow.set.settings["fav"][0]["zoom"] = self.MainWindow.zoom
				self.getControl( 100 ).setLabel( self.MainWindow.set.settings["fav"][0]["name"] )
				self.xbmcearth_communication.get_Google_Analytics( referer_url,  urllib.quote("Set Favorite 1" + str(self.MainWindow.set.settings["fav"][0]["name"])), urllib.quote("/xbmc_earth/set_favorite1.html"),self.MainWindow)
		elif controlId == 1001:
			keyboard = xbmc.Keyboard()
			keyboard.setHeading(__language__( 10007 ))
			keyboard.doModal()
			if keyboard.isConfirmed():
				self.MainWindow.set.settings["fav"][1]["name"] = keyboard.getText()
				self.MainWindow.set.settings["fav"][1]["lon"] = self.MainWindow.lon
				self.MainWindow.set.settings["fav"][1]["lat"] = self.MainWindow.lat
				self.MainWindow.set.settings["fav"][1]["zoom"] = self.MainWindow.zoom
				self.getControl( 101 ).setLabel( self.MainWindow.set.settings["fav"][1]["name"]  )
				self.xbmcearth_communication.get_Google_Analytics( referer_url,  urllib.quote("Set Favorite 2" + str(self.MainWindow.set.settings["fav"][1]["name"])), urllib.quote("/xbmc_earth/set_favorite2.html"),self.MainWindow)
		elif controlId == 1002:
			keyboard = xbmc.Keyboard()
			keyboard.setHeading(__language__( 10008 ))
			keyboard.doModal()
			if keyboard.isConfirmed():
				self.MainWindow.set.settings["fav"][2]["name"] = keyboard.getText()
				self.MainWindow.set.settings["fav"][2]["lon"] = self.MainWindow.lon
				self.MainWindow.set.settings["fav"][2]["lat"] = self.MainWindow.lat
				self.MainWindow.set.settings["fav"][2]["zoom"] = self.MainWindow.zoom
				self.getControl( 102 ).setLabel( self.MainWindow.set.settings["fav"][2]["name"]  )
				self.xbmcearth_communication.get_Google_Analytics( referer_url,  urllib.quote("Set Favorite 3" + str(self.MainWindow.set.settings["fav"][2]["name"])), urllib.quote("/xbmc_earth/set_favorite3.html"),self.MainWindow)	
		elif controlId == 103:
			self.MainWindow.getControl(2003).setVisible(True)
			self.MainWindow.show_weather = True
			self.xbmcearth_communication.get_Google_Analytics( referer_url,  urllib.quote("Show Weather"), urllib.quote("/xbmc_earth/weather.html"),self.MainWindow)	
			self.MainWindow.drawSAT()
		
	def onFocus( self, controlId ):
		pass
		
	def onAction( self, action ):
	
		if ( action in ACTION_CANCEL_DIALOG ):
			self._close_dialog()
	
	def _close_dialog( self ):
		
		self.close()