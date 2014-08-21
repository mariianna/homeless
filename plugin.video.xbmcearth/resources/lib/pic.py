import xbmc, xbmcgui, time, threading, datetime, os, urllib, httplib, sys, glob, random, traceback

# Script constants
__scriptname__ = "XBMC Earth"
__author__ = "MrLight"
__url__ = ""
__svn_url__ = ""
__credits__ = ""
__version__ = "pre-0.2"
__svn_revision__ = ""


BASE_RESOURCE_PATH = os.path.join( os.getcwd().replace( ";", "" ), "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

__language__ = xbmc.Language( os.getcwd() ).getLocalizedString 

from threading import Thread
from googleearth_coordinates import  Googleearth_Coordinates
from xbmcearth_communication import Xbmcearth_communication
from xbmcearth_communication import get_file

from PIL import Image, ImageFont, ImageDraw, ImageFilter
import aggdraw

from xml.dom import minidom 

import simplejson

from global_data import *
TEMPFOLDER = os.path.join( os.getcwd().replace( ";", "" ), "temp" )

class Pic_GUI( xbmcgui.WindowXMLDialog ):
	def __init__( self, *args, **kwargs ):
		xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
		self.pic = kwargs[ "pic" ]
		self.height = int(kwargs[ "height" ])
		self.width = int(kwargs[ "width" ])
		self.MainWindow = kwargs[ "mainWindow" ]
		self.title = ''
		self.info = ''
		self.doModal()
		
		
	def onInit( self ):
		xbmcgui.lock()
		#self._actView()
		self._show_Pic()
		xbmcgui.unlock()

	def _show_Pic( self ):
		try:
			self.title = urllib.unquote(self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty("Title"))
			self.info = urllib.unquote(self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty("Genre"))
			#set Pic
			if self.pic != "":
				self.getControl( 20 ).setImage(self.pic)
				#self.getControl(21).setVisible(0)
				#self.getControl(20).setVisible(1)
			else:
				#self.getControl(21).setVisible(1)
				#self.getControl(20).setVisible(0)
				self.width = 425
				self.height = 350
			if self.width < 700:
				self.getControl( 20 ).setWidth(self.width)
				self.getControl( 20 ).setHeight(self.height)
			else:
				self.getControl( 20 ).setWidth(500)
				self.getControl( 20 ).setHeight(100)
			#set Background Dim
			self.getControl( 19 ).setWidth(self.width+13)
			self.getControl( 19 ).setHeight(self.height+43)
			self.getControl( 206 ).setPosition(7,self.height+2)
			self.getControl( 207 ).setPosition(9,self.height+3)
			self.getControl( 206 ).setLabel(self.title)
			self.getControl( 207 ).setLabel(self.info)
		except:
			traceback.print_exc()

	def _close_dialog( self ):
		self.close()

	def onClick( self, controlId ):
		pass

	def onFocus( self, controlId ):
		pass

	def onAction( self, action ):
		if ( action in ACTION_CANCEL_DIALOG ):
			self._close_dialog()
		elif action.getButtonCode() == KEYBOARD_RIGHT or action.getButtonCode() == REMOTE_RIGHT or action.getButtonCode() == pad_button_dpad_right:
			if self.MainWindow.getListSize() > (self.MainWindow.getCurrentListPosition()+1) and self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()+1).getProperty('lon') != "":
				self.MainWindow.getControl( 50 ).selectItem(self.MainWindow.getCurrentListPosition()+1)
			else:
				self.MainWindow.getControl( 50 ).selectItem(0)
			self._actView()
		elif action.getButtonCode() == KEYBOARD_LEFT or action.getButtonCode() == REMOTE_LEFT or action.getButtonCode() == pad_button_dpad_left:
			if self.MainWindow.getCurrentListPosition() > 0:
				self.MainWindow.getControl( 50 ).selectItem(self.MainWindow.getCurrentListPosition()-1)
			else:
				self.MainWindow.getControl( 50 ).selectItem(self.MainWindow.getListSize()-1)
			self._actView()
		else:
			#Try Action in MainWindow
			self.MainWindow.onAction(action)
			
	def tryYoutube(self):
		if self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('type')  == "youtube":
			self.MainWindow.xbmcearth_communication.connect("www.youtube.com")
			result = self.MainWindow.xbmcearth_communication.get_Youtube_html(referer_url,"?v="+self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('video_id'))
			if result != False:
				x = result.find('var swfArgs = ')
				result =result[x+14:result.find(';',x+15)]
				result = simplejson.loads(result)
				base_v_url = "http://youtube.com/get_video?video_id="+result["video_id"]+"&t="+result["t"]
				base_v_url
				vid_url = self.MainWindow.xbmcearth_communication.stream_Youtube(base_v_url)
				#player.glob_player.stop()
				#try:
				self.MainWindow.Player.play(vid_url)
				#	
				#except:
				#	print "old xbmc - starting fullscreen"
				#	player.glob_player.play(vid_url)
			
	def _actView(self):
		self.MainWindow.lon = float(self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('lon'))
		self.MainWindow.lat = float(self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('lat'))
		googleearth_coordinates = Googleearth_Coordinates()
		coord=googleearth_coordinates.getTileRef(self.MainWindow.lon, self.MainWindow.lat, self.MainWindow.zoom)
		coord_dist = googleearth_coordinates.getLatLong(coord)
		self.MainWindow.lon = self.MainWindow.lon - coord_dist[2]
		self.MainWindow.drawSAT()
		#Panoramio
		if self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('type')  == "Panoramio":
			self.MainWindow.connect()
			current = get_file(self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('photo_file_url'), "Panoramio\\medium\\m" + self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('photo_id') + ".jpg", referer_url)
			current.start()
			current.join(1000)
			self.pic = TEMPFOLDER + "\\Panoramio\\medium\\m" + self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('photo_id') + ".jpg" 
			self.width=int(self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('width'))
			self.height=int(self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('height'))
		#Flickr
		elif self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('type')  == "flickr":
			self.MainWindow.xbmcearth_communication.connect("farm"+str(self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('farm'))+".static.flickr.com")
			current = get_file("http://farm"+str(self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('farm'))+".static.flickr.com/"+str(self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('server'))+"/"+str(self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('photo_id'))+"_"+str(self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('secret'))+".jpg", "Flickr\\medium\\"+str(self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('photo_id'))+".jpg", referer_url)
			current.start()
			current.join(1000)
			im = Image.open(TEMPFOLDER + "\\Flickr\\medium\\"+self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('photo_id')+".jpg")
			size = im.size			
			self.pic = TEMPFOLDER + "\\Flickr\\medium\\"+self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('photo_id')+".jpg"
			self.width=size[0]
			self.height=size[1]
		#locr
		if self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('type')  == "locr":
			self.MainWindow.connect()
			current = get_file(self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('photo_file_url'), "Locr\\medium\\" + self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('photo_id') + ".jpg", referer_url)
			current.start()
			current.join(1000)
			self.pic = TEMPFOLDER + "\\Locr\\medium\\" + self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('photo_id') + ".jpg" 
			self.width=int(self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('width'))
			self.height=int(self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('height'))
		#webcams
		if self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('type')  == "webcams":
			self.MainWindow.connect()
			current = get_file("http://images.webcams.travel/webcam/"+self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('id')+".jpg", "Webcams\\medium\\" +  self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('id') + ".jpg", referer_url,'','','','',0)
			current.start()
			current.join(1000)
			im = Image.open(TEMPFOLDER + "\\Webcams\\medium\\"+self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('id')+".jpg")
			size = im.size			
			self.pic = TEMPFOLDER + "\\Webcams\\medium\\"+self.MainWindow.getListItem(self.MainWindow.getCurrentListPosition()).getProperty('id')+".jpg"
			self.width=size[0]
			self.height=size[1]
		
		
	#list_item.setInfo( 'video', { "Title": photos["photo_title"], "Genre": "Upload Date: " + photos["upload_date"] + " - Owner: " + photos["owner_name"]})
		self._show_Pic()