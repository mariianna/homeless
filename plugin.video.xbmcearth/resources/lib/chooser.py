"""
helper module for settings

Nuka1195
"""

import sys
import os
import xbmcgui
import xbmc
import urllib

#from utilities import *
from global_data import *
_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__version__ = sys.modules[ "__main__" ].__version__

BASE_RESOURCE_PATH = os.path.join( os.getcwd().replace( ";", "" ), "resources" )

class GUI( xbmcgui.WindowXMLDialog ):
	""" Settings module: used for changing settings """
	def __init__( self, *args, **kwargs ):
		xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
		self.controlId = 0
		#self.base_path = os.path.join( BASE_RESOURCE_PATH, "skins" )
		self.choices = kwargs[ "choices" ]
		self.descriptions = kwargs[ "descriptions" ]
		self.original = kwargs[ "original" ]
		self.selection = kwargs[ "selection" ]
		self.list_control = kwargs[ "list_control" ]
		self.title = urllib.unquote(kwargs[ "title" ])
		self.doModal()

	def onInit( self ):
		self.show_chooser()

	def show_chooser( self ):
		self.getControl( 500 ).setLabel( self.title )
		#self.getControl( 502 ).setLabel( _( 231 ) )
		self._setup_list()
		#if ( self.list_control == 0 and self.descriptions[ 0 ] == "" ):
		#	self._get_thumb( self.choices[ self.getControl( 503 ).getSelectedPosition() ] )

	def _setup_list( self ):
		xbmcgui.lock()
		#self.getControl( 502 ).setVisible( False )
		self.getControl( 503 ).setVisible( self.list_control == 0 )
		self.getControl( 504 ).setVisible( self.list_control == 1 )
		self.getControl( 505 ).setVisible( self.list_control == 0 and self.descriptions[ 0 ] != "" )
		self.getControl( 503 ).setVisible( True )
		self.getControl( 503 + self.list_control ).reset()
		for placemark in  self.choices:
			if len(self.choices) > 1:
				#if "lon" in placemark and "lat" in placemark:
				#	self.markercontainer.append(marker(self, float(placemark["lat"]), float(placemark["lon"]), BASE_RESOURCE_PATH + '\\skins\\Default\\media\\icon' + str(index) + '.png',12,38,24,38))
				list_item = xbmcgui.ListItem(placemark["name"], '', '', '')
			else:
				#if "lon" in placemark and "lat" in placemark:
				#	self.markercontainer.append(marker(self, float(placemark["lat"]), float(placemark["lon"])))
				#	self.zoom = 1
				list_item = xbmcgui.ListItem(placemark["name"], '', '', '')
			
			#listitem = xbmcgui.ListItem( choice, self.descriptions[ count ] )
			self.getControl( 503 + self.list_control ).addItem( list_item )
			#if ( count == self.original ):
			#	self.getControl( 503 + self.list_control ).selectItem( count )
			#	self.getControl( 503 + self.list_control ).getSelectedItem().select( True )
		self.getControl( 503 + self.list_control ).selectItem( self.selection )
		self.setFocus( self.getControl( 503 + self.list_control ) )
		xbmcgui.unlock()

	def _get_thumb( self, choice ):
		#xbmc.executebuiltin( "Skin.SetString(AMT-chooser-thumbfolder,%s)" % ( os.path.join( self.base_path, choice, "media", "thumbs" ), ) )
		#self.getControl( 502 ).setVisible( os.path.isfile( os.path.join( self.base_path, choice, "warning.txt" ) ) )
		pass
		
	def _close_dialog( self, selection=None ):
		#xbmc.sleep( 5 )
		self.selection = selection
		self.close()

	def onClick( self, controlId ):
		if ( controlId in ( 503, 504, ) ):
			self._close_dialog( self.choices[ self.getControl( controlId ).getSelectedPosition() ]["name"] )

	def onFocus( self, controlId ):
		self.controlId = controlId

	def onAction( self, action ):
		if ( action in ACTION_CANCEL_DIALOG ):
			self._close_dialog()
		elif ( self.list_control == 0 and self.descriptions[ 0 ] == "" ):
			self._get_thumb( self.choices[ self.getControl( 503 ).getSelectedPosition() ]["name"] )
