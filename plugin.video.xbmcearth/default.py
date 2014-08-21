
import xbmc, xbmcgui, time, threading, datetime, os, urllib, httplib, sys, glob, random, traceback

try: Emulating = xbmcgui.Emulating
except: Emulating = False

# Script constants
__scriptname__ = "XBMC Earth"
__author__ = "MrLight"
__version__ = "0.50"
__date__ = '15-01-2009'
xbmc.output(__scriptname__ + " Version: " + __version__ + " Date: " + __date__)


# Shared resources

BASE_RESOURCE_PATH = os.path.join( os.getcwd().replace( ";", "" ), "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

__language__ = xbmc.Language( os.getcwd() ).getLocalizedString 

from threading import Thread

from googleearth_coordinates import  Googleearth_Coordinates
from xbmcearth_communication import *
from virtualearth_coordinates import *
from pic import Pic_GUI
import update 
import settings

from PIL import Image, ImageFont, ImageDraw, ImageFilter
import aggdraw

from xml.dom import minidom 
import simplejson

from global_data import *
TEMPFOLDER = os.path.join( os.getcwd().replace( ";", "" ), "temp" )


class MyPlayer( xbmc.Player ) :

	
	
	def __init__ ( self, window ): 
		xbmc.Player.__init__( self )
		self.window = window  
	
	def onPlayBackStarted(self): 
		if self.window.playYoutube == True:
			self.window.showLargeOverlay = True
			self.window.hide_markers()
		pass
		
	
	def onPlayBackEnded(self):
		try:
			print "PlayBackEnd"
			if self.window.playYoutube == True:
				self.window.showLargeOverlay = False
				self.window.playYoutube = False
				self.window.redraw_markers()
		except:
			pass
	
	def onPlayBackStopped(self):
		try:
			print "PLaybackStopped"
			if self.window.playYoutube == True:
				self.window.showLargeOverlay = False
				self.window.playYoutube = False
				self.window.redraw_markers()
		except:
			pass

class MainClass(xbmcgui.WindowXML):
	#############
	#Value are set during init from settings file
	lon = 13.411494 #Longitude
	lat = 52.523480 #Latitude
	zoom = 8	#Zoomlevel
	hybrid = 1 	#switch between the views
	#############
	URL_satPic = "http://khm2.google.com/kh?v=44"
	URL_mapHybrid = "http://mt0.google.com/mt?v=w2t.88&x="
	URL_mapStreet = "http://mt0.google.com/mt?v=w2.88&x="
	URL_mapArea = "http://mt0.google.com/mt?v=w2p.87&x="
	map_size_x = 3	#Groeße der angezeigten Karte (3 Tiles) muss ungerade sein
	map_size_y = 3  #Groeße der angezeigten Karte (3 Tiles) muss ungerade sein
	map_pos_x_windowed = 320
	map_pos_y_windowed = 270
	pic_size_windowed = 190
	map_pos_x_full = 0
	map_pos_y_full = 0
	pic_size_full = 0
	map_pos_x = 0	#will be calculated
	map_pos_y = 0	#will be calculated
	pic_size = 0	#will be calculated
	
	map_move = 0
	markercontainer = dict()
	routecontainer = dict({'enable': 0, 'linestring': ''}) 
	piccontainer = dict({'enable': 0, 'url_query': '', 'url_pic': ''})
	show_weather = False
	showLargeOverlay = False
	playYoutube = False
	cleanup_thread = ''
	xbmcearth_communication = Xbmcearth_communication()
	set = settings.Settings()
	
	
	def __init__(self, *args, **kwargs):
		global URL_satPic
		global cookie_txt
		if Emulating: 
			xbmcgui.Window.__init__(self)
		self.set.read_settings()
		self.init_startup_values()

		#Clear cached Files
		self.cleanup_thread = file_remove(self)
		self.cleanup_thread.start()
		#Connect to GoogleMaps
		try:
			os.mkdir(TEMPFOLDER)
		except: pass
		self.connect()
		#Get maps.JS
		maps_js = self.xbmcearth_communication.get_Maps_JS(referer_url, maps_key)
		self.findTileURLs(maps_js)
		self.Player = MyPlayer(xbmc.PLAYER_CORE_MPLAYER)
		self.Player.__init__(self)
		
		x = maps_js.find('_mSatelliteToken = "') #find CookieData
		cookie_txt = maps_js[x+20:maps_js.find('";',x+20)]
		self.URL_satPic = self.URL_satPic + "&cookie=" + cookie_txt + "&t="  #extend Sat_Pic URL
				
		#setup picsize
		w = 720
		h = 576
		w = w/self.map_size_x
		h = h/self.map_size_y
		if w>h:
			self.pic_size = int(w)
			self.map_pos_x_full = int(w)
			self.map_pos_y_full = int((float(576)-int(w))/2)
		else:
			self.pic_size = int(h)
			self.map_pos_x_full = int((1-(self.getWidth()/(self.getHeight())))*self.getWidth())
			self.map_pos_y_full = int(h)
		self.pic_size_full	= self.pic_size
		self.map_pos_x = self.map_pos_x_windowed
		self.map_pos_y = self.map_pos_y_windowed
		self.pic_size = self.pic_size_windowed
		#make ImageBlocks for Map and Sat
		#SatBlocks
		self.satBlocks = [[] for i in range(self.map_size_x)]
		for x in range(self.map_size_x):
			self.satBlocks.append(xbmcgui.ControlImage(0,0,0,0, ''))
			for y in range(self.map_size_y):
				Pic_size = self.pic_size
				Map_pos_x = (self.map_pos_x - Pic_size) + (Pic_size*x)
				Map_pos_y = (self.map_pos_y - Pic_size) + (Pic_size*y)
				self.satBlocks[x].append(xbmcgui.ControlImage(Map_pos_x,Map_pos_y,Pic_size,Pic_size, ''))
				self.addControl(self.satBlocks[x][y])
		#Overlay
		self.mapBlocks = [[] for i in range(self.map_size_x)]
		for x in range(self.map_size_x):
			self.mapBlocks.append(xbmcgui.ControlImage(0,0,0,0, ''))
			for y in range(self.map_size_y):
				Pic_size = self.pic_size
				Map_pos_x = (self.map_pos_x - Pic_size) + (Pic_size*x)
				Map_pos_y = (self.map_pos_y - Pic_size) + (Pic_size*y)
				self.mapBlocks[x].append(xbmcgui.ControlImage(Map_pos_x,Map_pos_y,Pic_size,Pic_size, ''))
				self.addControl(self.mapBlocks[x][y])
		self.route_pic = xbmcgui.ControlImage(130,80,Pic_size*3,Pic_size*3, '')
		self.addControl(self.route_pic)
		self.nasa_view = xbmcgui.ControlImage(130,80,Pic_size*3,Pic_size*3, '')
		self.addControl(self.nasa_view)
		self.xbmcearth_communication.get_Google_Analytics( referer_url,  urllib.quote("Start Version:" + str(__version__) ), "/xbmc_earth/start.html", self)
		
		
	def init_startup_values(self):
		self.lon  = self.set.settings["geo"]["lon"]
		self.lat  = self.set.settings["geo"]["lat"]
		self.zoom  = self.set.settings["geo"]["zoom"]
		self.hybrid = self.set.settings["geo"]["hybrid"]
		self.init_analytics()
		
	def init_analytics(self):
		time_now = str(int(time.mktime(datetime.datetime.now().timetuple())))
		if self.set.settings["analytics"]["cookie_number"] == "":
			self.set.settings["analytics"]["cookie_number"] = str(random.randint(10000000,99999999))
		if self.set.settings["analytics"]["random"] == "":
			self.set.settings["analytics"]["random"] = str(random.randint(1000000000,2147483647))
		if self.set.settings["analytics"]["first_use"] == "":
			self.set.settings["analytics"]["first_use"] = time_now
		if self.set.settings["analytics"]["last_use"] == "":
			self.set.settings["analytics"]["last_use"] = time_now
		if self.set.settings["analytics"]["now"] == "":
			self.set.settings["analytics"]["now"] = time_now
		self.set.settings["analytics"]["last_use"] = self.set.settings["analytics"]["now"]
		self.set.settings["analytics"]["now"] = time_now
		self.set.settings["analytics"]["count"] += 1
		
	
	def save_current_values(self):
		self.set.settings["geo"]["lon"] = self.lon
		self.set.settings["geo"]["lat"] = self.lat
		self.set.settings["geo"]["zoom"] = self.zoom
		self.set.settings["geo"]["hybrid"] = self.hybrid 
		self.set.write_settings()
		
	def onInit(self):
		if self.showLargeOverlay == False:
			self.getControl(2004).setVisible(False) #Hide VideoOverlay
		self.getControl(2001).setVisible(0)
		self.getControl(2003).setVisible(False)
		
		for button_id in range( 100, 108 ):
			try:
				self.getControl( button_id ).setLabel( __language__( button_id ) )
			except:
				pass
		for button_id in range( 109, 122 ):
			try:
				self.getControl( button_id ).setLabel( __language__( button_id ) )
			except:
				pass
		#Start Backgroundthread
		self.background = background_thread(self)
		self.background.start()
		self.updateRadioState()
		self.drawSAT()
		pass
		


			
	def onClick(self, controlID):
		#Action to map_move
		if controlID == 100:
			if self.map_move == 0:
				self.map_mov()
				self.getControl(2000).setVisible(0)
			elif self.map_move == 1:
				self.map_mov()
				self.getControl(2000).setVisible(1)
		elif controlID == 101:
			self.search_map()
		elif controlID == 102:
			self.showPanoramio()
		elif controlID == 103:
			self.showFlickr()
		elif controlID == 104:
			self.showLocr()
		elif controlID == 105:
			self.showYoutube()
		elif controlID == 106:
			self.search_Route()
		elif controlID == 107:
			self.showWebcams()
		elif controlID == 109:
			import context
			con = context.GUI( "script-%s-DialogContextMenu.xml" % ( __scriptname__.replace( " ", "_" ), ), os.getcwd(),  "Default", 0,mainWindow = self)
			del con
		elif controlID == 110:
			self.show_GHYB()
		elif controlID == 111:
			self.show_GSAT()
		elif controlID == 112:
			self.show_GMAP()
		elif controlID == 113:
			self.show_GAREA()
		elif controlID == 114:
			self.moveLEFT()
		elif controlID == 115:
			self.moveRIGHT()
		elif controlID == 116:
			self.moveUP()
		elif controlID == 117:
			self.moveDOWN()
		elif controlID == 118:
			self.zoomIN()
		elif controlID == 119:
			self.zoomOUT()
		
		elif controlID == 120:
			self.switch_MS_Google()
		elif controlID == 121:
			self.switch_MS_Google()
		
		elif ( 50 <= controlID <= 59 ):
			self.zoom_to_select(int(self.getCurrentListPosition()))


	def onFocus(self, controlID):
		pass
			
	def onAction(self, action):
		googleearth_coordinates = Googleearth_Coordinates()
		#main_menu active
		if self.map_move == 0:
			if action.getButtonCode() == 61467 or action.getButtonCode() == REMOTE_BACK or action.getButtonCode() == pad_button_back or action in ACTION_CANCEL_DIALOG:
				if self.routecontainer['enable'] == 1:
					self.routecontainer['enable'] = 0
					self.getControl(2001).setVisible(0)
					self.drawSAT()
				elif self.playYoutube == True:
					self.Player.stop()
				elif self.piccontainer['enable'] == 1:
					self.piccontainer['enable'] = 0
					self.delete_markers()
					self.getControl(2001).setVisible(0)
					self.drawSAT()
				elif self.show_weather == True:
					self.getControl(2003).setVisible(False)
					self.show_weather = False	
				else:
					self.goodbye()
		#map_move active
		if self.map_move == 1:
			if action.getButtonCode() == 61467 or action.getButtonCode() == REMOTE_BACK or action.getButtonCode() == pad_button_back or action in ACTION_CANCEL_DIALOG:
				self.map_mov()
				self.getControl(2000).setVisible(1)
			if action.getButtonCode() == KEYBOARD_UP or action.getButtonCode() == REMOTE_UP or action.getButtonCode() == pad_button_dpad_up:
				self.moveUP()
			if action.getButtonCode() == KEYBOARD_DOWN or action.getButtonCode() == REMOTE_DOWN or action.getButtonCode() == pad_button_dpad_down:
				self.moveDOWN()
			if action.getButtonCode() == KEYBOARD_LEFT or action.getButtonCode() == REMOTE_LEFT or action.getButtonCode() == pad_button_dpad_left:
				self.moveLEFT()
			if action.getButtonCode() == KEYBOARD_RIGHT or action.getButtonCode() == REMOTE_RIGHT or action.getButtonCode() == pad_button_dpad_right:
				self.moveRIGHT()
		if self.map_move == 2:
			if action.getButtonCode() == 61467 or action.getButtonCode() == REMOTE_BACK or action.getButtonCode() == pad_button_back:
				self.map_move = 0
				try:
					self.pan_pic.setImage("")
					self.removeControl(self.pan_pic.getId())
				except:
					pass
				self.getControl(2000).setVisible(1)
		# do always
		if action.getButtonCode() == KEYBOARD_PG_DW or action.getButtonCode() == REMOTE_4 or action.getButtonCode() == pad_button_left_trigger:
			self.zoomOUT()
		if action.getButtonCode() == KEYBOARD_PG_UP or action.getButtonCode() == REMOTE_1 or action.getButtonCode() == pad_button_right_trigger:
			self.zoomIN()
		if action.getButtonCode() == KEYBOARD_INSERT or action.getButtonCode() == REMOTE_INFO or action.getButtonCode() == pad_button_white:
			if self.hybrid == 1:
				self.hybrid = 2
				self.show_GMAP()
			elif self.hybrid ==2:
				self.hybrid = 3
				self.show_GAREA()
			elif self.hybrid ==3:
				self.hybrid = 4
				self.show_GSAT()
			elif self.hybrid ==4:
				self.hybrid = 5
				self.show_GHYB()
			elif self.hybrid ==5:
				self.hybrid = 6
				self.show_GMAP()
			elif self.hybrid ==6:
				self.hybrid = 0
				self.show_GSAT()
			else:
				self.hybrid = 1
				self.show_GHYB()
			#self.drawSAT()
	
	def updateRadioState(self):
		self.getControl(110).setSelected(False)
		self.getControl(111).setSelected(False)
		self.getControl(112).setSelected(False)
		self.getControl(113).setSelected(False)
		self.getControl(120).setSelected(False)
		self.getControl(121).setSelected(False)
		if self.hybrid == 0:
			self.getControl(111).setSelected(True)
			self.getControl(120).setSelected(True)
		elif self.hybrid == 1:
			self.getControl(110).setSelected(True)
			self.getControl(120).setSelected(True)
		elif self.hybrid == 2:
			self.getControl(112).setSelected(True)
			self.getControl(120).setSelected(True)
		elif self.hybrid == 3:
			self.getControl(113).setSelected(True)
			self.getControl(120).setSelected(True)
		elif self.hybrid == 4:
			self.getControl(111).setSelected(True)
			self.getControl(121).setSelected(True)
		elif self.hybrid == 5:
			self.getControl(110).setSelected(True)
			self.getControl(121).setSelected(True)
		elif self.hybrid == 6:
			self.getControl(112).setSelected(True)
			self.getControl(121).setSelected(True)
			
	def show_GSAT(self):
		if self.hybrid <= 3:
			self.hybrid = 0
			self.select_Google()
		else:
			self.hybrid = 4
			self.select_MS()
		self.updateRadioState()
		self.drawSAT()
	
	def show_GHYB(self):
		if self.hybrid <= 3:
			self.hybrid = 1
			self.select_Google()
		else:
			self.hybrid = 5
			self.select_MS()
		self.updateRadioState()
		self.drawSAT()
	
	def show_GMAP(self):
		if self.hybrid <= 3:
			self.hybrid = 2
			self.select_Google()
		else:
			self.hybrid = 6
			self.select_MS()
		self.updateRadioState()
		self.drawSAT()
		
	def show_GAREA(self):
		if self.hybrid <= 3:
			self.hybrid = 3
			self.select_Google()
		else:
			pass
		self.updateRadioState()
		self.drawSAT()
		
	def select_MS(self):
		self.getControl(120).setSelected(False)
		self.getControl(121).setSelected(True)

	def select_Google(self):
		self.getControl(120).setSelected(True)
		self.getControl(121).setSelected(False)

	def switch_MS_Google(self):
		if self.hybrid < 3:
			self.hybrid += 4
		elif self.hybrid > 3:
			self.hybrid -= 4
		self.updateRadioState()
		self.drawSAT()
	
	def moveUP(self):
		coord_dist =[]
		coord=Googleearth_Coordinates().getTileRef(self.lon, self.lat, self.zoom)
		coord_dist = Googleearth_Coordinates().getLatLong(coord)
		self.lat = self.lat + coord_dist[3]
		self.drawSAT()
	def moveDOWN(self):
		coord_dist =[]
		coord=Googleearth_Coordinates().getTileRef(self.lon, self.lat, self.zoom)
		coord_dist = Googleearth_Coordinates().getLatLong(coord)
		self.lat = self.lat - coord_dist[3]
		self.drawSAT()
	def moveLEFT(self):
		coord_dist =[]
		coord=Googleearth_Coordinates().getTileRef(self.lon, self.lat, self.zoom)
		coord_dist = Googleearth_Coordinates().getLatLong(coord)
		self.lon = self.lon - coord_dist[2]
		self.drawSAT()	
	def moveRIGHT(self):
		coord_dist =[]
		coord=Googleearth_Coordinates().getTileRef(self.lon, self.lat, self.zoom)
		coord_dist = Googleearth_Coordinates().getLatLong(coord)
		self.lon = self.lon + coord_dist[2]
		self.drawSAT()
	def zoomOUT(self):
		self.zoom += 1
		self.drawSAT()	
	def zoomIN(self):
		self.zoom -= 1
		self.drawSAT()
		
	def goodbye(self):
		global run_backgroundthread
		try:
			run_backgroundthread = 0
			self.cleanup_thread.join(1.0)
			self.background.join(1.0)
		except:
			pass
		try:
			self.save_current_values()
		except:
			traceback.print_exc()
		self.close()
		
	def connect(self):
		self.xbmcearth_communication.connect("maps.google.com")
	
	#Plan a Route from A to B
	#Show virtual Keyboard for Start and Destintion
	def search_Route(self):
		self.start = ""
		self.ziel = ""
		keyboard = xbmc.Keyboard()
		keyboard.setHeading(__language__( 10001 ))
		keyboard.doModal()
		if keyboard.isConfirmed():
			search_string = ''
			search_string = keyboard.getText()
			self.connect()
			search_kml = self.xbmcearth_communication.get_Query_Place(referer_url, maps_key, search_string)
			result = self.parse_kml(search_kml)
			import chooser
			ch = chooser.GUI( "script-%s-chooser.xml" % ( __scriptname__.replace( " ", "_" ), ), os.getcwd(),  "Default", 0, choices=result["Placemarks"], descriptions=result["Placemarks"], original=-1, selection=0, list_control=1, title=urllib.quote(__language__( 10004 )) )
			self.start = ch.selection
			del ch
		keyboard = xbmc.Keyboard()
		keyboard.setHeading(__language__( 10002 ))
		keyboard.doModal()
		if keyboard.isConfirmed():
			search_string = ''
			search_string = keyboard.getText()
			self.connect()
			search_kml = self.xbmcearth_communication.get_Query_Place(referer_url, maps_key, search_string)
			result = self.parse_kml(search_kml)
			import chooser
			ch = chooser.GUI( "script-%s-chooser.xml" % ( __scriptname__.replace( " ", "_" ), ), os.getcwd(),  "Default", 0, choices=result["Placemarks"], descriptions=result["Placemarks"], original=-1, selection=0, list_control=1, title=urllib.quote(__language__( 10005 )) )
			self.ziel = ch.selection
			del ch
		self.proc_route_result(self.planRoute( self.start, self.ziel))
		self.xbmcearth_communication.get_Google_Analytics( referer_url,  urllib.quote("Search_Route"), urllib.quote("/xbmc_earth/search_route.html?q="+str(self.start)+" - " + str(self.ziel) + "&cat=Route_Search"),self)

		self.drawSAT()	
	
	def planRoute(self, start, ziel):
		self.connect()
		search_kml = self.xbmcearth_communication.get_Route(referer_url,start, ziel)
		if search_kml != False:
			resultcontainer = dict()
			#self.delete_markers()
			#self.clearList()
			xmldoc = minidom.parseString(search_kml)
			resultcontainer = dict()
			#read route name
			nodelist = xmldoc.getElementsByTagName("name")
			node = nodelist[0]
			name =  node.firstChild.data.encode('latin-1', 'ignore')
			resultcontainer["name"] = name
			#read length
			nodelist = xmldoc.getElementsByTagName("Placemark")
			node = nodelist[len(nodelist)-1]
			sub_node2 = node.getElementsByTagName('description')
			for node in sub_node2:
				description = node.firstChild.data.encode('latin-1', 'ignore').replace('<br/>','\n').replace('<![CDATA[','').replace('&#160;',' ').replace(']]>',' ')
				resultcontainer["info"] = description
			index = 0
			placemark_seq = []
			resultcontainer["Placemarks"] = placemark_seq
			for node in nodelist[0:len(nodelist)-2]:
				placemark = dict()
				resultcontainer["Placemarks"].append(placemark)
				node_temp = node
				sub_node2 = node_temp.getElementsByTagName('name')
				for node in sub_node2:
					name = node.firstChild.data.encode('latin-1', 'ignore')
					resultcontainer["Placemarks"][index]["name"] = name
				sub_node2 = node_temp.getElementsByTagName('description')
				for node in sub_node2:
					description = node.firstChild.data.encode('latin-1', 'ignore').replace('<br/>','\n').replace('<![CDATA[','').replace('&#160;',' ').replace(']]>',' ')
					resultcontainer["Placemarks"][index]["info"] = description
				sub_node2 = node_temp.getElementsByTagName('text')
				#for node in sub_node2:
				#	x = node.firstChild.data.find('<img src="http://base.googlehosted.com/')
				#	if x != -1:
				#		url =  node.firstChild.data[x+10:node.firstChild.data.find('"/>',node.firstChild.data.find('<img src="http://base.googlehosted.com/'))].encode('UTF-8', 'ignore')
				#		searchresult[index][2] = url
				sub_node2 = node_temp.getElementsByTagName('coordinates')
				for node in sub_node2:
					Lon = node.firstChild.data[0:node.firstChild.data.find(',')]
					Lat = node.firstChild.data[node.firstChild.data.find(',')+1:node.firstChild.data.find(',', node.firstChild.data.find(',')+1)]
					resultcontainer["Placemarks"][index]["lon"] = float(Lon)
					resultcontainer["Placemarks"][index]["lat"] = float(Lat)
				index += 1
			nodelist = xmldoc.getElementsByTagName("GeometryCollection")
			for node in nodelist:
				node_temp = node
				self.routecontainer['linestring'] = ''
				sub_node2 = node_temp.getElementsByTagName('coordinates')
				for node in sub_node2:
					#print node.firstChild.data.encode('latin-1', 'ignore')
					self.routecontainer['linestring'] = self.routecontainer['linestring'] + node.firstChild.data.encode('latin-1', 'ignore') 
			self.routecontainer['enable'] = 1
			return resultcontainer
			
	
	def proc_route_result(self, result):
		self.delete_markers()
		#calc zoomlevel to fit
		self.fit_placemarks(result["Placemarks"])
		#make resultlist in MainGUI
		self.clearList()
		list_item = xbmcgui.ListItem(result["name"], '', '', '')
		list_item.setInfo( 'video', { "Title": result["name"], "Genre":result["info"] }) 				
		list_item.setProperty('name', urllib.quote(result["name"]))
		list_item.setProperty('lon',str(self.lon))
		list_item.setProperty('lat',str(self.lat))
		list_item.setProperty('zoom',str(self.zoom))
		self.addItem(list_item)
		for placemark in result["Placemarks"]:
			if "name" in placemark:
				pass
			else:
				placemark["name"] = 'error - no name'
			if "info" in placemark:
				pass
			else:
				placemark["info"] = ''
			list_item = xbmcgui.ListItem(placemark["name"], '', '', '')
			list_item.setInfo( 'video', { "Title": placemark["name"], "Genre": placemark["info"] }) 				
			list_item.setProperty('name', urllib.quote(placemark["name"]))
			if "lon" in placemark and "lat" in placemark:
				list_item.setProperty('lon',str(placemark["lon"]))
				list_item.setProperty('lat',str(placemark["lat"]))
			
			self.addItem(list_item)
		#self.makeRoute(self.routecontainer['linestring'])
		self.getControl(2001).setVisible(1)
	
	
	#Panoramio Support
	def showPanoramio(self):
		self.proc_panoramio_result(self.getPanoramio(0,20))
		self.xbmcearth_communication.get_Google_Analytics( referer_url,  urllib.quote("Show Panoramio"), urllib.quote("/xbmc_earth/panoramio.html"),self)

		self.piccontainer["enable"] = 1
		self.piccontainer["type"] = "Panoramio"
		
	def getPanoramio(self, start, size):
		Lon = self.lon
		Lat = self.lat
		Zoom = self.zoom
		googleearth_coordinates = Googleearth_Coordinates()
		coord=googleearth_coordinates.getTileRef(Lon, Lat, Zoom)
		coord_dist =[]
		coord_dist = googleearth_coordinates.getLatLong(coord)
		self.xbmcearth_communication.connect("www.panoramio.com")
		result = self.xbmcearth_communication.get_Panoramio(referer_url,"?order=popularity&set=public&from="+str(start)+"&to="+str(start+size)+"&minx="+ str(coord_dist[0]-coord_dist[2]) +"&miny=" + str(coord_dist[1]-coord_dist[3]) + "&maxx="+str(coord_dist[0]+coord_dist[2]*2)+"&maxy="+str(coord_dist[1]+coord_dist[3]*2)+"&size=medium")
		if result != False:
			result = simplejson.loads(result)
			index = 0
			resultcontainer = dict()
			resultcontainer["count"] = result['count']
			resultcontainer["start"] = start + size
			resultcontainer["size"] = size
			results = result['photos']
			placemark_seq = []
			resultcontainer["Placemarks"] = placemark_seq
			for photos in results:
				placemark = dict()
				resultcontainer["Placemarks"].append(placemark)
				resultcontainer["Placemarks"][index]["name"] = photos["photo_title"]
				resultcontainer["Placemarks"][index]["photo_id"] = photos["photo_id"]
				resultcontainer["Placemarks"][index]["photo_file_url"] = photos["photo_file_url"]
				resultcontainer["Placemarks"][index]["lon"] = photos["longitude"]
				resultcontainer["Placemarks"][index]["lat"] = photos["latitude"]
				resultcontainer["Placemarks"][index]["width"] = photos["width"]
				resultcontainer["Placemarks"][index]["height"] = photos["height"]
				resultcontainer["Placemarks"][index]["upload_date"] = photos["upload_date"]
				resultcontainer["Placemarks"][index]["owner_name"] = photos["owner_name"]
				index += 1
			return resultcontainer
		else:
			return False
	
	def proc_panoramio_result(self, result):
		if result != False:
			self.clearList()
			self.delete_markers()
			if  result["count"] > result["start"]:
				list_item = xbmcgui.ListItem(__language__( 10003 ) % (str(result["size"])), '', "", "")
				list_item.setInfo( 'video', { "Title": __language__( 10003 ) % (str(result["size"])), "Genre": str(result["count"]) + " Photos"})
				list_item.setProperty('type',"Panoramio")
				list_item.setProperty('next',"next")
				list_item.setProperty('start',str(result["start"]))
				list_item.setProperty('size',str(result["size"]))
				self.addItem(list_item)
			for photo in result["Placemarks"]:	
				photo["path"]="\\Panoramio\\small\\sm"
				current = get_file(photo["photo_file_url"].replace("medium","square"), "Panoramio\\small\\sm"+str(photo["photo_id"])+".jpg", referer_url,'',self.add_panoramio_hit,self,photo)
				thread_starter=0
				while thread_starter<10:
					try:
						current.start()
						thread_starter=100
					except:
						time.sleep(1)
						thread_starter +=1

				#current.join(1000)
				

			self.getControl(2001).setVisible(1)

	def add_panoramio_hit(self, photo):
		list_item = xbmcgui.ListItem(photo["name"], '', "", TEMPFOLDER + photo["path"]+str(photo["photo_id"])+".jpg")
		list_item.setInfo( 'video', { "Title": photo["name"], "Genre": "Upload Date: " + photo["upload_date"] + " - Owner: " + photo["owner_name"]}) 				
		list_item.setProperty('Piclink', TEMPFOLDER + photo["path"]+str(photo["photo_id"])+".jpg")
		list_item.setProperty('Title', urllib.quote(photo["name"]))
		list_item.setProperty('Genre', urllib.quote("Upload Date: " + photo["upload_date"] + " - Owner: " + photo["owner_name"]))
		list_item.setProperty('lon',str(photo["lon"]))
		list_item.setProperty('lat',str(photo["lat"]))
		list_item.setProperty('photo_file_url',photo["photo_file_url"])
		list_item.setProperty('photo_id',str(photo["photo_id"]))
		list_item.setProperty('id',str(photo["photo_id"]))
		list_item.setProperty('width',str(photo["width"]))
		list_item.setProperty('height',str(photo["height"]))
		list_item.setProperty('type',"Panoramio")
		self.markercontainer[str(photo["photo_id"])]=marker(self, float(photo["lat"]), float(photo["lon"]), TEMPFOLDER + photo["path"]+str(photo["photo_id"])+".jpg",16,32,32,32)
		self.addItem(list_item,0)
	
	#Flickr Support
	def showFlickr(self):
		self.proc_flickr_result(self.getFlickr_bbox(1,20))
		self.xbmcearth_communication.get_Google_Analytics( referer_url,  urllib.quote("Show Flickr"), urllib.quote("/xbmc_earth/flickr_bbox.html"),self)
		self.piccontainer["enable"] = 1
		self.piccontainer["type"] = "Flickr"
	
	def getFlickr_bbox(self, page, size):
		Lon = self.lon
		Lat = self.lat
		Zoom = self.zoom
		googleearth_coordinates = Googleearth_Coordinates()
		coord=googleearth_coordinates.getTileRef(Lon, Lat, Zoom)
		coord_dist =[]
		coord_dist = googleearth_coordinates.getLatLong(coord)
		self.xbmcearth_communication.connect("api.flickr.com")
		result = self.xbmcearth_communication.get_Flickr(referer_url,"?method=flickr.photos.search&format=json&api_key=" + flickr_Key + "&min_upload_date=977957078&sort=interestingness-desc&bbox="+str(coord_dist[0]-coord_dist[2])+","+str(coord_dist[1]-coord_dist[3])+","+str(coord_dist[0]+coord_dist[2]*2)+","+str(coord_dist[1]+coord_dist[3]*2)+"&extras=+date_taken%2C+owner_name%2C+geo%2C&page="+str(page)+"&per_page="+str(size))
		if result != False:
			result = result.replace("jsonFlickrApi(","").replace(")","")
			result = simplejson.loads(result)
			index = 0
			results = result['photos']
			resultcontainer = dict()
			resultcontainer["count"] = results['total']
			resultcontainer["start"] = page + 1
			resultcontainer["size"] = size
			results = results['photo']
			placemark_seq = []
			resultcontainer["Placemarks"] = placemark_seq
			for photos in results:
				placemark = dict()
				resultcontainer["Placemarks"].append(placemark)
				resultcontainer["Placemarks"][index]["name"] = photos["title"]
				resultcontainer["Placemarks"][index]["photo_id"] = photos["id"]
				#resultcontainer["Placemarks"][index]["photo_file_url"] = photos["photo_file_url"]
				resultcontainer["Placemarks"][index]["lon"] = photos["longitude"]
				resultcontainer["Placemarks"][index]["lat"] = photos["latitude"]
				#resultcontainer["Placemarks"][index]["width"] = photos["width"]
				#resultcontainer["Placemarks"][index]["height"] = photos["height"]
				resultcontainer["Placemarks"][index]["upload_date"] = photos["datetaken"]
				resultcontainer["Placemarks"][index]["owner_name"] = photos["ownername"]
				resultcontainer["Placemarks"][index]["farm"] = photos["farm"]
				resultcontainer["Placemarks"][index]["server"] = photos["server"]
				resultcontainer["Placemarks"][index]["secret"] = photos["secret"]
				index += 1
			return resultcontainer
		else:
			return False
		
	def proc_flickr_result(self, result):
		if result != False:
			self.clearList()
			self.delete_markers()
			if  result["count"] > result["start"]*result["size"]:
				list_item = xbmcgui.ListItem(__language__( 10003 ) % (str(result["size"])), '', "", "")
				list_item.setInfo( 'video', { "Title": __language__( 10003 ) % (str(result["size"])), "Genre": str(result["count"]) + " Photos"})
				list_item.setProperty('type',"flickr")
				list_item.setProperty('next',"next")
				list_item.setProperty('start',str(result["start"]))
				list_item.setProperty('size',str(result["size"]))
				self.addItem(list_item)
			for photo in result["Placemarks"]:	
				photo["path"]="\\Flickr\\small\\"
				current = get_file("http://farm"+str(photo["farm"])+".static.flickr.com/"+str(photo["server"])+"/"+str(photo["photo_id"])+"_"+str(photo["secret"])+"_s.jpg", "Flickr\\small\\"+str(photo["photo_id"])+".jpg", referer_url,'',self.add_flickr_hit,self,photo)
				thread_starter=0
				while thread_starter<10:
					try:
						current.start()
						thread_starter=100
					except:
						time.sleep(1)
						thread_starter +=1

				#current.join(1000)
				

			self.getControl(2001).setVisible(1)
			
	def add_flickr_hit(self, photo):
		list_item = xbmcgui.ListItem(photo["name"], '', "", TEMPFOLDER + photo["path"]+str(photo["photo_id"])+".jpg")
		list_item.setInfo( 'video', { "Title": photo["name"], "Genre": "Date taken: " + photo["upload_date"] + " - Owner: " + photo["owner_name"]}) 				
		list_item.setProperty('Piclink', TEMPFOLDER + photo["path"]+str(photo["photo_id"])+".jpg")
		list_item.setProperty('Title', urllib.quote(photo["name"]))
		list_item.setProperty('Genre', urllib.quote("Date taken: " + photo["upload_date"] + " - Owner: " + photo["owner_name"]))
		list_item.setProperty('lon',str(photo["lon"]))
		list_item.setProperty('lat',str(photo["lat"]))
		list_item.setProperty('farm',str(photo["farm"]))
		list_item.setProperty('photo_id',str(photo["photo_id"]))
		list_item.setProperty('id',str(photo["photo_id"]))
		list_item.setProperty('server',str(photo["server"]))
		list_item.setProperty('secret',str(photo["secret"]))
		list_item.setProperty('type',"flickr")
		self.markercontainer[str(photo["photo_id"])] = marker(self, float(photo["lat"]), float(photo["lon"]), TEMPFOLDER + photo["path"]+str(photo["photo_id"])+".jpg",16,32,32,32)
		self.addItem(list_item,0)
		
	#Locr Support
	def showLocr(self):
		self.proc_locr_result(self.getLocr(1,20))
		self.xbmcearth_communication.get_Google_Analytics( referer_url,  urllib.quote("Show Locr"), urllib.quote("/xbmc_earth/locr.html"),self)
		self.piccontainer["enable"] = 1
		self.piccontainer["type"] = "Locr"
	
	def getLocr(self, start, size):
		Lon = self.lon
		Lat = self.lat
		Zoom = self.zoom
		googleearth_coordinates = Googleearth_Coordinates()
		coord=googleearth_coordinates.getTileRef(Lon, Lat, Zoom)
		coord_dist =[]
		coord_dist = googleearth_coordinates.getLatLong(coord)
		self.xbmcearth_communication.connect("www.locr.com")
		result = self.xbmcearth_communication.get_Locr(referer_url,"?longitudemin="+str(coord_dist[0]-coord_dist[2])+"&latitudemin="+str(coord_dist[1]-coord_dist[3])+"&longitudemax="+str(coord_dist[0]+coord_dist[2]*2)+"&latitudemax=" + str(coord_dist[1]+coord_dist[3]*2) + "&count="+str(size)+"&start="+str(start)+"&category=popularity&size=medium&locr=true")
		if result != False:
			result = simplejson.loads(result)
			index = 0
			resultcontainer = dict()
			resultcontainer["start"] = start + size
			resultcontainer["size"] = size
			results = result['photos']
			placemark_seq = []
			resultcontainer["Placemarks"] = placemark_seq
			for photos in results:
				placemark = dict()
				resultcontainer["Placemarks"].append(placemark)
				resultcontainer["Placemarks"][index]["name"] = photos["caption"]
				resultcontainer["Placemarks"][index]["photo_id"] = photos["photo_name"]
				resultcontainer["Placemarks"][index]["photo_file_url"] = photos["photo_file_url"]
				resultcontainer["Placemarks"][index]["photo_ext"] = photos["photo_ext"]
				resultcontainer["Placemarks"][index]["lon"] = photos["longitude"]
				resultcontainer["Placemarks"][index]["lat"] = photos["latitude"]
				resultcontainer["Placemarks"][index]["width"] = photos["photo_offset_width"]
				resultcontainer["Placemarks"][index]["height"] = photos["photo_offset_height"]
				resultcontainer["Placemarks"][index]["tags"] = photos["tags"]
				resultcontainer["Placemarks"][index]["description"] = photos["description"]
				resultcontainer["Placemarks"][index]["created"] = photos["created"]
				resultcontainer["Placemarks"][index]["owner_name"] = photos["user_name"]

				index += 1
			return resultcontainer
		else:
			return False
	
	def proc_locr_result(self, result):
		if result != False:
			self.clearList()
			self.delete_markers()
			if  len(result["Placemarks"]) == 20:
				list_item = xbmcgui.ListItem(__language__( 10003 ) % (str(result["size"])), '', "", "")
				list_item.setInfo( 'video', { "Title": __language__( 10003 ) % (str(result["size"])), "Genre": ""})
				list_item.setProperty('type',"locr")
				list_item.setProperty('next',"next")
				list_item.setProperty('start',str(result["start"]))
				list_item.setProperty('size',str(result["size"]))
				self.addItem(list_item)
			for photo in result["Placemarks"]:	
				photo["path"]="Locr\\small\\"
				current = get_file(photo["photo_file_url"].replace("_M","_SQ"), photo["path"]+str(photo["photo_id"])+".jpg", referer_url,'',self.add_locr_hit,self,photo)
				thread_starter=0
				while thread_starter<10:
					try:
						current.start()
						thread_starter=100
					except:
						time.sleep(1)
						thread_starter +=1

				#current.join(1000)
			self.getControl(2001).setVisible(1)
	
	def add_locr_hit(self, photo):
		list_item = xbmcgui.ListItem(photo["name"], '', "", TEMPFOLDER +"\\"+ photo["path"]+str(photo["photo_id"])+".jpg")
		list_item.setInfo( 'video', { "Title": photo["name"], "Genre": "Create Date: " + photo["created"] + " - Owner: " + photo["owner_name"]}) 				
		list_item.setProperty('Piclink', TEMPFOLDER +"\\"+ photo["path"]+str(photo["photo_id"])+".jpg")
		list_item.setProperty('Title', urllib.quote(photo["name"]))
		list_item.setProperty('Genre', urllib.quote("Create Date: " + photo["created"] + " - Owner: " + photo["owner_name"]))
		list_item.setProperty('lon',str(photo["lon"]))
		list_item.setProperty('lat',str(photo["lat"]))
		list_item.setProperty('photo_file_url',photo["photo_file_url"])
		list_item.setProperty('photo_id',str(photo["photo_id"]))
		list_item.setProperty('id',str(photo["photo_id"]))
		list_item.setProperty('width',str(photo["width"]))
		list_item.setProperty('height',str(photo["height"]))
		list_item.setProperty('type',"locr")
		self.markercontainer[str(photo["photo_id"])] = marker(self, float(photo["lat"]), float(photo["lon"]), TEMPFOLDER +"\\"+ photo["path"]+str(photo["photo_id"])+".jpg",16,32,32,32)
		self.addItem(list_item,0)
		
	#Youtube Support
	def showYoutube(self):
		self.proc_youtube_result(self.getYoutube(1,20))
		self.xbmcearth_communication.get_Google_Analytics( referer_url,  urllib.quote("Show Youtube"), urllib.quote("/xbmc_earth/youtube.html"),self)
		self.piccontainer["enable"] = 1
		self.piccontainer["type"] = "Youtube"
	
	def getYoutube(self, start, size):
		Lon = self.lon
		Lat = self.lat
		Zoom = self.zoom
		googleearth_coordinates = Googleearth_Coordinates()
		coord=googleearth_coordinates.getTileRef(Lon, Lat, Zoom)
		coord_dist =[]
		coord_dist = googleearth_coordinates.getLatLong(coord)
		center_lon = coord_dist[0]+(coord_dist[2]/2)
		center_lat = coord_dist[1]+(coord_dist[3]/2)
		distance = googleearth_coordinates.getDistance(center_lat,center_lon,center_lat+(coord_dist[3]*1.5),center_lon+(coord_dist[2]*1.5))
		self.xbmcearth_communication.connect("gdata.youtube.com")
		result = self.xbmcearth_communication.get_Youtube(referer_url,"?orderby=viewCount&location="+str(center_lat)+","+str(center_lon)+"!&location-radius="+str(distance)+"km&alt=json&start-index="+str(start)+"&max-results="+str(size))
		if result != False:
			result = simplejson.loads(result)
			index = 0
			feed = result["feed"]
			resultcontainer = dict()
			results = feed["openSearch$totalResults"]
			resultcontainer["count"] = results['$t']
			resultcontainer["start"] = start + size
			resultcontainer["size"] = size
			videos = feed['entry']
			placemark_seq = []
			resultcontainer["Placemarks"] = placemark_seq
			for video in videos:
				placemark = dict()
				resultcontainer["Placemarks"].append(placemark)
				resultcontainer["Placemarks"][index]["video_id"] = video['id']['$t'].replace('http://gdata.youtube.com/feeds/api/videos/','')
				resultcontainer["Placemarks"][index]["name"] = video["title"]['$t']
				resultcontainer["Placemarks"][index]["description"] = video["content"]['$t'].replace('\n','')
				resultcontainer["Placemarks"][index]["photo_file_url"] = video["media$group"]["media$thumbnail"][0]['url']
				try:
					resultcontainer["Placemarks"][index]["lon"] = video["georss$where"]["gml$Point"]["gml$pos"]['$t'].split(' ')[1]
					resultcontainer["Placemarks"][index]["lat"] = video["georss$where"]["gml$Point"]["gml$pos"]['$t'].split(' ')[0]
				except:
					resultcontainer["Placemarks"][index]["lon"] = self.lon
					resultcontainer["Placemarks"][index]["lat"] = self.lat
				#resultcontainer["Placemarks"][index]["width"] = photos["photo_offset_width"]
				#resultcontainer["Placemarks"][index]["height"] = photos["photo_offset_height"]
				#resultcontainer["Placemarks"][index]["tags"] = photos["tags"]
				#resultcontainer["Placemarks"][index]["description"] = photos["description"]
				try:
					resultcontainer["Placemarks"][index]["created"] = video["yt$recorded"]['$t']
				except:
					resultcontainer["Placemarks"][index]["created"] = video["published"]['$t']
				#resultcontainer["Placemarks"][index]["owner_name"] = photos["user_name"]
				index += 1
			return resultcontainer
		else:
			return False
	
	def proc_youtube_result(self, result):
		if result != False:
			self.clearList()
			self.delete_markers()
			if  result["count"] > result["start"]*result["size"]:
				list_item = xbmcgui.ListItem(__language__( 10003 ) % (str(result["size"])), '', "", "")
				list_item.setInfo( 'video', { "Title": __language__( 10003 ) % (str(result["size"])), "Genre": str(result["count"]) + " Videos"})
				list_item.setProperty('type',"youtube")
				list_item.setProperty('next',"next")
				list_item.setProperty('start',str(result["start"]))
				list_item.setProperty('size',str(result["size"]))
				self.addItem(list_item)
			for video in result["Placemarks"]:	
				video["path"] = "\\Youtube\\small\\"
				current = get_file(video["photo_file_url"], "Youtube\\small\\"+str(video["video_id"])+".jpg", referer_url,'',self.add_youtube_hit,self,video)
				thread_starter=0
				while thread_starter<10:
					try:
						current.start()
						thread_starter=100
					except:
						time.sleep(1)
						thread_starter +=1
				#current.join(1000)
			self.getControl(2001).setVisible(1)
		
	def add_youtube_hit(self, video):
		list_item = xbmcgui.ListItem(video["name"], '', "", TEMPFOLDER + video["path"]+str(video["video_id"])+".jpg")
		list_item.setInfo( 'video', { "Title": video["name"], "Genre": "Create Date: " + video["created"] + " - Description: " + video["description"]}) 				
		#list_item.setProperty('Piclink', TEMPFOLDER + "\\Youtube\\medium\\"+str(video["video_id"])+".jpg")
		list_item.setProperty('Title', urllib.quote(video["name"]))
		list_item.setProperty('Genre', urllib.quote("Create Date: " + video["created"]))#+ " - Owner: " + video["owner_name"]))
		list_item.setProperty('lon',str(video["lon"]))
		list_item.setProperty('lat',str(video["lat"]))
		#list_item.setProperty('video_file_url',video["video_file_url"])
		list_item.setProperty('video_id',str(video["video_id"]))
		list_item.setProperty('id',str(video["video_id"]))
		#list_item.setProperty('width',str(video["width"]))
		#list_item.setProperty('height',str(video["height"]))
		list_item.setProperty('type',"youtube")
		self.markercontainer[str(video["video_id"])] = marker(self, float(video["lat"]), float(video["lon"]), TEMPFOLDER + video["path"]+str(video["video_id"])+".jpg",16,32,32,32)
		self.addItem(list_item,0)
		
	#Flickr Support
	def showWebcams(self):
		self.proc_webcams_result(self.getWebcams_bbox(1,20))
		self.xbmcearth_communication.get_Google_Analytics( referer_url,  urllib.quote("Show Webcams"), urllib.quote("/xbmc_earth/webcams.html"),self)
		self.piccontainer["enable"] = 1
		self.piccontainer["type"] = "Webcams"
	
	def getWebcams_bbox(self, page, size):
		Lon = self.lon
		Lat = self.lat
		Zoom = self.zoom
		googleearth_coordinates = Googleearth_Coordinates()
		coord=googleearth_coordinates.getTileRef(Lon, Lat, Zoom)
		coord_dist =[]
		coord_dist = googleearth_coordinates.getLatLong(coord)
		center_lon = coord_dist[0]+(coord_dist[2]/2)
		center_lat = coord_dist[1]+(coord_dist[3]/2)
		distance = googleearth_coordinates.getDistance(center_lat,center_lon,center_lat+(coord_dist[3]*1.5),center_lon+(coord_dist[2]*1.5))
		self.xbmcearth_communication.connect("api.webcams.travel")
		result = self.xbmcearth_communication.get_Webcams(referer_url,"?method=wct.webcams.list_nearby&devid=" + webcams_key + "&format=json&lat="+str(center_lat)+"&lng="+str(center_lon)+"&radius="+str(distance)+"&unit=km&page="+str(page)+"&per_page="+str(size))
		if result != False:
			result = simplejson.loads(result)
			index = 0
			results = result['webcams']
			resultcontainer = dict()
			resultcontainer["count"] = results['count']
			resultcontainer["start"] = page + 1
			resultcontainer["size"] = size
			results = results['webcam']
			placemark_seq = []
			resultcontainer["Placemarks"] = placemark_seq
			for webcams in results:
				placemark = dict()
				resultcontainer["Placemarks"].append(placemark)
				resultcontainer["Placemarks"][index]["name"] = webcams["title"]
				resultcontainer["Placemarks"][index]["id"] = webcams["webcamid"]
				resultcontainer["Placemarks"][index]["webcam_file_url"] = webcams["daylight_icon_url"]
				resultcontainer["Placemarks"][index]["lon"] = webcams["longitude"]
				resultcontainer["Placemarks"][index]["lat"] = webcams["latitude"]
				#resultcontainer["Placemarks"][index]["width"] = webcams["width"]
				#resultcontainer["Placemarks"][index]["height"] = webcams["height"]
				resultcontainer["Placemarks"][index]["upload_date"] = datetime.date.fromtimestamp(webcams["last_update"]).ctime()
				resultcontainer["Placemarks"][index]["owner_name"] = webcams["user"]
				resultcontainer["Placemarks"][index]["rating"] = webcams["rating_avg"]
				resultcontainer["Placemarks"][index]["rating_count"] = webcams["rating_count"]
				#resultcontainer["Placemarks"][index]["secret"] = webcams["secret"]
				index += 1
			return resultcontainer
		else:
			return False
		
	def proc_webcams_result(self, result):
		if result != False:
			self.clearList()
			self.delete_markers()
			if  result["count"] > result["start"]*result["size"]:
				list_item = xbmcgui.ListItem(__language__( 10003 ) % (str(result["size"])), '', "", "")
				list_item.setInfo( 'video', { "Title": __language__( 10003 ) % (str(result["size"])), "Genre": str(result["count"]) + " Webcams"})
				list_item.setProperty('type',"webcams")
				list_item.setProperty('next',"next")
				list_item.setProperty('start',str(result["start"]))
				list_item.setProperty('size',str(result["size"]))
				self.addItem(list_item)
			for webcam in result["Placemarks"]:	
				webcam["path"]="\\Webcams\\small\\"
				current = get_file(webcam["webcam_file_url"], "Webcams\\small\\"+str(webcam["id"])+".jpg", referer_url,'',self.add_webcams_hit,self,webcam,0)
				thread_starter=0
				while thread_starter<10:
					try:
						current.start()
						thread_starter=100
					except:
						time.sleep(1)
						thread_starter +=1

				#current.join(1000)
				

			self.getControl(2001).setVisible(1)
			
	def add_webcams_hit(self, webcam):
		list_item = xbmcgui.ListItem(webcam["name"], '', "", TEMPFOLDER + webcam["path"]+str(webcam["id"])+".jpg")
		list_item.setInfo( 'video', { "Title": webcam["name"], "Genre": "Date taken: " + webcam["upload_date"] + " - Owner: " + webcam["owner_name"]}) 				
		list_item.setProperty('Piclink', TEMPFOLDER + webcam["path"]+str(webcam["id"])+".jpg")
		list_item.setProperty('Title', urllib.quote(webcam["name"]))
		list_item.setProperty('Genre', urllib.quote("Date taken: " + webcam["upload_date"] + " - Owner: " + webcam["owner_name"]))
		list_item.setProperty('lon',str(webcam["lon"]))
		list_item.setProperty('lat',str(webcam["lat"]))
		list_item.setProperty('webcam_id',str(webcam["id"]))
		list_item.setProperty('id',str(webcam["id"]))
		list_item.setProperty('rating',str(webcam["rating"]))
		list_item.setProperty('rating_count',str(webcam["rating_count"]))
		list_item.setProperty('type',"webcams")
		self.markercontainer[str(webcam["id"])] = marker(self, float(webcam["lat"]), float(webcam["lon"]), TEMPFOLDER + webcam["path"]+str(webcam["id"])+".jpg",16,32,32,32)
		self.addItem(list_item,0)
		
	#Search Support
	def search_map(self, key_txt = ''):
		keyboard = xbmc.Keyboard(key_txt)
		keyboard.doModal()
		if keyboard.isConfirmed():
			search_string = ''
			search_string = keyboard.getText()
			self.connect()
			search_kml = self.xbmcearth_communication.get_Query_Place(referer_url, maps_key, search_string)
			result = self.parse_kml(search_kml)
			self.proc_search_result(result)
			self.drawSAT()
			self.xbmcearth_communication.get_Google_Analytics( referer_url,  urllib.quote("Search_Map"), urllib.quote("/xbmc_earth/search_map.html?q="+search_string+"&cat=Map_Search"),self)

	
	def proc_search_result(self, result):
		self.delete_markers()
		#Look at -> Single result zoom to result
		if "lookAT_lon" in result and "lookAT_lat" in result	:
			self.lon = result["lookAT_lon"]
			self.lat = result["lookAT_lat"]
		else:
		#more than one result -> calc zoomlevel to fit
			self.fit_placemarks(result["Placemarks"])
		#make resultlist in MainGUI
		self.clearList()
		index = 0
		for placemark in result["Placemarks"]:
			if "name" in placemark:
				pass
			else:
				placemark["name"] = 'error - no name'
			if "info" in placemark:
				pass
			else:
				placemark["info"] = ''
			index += 1
			if len(result["Placemarks"]) > 1:
				list_item = xbmcgui.ListItem(placemark["name"], '', BASE_RESOURCE_PATH + '\\skins\\Default\\media\\icon' + str(index) + '.png', BASE_RESOURCE_PATH + '\\skins\\Default\\media\\icon' + str(index) + '.png')
				if "lon" in placemark and "lat" in placemark:
					self.markercontainer[str(index)] = marker(self, float(placemark["lat"]), float(placemark["lon"]), BASE_RESOURCE_PATH + '\\skins\\Default\\media\\icon' + str(index) + '.png',12,38,24,38)
					list_item.setProperty('id',str(index))
			else:
				list_item = xbmcgui.ListItem(placemark["name"], '', BASE_RESOURCE_PATH + '\\skins\\Default\\media\\arrow.png', BASE_RESOURCE_PATH + '\\skins\\Default\\media\\arrow.png')
				if "lon" in placemark and "lat" in placemark:
					self.markercontainer["1"] = marker(self, float(placemark["lat"]), float(placemark["lon"]))
					list_item.setProperty('id','1')
					self.zoom = 1
			list_item.setInfo( 'video', { "Title": placemark["name"], "Genre": placemark["info"] }) 				
			list_item.setProperty('name', urllib.quote(placemark["name"]))
			if "lon" in placemark and "lat" in placemark:
				list_item.setProperty('lon',str(placemark["lon"]))
				list_item.setProperty('lat',str(placemark["lat"]))
			
			self.addItem(list_item)
		self.getControl(2001).setVisible(1)
		
		
	def fit_placemarks(self, placemarks):
		min_lon = 999.9
		max_lon = -999.9
		min_lat = 999.9
		max_lat = -999.9
		for placemark in placemarks:
			if "lon" in placemark and "lat" in placemark:
				if placemark["lon"] < min_lon:
					min_lon = placemark["lon"]
				if placemark["lon"] > max_lon:
					max_lon = placemark["lon"]
				if placemark["lat"] < min_lat:
					min_lat = placemark["lat"]
				if placemark["lat"] > max_lat:
					max_lat = placemark["lat"]
		if min_lon != 999.9 and max_lon != -999.9 and min_lat != 999.0 and max_lat != -999.0:
			self.lon = min_lon + ((max_lon-min_lon) / 2.0)
			self.lat = min_lat + ((max_lat-min_lat) / 2.0)
			googleearth_coordinates = Googleearth_Coordinates()
			coord=googleearth_coordinates.getTileRef(self.lon, self.lat, 0)
			coord_dist = googleearth_coordinates.getLatLong(coord)
			index = 1
			while ((max_lon - min_lon) > (coord_dist[2]*self.map_size_x) and (max_lat - min_lat) > (coord_dist[3]*self.map_size_y)):
				coord=googleearth_coordinates.getTileRef(self.lon, self.lat, index)
				coord_dist = googleearth_coordinates.getLatLong(coord)
				index += 1
			self.zoom = index

	def parse_kml(self, kml):
		if kml != False:
			resultcontainer = dict()
			xmldoc = minidom.parseString(kml)
			nodelist = xmldoc.getElementsByTagName("LookAt")
			for node in nodelist:
				node_temp = node
				sub_node2 = node_temp.getElementsByTagName('longitude')
				for node in sub_node2:
					Lon = float(node.firstChild.data)
					resultcontainer["lookAT_lon"] = Lon
				sub_node2 = node_temp.getElementsByTagName('latitude')
				for node in sub_node2:
					Lat = float(node.firstChild.data)
					resultcontainer["lookAT_lat"] = Lat
				sub_node2 = node_temp.getElementsByTagName('range')
				for node in sub_node2:
					Range =  float(node.firstChild.data)
					resultcontainer["lookAT_Range"] = Range
			nodelist = xmldoc.getElementsByTagName("Placemark")
			index = 0
			placemark_seq = []
			resultcontainer["Placemarks"] = placemark_seq
			for node in nodelist:
				placemark = dict()
				resultcontainer["Placemarks"].append(placemark)
				node_temp = node
				sub_node2 = node_temp.getElementsByTagName('name')
				for node in sub_node2:
					name = node.firstChild.data.encode('latin-1', 'ignore')
					resultcontainer["Placemarks"][index]["name"] = name
				sub_node2 = node_temp.getElementsByTagName('address')
				for node in sub_node2:
					address = node.firstChild.data.encode('latin-1', 'ignore').replace('<br/>','\n')
					resultcontainer["Placemarks"][index]["info"] = address
				sub_node2 = node_temp.getElementsByTagName('text')
				for node in sub_node2:
					x = node.firstChild.data.find('<img src="http://base.googlehosted.com/')
					if x != -1:
						url =  node.firstChild.data[x+10:node.firstChild.data.find('"/>',node.firstChild.data.find('<img src="http://base.googlehosted.com/'))].encode('UTF-8', 'ignore')
						resultcontainer["Placemarks"][index]["url"] = url
				sub_node2 = node_temp.getElementsByTagName('coordinates')
				for node in sub_node2:
					Lon = node.firstChild.data[0:node.firstChild.data.find(',')]
					Lat = node.firstChild.data[node.firstChild.data.find(',')+1:node.firstChild.data.find(',', node.firstChild.data.find(',')+1)]
					resultcontainer["Placemarks"][index]["lon"] = float(Lon)
					resultcontainer["Placemarks"][index]["lat"] = float(Lat)
				index += 1
			return resultcontainer
		
	def zoom_to_select(self, index):
		lon_temp = self.lon
		lat_temp = self.lat
		zoom_temp = self.zoom
		if self.getListItem(self.getCurrentListPosition()).getProperty('type')  == "Panoramio": 
			#Panoramio
			self.zoom_to_panoramio()			
		elif self.getListItem(self.getCurrentListPosition()).getProperty('type')  == "flickr":
			#FLICKR
			self.zoom_to_flickr()		
		elif self.getListItem(self.getCurrentListPosition()).getProperty('type')  == "locr":
			#locr
			self.zoom_to_locr()
		elif self.getListItem(self.getCurrentListPosition()).getProperty('type')  == "youtube":
			#youtube
			self.zoom_to_youtube()
		elif self.getListItem(self.getCurrentListPosition()).getProperty('type')  == "webcams":
			#webcams
			self.zoom_to_webcams()
		elif self.getListItem(self.getCurrentListPosition()).getProperty('lon') != '' and self.getListItem(self.getCurrentListPosition()).getProperty('lat') != '':
			lon_temp = float(self.getListItem(self.getCurrentListPosition()).getProperty('lon'))
			lat_temp = float(self.getListItem(self.getCurrentListPosition()).getProperty('lat'))
			if self.getListItem(self.getCurrentListPosition()).getProperty('zoom') != '':
				zoom_temp = int(self.getListItem(self.getCurrentListPosition()).getProperty('zoom'))
			elif zoom_temp > 2:
				zoom_temp = 2
		else:
			self.search_map(urllib.unquote(self.getListItem(self.getCurrentListPosition()).getProperty('name')))
			lon_temp = self.lon
			lat_temp = self.lat
			zoom_temp = self.zoom
			pass
		self.lon = lon_temp
		self.lat = lat_temp
		self.zoom = zoom_temp
		self.drawSAT()

	def zoom_to_panoramio(self):
		if self.getListItem(self.getCurrentListPosition()).getProperty('next')  == "next":
			self.proc_panoramio_result(self.getPanoramio(int(self.getListItem(self.getCurrentListPosition()).getProperty('start')),int(self.getListItem(self.getCurrentListPosition()).getProperty('size')) ))
			pass
		else:
			self.lon = float(self.getListItem(self.getCurrentListPosition()).getProperty('lon'))
			self.lat = float(self.getListItem(self.getCurrentListPosition()).getProperty('lat'))
			if self.getListItem(self.getCurrentListPosition()).getProperty('zoom') != '':
				self.zoom = int(self.getListItem(self.getCurrentListPosition()).getProperty('zoom'))
			elif self.zoom > 2:
				self.zoom = 2
			if self.getListItem(self.getCurrentListPosition()).getProperty('type')  == "Panoramio":
				if self.getListItem(self.getCurrentListPosition()).getProperty('photo_file_url') != '' and self.getListItem(self.getCurrentListPosition()).getProperty('width') != '' and self.getListItem(self.getCurrentListPosition()).getProperty('height') != '' and self.getListItem(self.getCurrentListPosition()).getProperty('photo_id') != '':
					self.getControl(2000).setVisible(0)
					#self.map_move = 2
					googleearth_coordinates = Googleearth_Coordinates()
					coord=googleearth_coordinates.getTileRef(self.lon, self.lat, self.zoom)
					coord_dist = googleearth_coordinates.getLatLong(coord)
					self.lon = self.lon - coord_dist[2]
					self.drawSAT()
					current = get_file(self.getListItem(self.getCurrentListPosition()).getProperty('photo_file_url'), "Panoramio\\medium\\m" + self.getListItem(self.getCurrentListPosition()).getProperty('photo_id') + ".jpg", referer_url)
					current.start()
					current.join(1000)
					cpic = Pic_GUI("script-%s-pic.xml" % ( __scriptname__.replace( " ", "_" ), ), os.getcwd(), "Default", 0,pic=TEMPFOLDER + "\\Panoramio\\medium\\m"+self.getListItem(self.getCurrentListPosition()).getProperty('photo_id')+".jpg", width=self.getListItem(self.getCurrentListPosition()).getProperty('width'), height=self.getListItem(self.getCurrentListPosition()).getProperty('height'), mainWindow = self)
					del cpic
					self.getControl(2000).setVisible(1)
	
	def zoom_to_flickr(self):
		if self.getListItem(self.getCurrentListPosition()).getProperty('next')  == "next":
			self.proc_flickr_result(self.getFlickr_bbox(int(self.getListItem(self.getCurrentListPosition()).getProperty('start')),int(self.getListItem(self.getCurrentListPosition()).getProperty('size')) ))
			pass
		else:
			self.lon = float(self.getListItem(self.getCurrentListPosition()).getProperty('lon'))
			self.lat = float(self.getListItem(self.getCurrentListPosition()).getProperty('lat'))
			if self.getListItem(self.getCurrentListPosition()).getProperty('zoom') != '':
				self.zoom = int(self.getListItem(self.getCurrentListPosition()).getProperty('zoom'))
			elif self.zoom > 2:
				self.zoom = 2
			if self.getListItem(self.getCurrentListPosition()).getProperty('type')  == "flickr":
				if self.getListItem(self.getCurrentListPosition()).getProperty('server') != '' and self.getListItem(self.getCurrentListPosition()).getProperty('secret') != '' and self.getListItem(self.getCurrentListPosition()).getProperty('farm') != '' and self.getListItem(self.getCurrentListPosition()).getProperty('photo_id') != '':
					self.getControl(2000).setVisible(0)
					#self.map_move = 2
					googleearth_coordinates = Googleearth_Coordinates()
					coord=googleearth_coordinates.getTileRef(self.lon, self.lat, self.zoom)
					coord_dist = googleearth_coordinates.getLatLong(coord)
					self.lon = self.lon - coord_dist[2]
					self.drawSAT()
					self.xbmcearth_communication.connect("farm"+str(self.getListItem(self.getCurrentListPosition()).getProperty('farm'))+".static.flickr.com")
					current = get_file("http://farm"+str(self.getListItem(self.getCurrentListPosition()).getProperty('farm'))+".static.flickr.com/"+str(self.getListItem(self.getCurrentListPosition()).getProperty('server'))+"/"+str(self.getListItem(self.getCurrentListPosition()).getProperty('photo_id'))+"_"+str(self.getListItem(self.getCurrentListPosition()).getProperty('secret'))+".jpg", "Flickr\\medium\\"+str(self.getListItem(self.getCurrentListPosition()).getProperty('photo_id'))+".jpg", referer_url)
					current.start()
					current.join(1000)
					im = Image.open(TEMPFOLDER + "\\Flickr\\medium\\"+self.getListItem(self.getCurrentListPosition()).getProperty('photo_id')+".jpg")
					size = im.size
					cpic = Pic_GUI("script-%s-pic.xml" % ( __scriptname__.replace( " ", "_" ), ), os.getcwd(), "Default", 0,pic=TEMPFOLDER + "\\Flickr\\medium\\"+self.getListItem(self.getCurrentListPosition()).getProperty('photo_id')+".jpg", width=size[0], height=size[1], mainWindow = self)
					del cpic
					self.getControl(2000).setVisible(1)
	
	def zoom_to_locr(self):
		if self.getListItem(self.getCurrentListPosition()).getProperty('next')  == "next":
			self.proc_locr_result(self.getLocr(int(self.getListItem(self.getCurrentListPosition()).getProperty('start')),int(self.getListItem(self.getCurrentListPosition()).getProperty('size')) ))
			pass
		else:
			self.lon = float(self.getListItem(self.getCurrentListPosition()).getProperty('lon'))
			self.lat = float(self.getListItem(self.getCurrentListPosition()).getProperty('lat'))
			if self.getListItem(self.getCurrentListPosition()).getProperty('zoom') != '':
				self.zoom = int(self.getListItem(self.getCurrentListPosition()).getProperty('zoom'))
			elif self.zoom > 2:
				self.zoom = 2
			if self.getListItem(self.getCurrentListPosition()).getProperty('type')  == "locr":
				if self.getListItem(self.getCurrentListPosition()).getProperty('photo_file_url') != '' and self.getListItem(self.getCurrentListPosition()).getProperty('width') != '' and self.getListItem(self.getCurrentListPosition()).getProperty('height') != '' and self.getListItem(self.getCurrentListPosition()).getProperty('photo_id') != '':
					self.getControl(2000).setVisible(0)
					#self.map_move = 2
					googleearth_coordinates = Googleearth_Coordinates()
					coord=googleearth_coordinates.getTileRef(self.lon, self.lat, self.zoom)
					coord_dist = googleearth_coordinates.getLatLong(coord)
					self.lon = self.lon - coord_dist[2]
					self.drawSAT()
					current = get_file(self.getListItem(self.getCurrentListPosition()).getProperty('photo_file_url'), "Locr\\medium\\" + self.getListItem(self.getCurrentListPosition()).getProperty('photo_id') + ".jpg", referer_url)
					current.start()
					current.join(1000)
					cpic = Pic_GUI("script-%s-pic.xml" % ( __scriptname__.replace( " ", "_" ), ), os.getcwd(), "Default", 0,pic=TEMPFOLDER + "\\Locr\\medium\\"+self.getListItem(self.getCurrentListPosition()).getProperty('photo_id')+".jpg", width=self.getListItem(self.getCurrentListPosition()).getProperty('width'), height=self.getListItem(self.getCurrentListPosition()).getProperty('height'), mainWindow = self)
					del cpic
					self.getControl(2000).setVisible(1)
	
	def zoom_to_youtube(self):
		if self.getListItem(self.getCurrentListPosition()).getProperty('next')  == "next":
			self.proc_youtube_result(self.getYoutube(int(self.getListItem(self.getCurrentListPosition()).getProperty('start')),int(self.getListItem(self.getCurrentListPosition()).getProperty('size')) ))
			pass
		else:
			self.lon = float(self.getListItem(self.getCurrentListPosition()).getProperty('lon'))
			self.lat = float(self.getListItem(self.getCurrentListPosition()).getProperty('lat'))
			if self.getListItem(self.getCurrentListPosition()).getProperty('zoom') != '':
				self.zoom = int(self.getListItem(self.getCurrentListPosition()).getProperty('zoom'))
			elif self.zoom > 2:
				self.zoom = 2
			if self.getListItem(self.getCurrentListPosition()).getProperty('type')  == "youtube":
				self.getControl(2000).setVisible(0)
				#self.map_move = 2
				googleearth_coordinates = Googleearth_Coordinates()
				coord=googleearth_coordinates.getTileRef(self.lon, self.lat, self.zoom)
				coord_dist = googleearth_coordinates.getLatLong(coord)
				self.lon = self.lon - coord_dist[2]
				self.drawSAT()

				self.xbmcearth_communication.connect("www.youtube.com")
				result = self.xbmcearth_communication.get_Youtube_html(referer_url,"?v="+self.getListItem(self.getCurrentListPosition()).getProperty('video_id'))
				if result != False:
					x = result.find('var swfArgs = ')
					result =result[x+14:result.find(';',x+15)]
					result = simplejson.loads(result)
					base_v_url = "http://youtube.com/get_video?video_id="+result["video_id"]+"&t="+result["t"]
					vid_url = self.xbmcearth_communication.stream_Youtube(base_v_url)
					self.Player.stop()
					try:
						self.Player.play(vid_url,'',1)
					except:
						print "old xbmc - starting fullscreen"
						self.Player.play(vid_url)
					self.playYoutube = True
				self.getControl(2000).setVisible(1)
					
	
	def zoom_to_webcams(self):
		if self.getListItem(self.getCurrentListPosition()).getProperty('next')  == "next":
			self.proc_webcams_result(self.getWebcams_bbox(int(self.getListItem(self.getCurrentListPosition()).getProperty('start')),int(self.getListItem(self.getCurrentListPosition()).getProperty('size')) ))
			pass
		else:
			self.lon = float(self.getListItem(self.getCurrentListPosition()).getProperty('lon'))
			self.lat = float(self.getListItem(self.getCurrentListPosition()).getProperty('lat'))
			if self.getListItem(self.getCurrentListPosition()).getProperty('zoom') != '':
				self.zoom = int(self.getListItem(self.getCurrentListPosition()).getProperty('zoom'))
			elif self.zoom > 2:
				self.zoom = 2
			if self.getListItem(self.getCurrentListPosition()).getProperty('type')  == "webcams":
				self.getControl(2000).setVisible(0)
				#self.map_move = 2
				googleearth_coordinates = Googleearth_Coordinates()
				coord=googleearth_coordinates.getTileRef(self.lon, self.lat, self.zoom)
				coord_dist = googleearth_coordinates.getLatLong(coord)
				self.lon = self.lon - coord_dist[2]
				self.drawSAT()
				current = get_file("http://images.webcams.travel/webcam/" + self.getListItem(self.getCurrentListPosition()).getProperty('id')+".jpg", "Webcams\\medium\\" + self.getListItem(self.getCurrentListPosition()).getProperty('id') + ".jpg", referer_url,'','','','',0)
				current.start()
				current.join(1000)
				im = Image.open(TEMPFOLDER + "\\Webcams\\medium\\"+self.getListItem(self.getCurrentListPosition()).getProperty('id')+".jpg")
				size = im.size
				cpic = Pic_GUI("script-%s-pic.xml" % ( __scriptname__.replace( " ", "_" ), ), os.getcwd(), "Default", 0,pic=TEMPFOLDER + "\\Webcams\\medium\\"+self.getListItem(self.getCurrentListPosition()).getProperty('id')+".jpg", width=size[0], height=size[1], mainWindow = self)
				del cpic
				self.getControl(2000).setVisible(1)
	
	
	
					
	#handle map	
	def map_mov(self):
		if self.map_move == 0:
			self.pic_size = self.pic_size_full
			self.map_move = 1
			#Move Map to Fullscreen
			self.xbmcearth_communication.get_Google_Analytics( referer_url,  urllib.quote("switch to mapmove"), urllib.quote("/xbmc_earth/switch_to_mapmove.html"),self)
			for x in range(self.map_size_x):
				for y in range(self.map_size_y):
					Pic_size = self.pic_size
					Map_pos_x = (self.map_pos_x_full - Pic_size) + (Pic_size*x)
					Map_pos_y = (self.map_pos_y_full - Pic_size) + (Pic_size*y)
					self.satBlocks[x][y].setPosition(Map_pos_x,Map_pos_y)
					self.mapBlocks[x][y].setPosition(Map_pos_x,Map_pos_y)
					self.satBlocks[x][y].setWidth(Pic_size)
					self.satBlocks[x][y].setHeight(Pic_size)
					self.mapBlocks[x][y].setWidth(Pic_size)
					self.mapBlocks[x][y].setHeight(Pic_size)
			self.redraw_markers()
			self.route_pic.setPosition(self.map_pos_x_full - Pic_size,self.map_pos_y_full - Pic_size)
			self.route_pic.setHeight(Pic_size*3)
			self.route_pic.setWidth(Pic_size*3)
		else:
			self.map_move = 0
			self.pic_size = self.pic_size_windowed
			#Move Map to Window
			for x in range(self.map_size_x):
				for y in range(self.map_size_y):
					Pic_size = self.pic_size
					Map_pos_x = (self.map_pos_x_windowed - Pic_size) + (Pic_size*x)
					Map_pos_y = (self.map_pos_y_windowed - Pic_size) + (Pic_size*y)
					self.satBlocks[x][y].setPosition(Map_pos_x,Map_pos_y)
					self.mapBlocks[x][y].setPosition(Map_pos_x,Map_pos_y)
					self.satBlocks[x][y].setWidth(Pic_size)
					self.satBlocks[x][y].setHeight(Pic_size)
					self.mapBlocks[x][y].setWidth(Pic_size)
					self.mapBlocks[x][y].setHeight(Pic_size)
			self.route_pic.setPosition(self.map_pos_x_windowed - Pic_size,self.map_pos_y_windowed - Pic_size)
			self.route_pic.setHeight(Pic_size*3)
			self.route_pic.setWidth(Pic_size*3)
			self.redraw_markers()
				
	def drawHYBRID(self):
		current = draw_map(self,self.mapBlocks)
		current.start()
		current.join()
		
	def drawSAT(self):
		"""
		import nasa_onearth
		nasa = nasa_onearth.draw_nasa(self,self.nasa_view)
		nasa.start()
		"""
		if self.show_weather == True:
			import weather
			weatherdata = weather.get_weather(self)
			weatherdata.start()
		sat = draw_sat(self,self.satBlocks)
		sat.start()
		map = draw_map(self,self.mapBlocks)
		map.start()
		self.redraw_markers()
		virtualEarth = draw_virtualearth(self,self.satBlocks)
		virtualEarth.start()
		sat.join()
		map.join()
		virtualEarth.join()
		if self.routecontainer['enable'] == 1:
			self.makeRoute(self.routecontainer['linestring'])
			self.route_pic.setVisible(True)
		else:
			self.route_pic.setVisible(False)
		if self.hybrid == 1:
			self.xbmcearth_communication.get_Google_Analytics( referer_url,  urllib.quote("Google Hybrid"), "/xbmc_earth/browse/Google/Hybrid_act.html",self)
		elif self.hybrid == 2:
			self.xbmcearth_communication.get_Google_Analytics( referer_url,  urllib.quote("Google Map"), "/xbmc_earth/browse/Google/Map_act.html",self)
		elif self.hybrid == 3:
			self.xbmcearth_communication.get_Google_Analytics( referer_url,  urllib.quote("Google Area"), "/xbmc_earth/browse/Google/Area_act.html",self)
		elif self.hybrid == 0:
			self.xbmcearth_communication.get_Google_Analytics( referer_url,  urllib.quote("Google Satelite"), "/xbmc_earth/browse/Google/Satelite_act.html",self)
		elif self.hybrid == 4:
			self.xbmcearth_communication.get_Google_Analytics( referer_url,  urllib.quote("VirtualEarth Satelite"), "/xbmc_earth/browse/VirtualEarth/Satelite_act.html",self)
		elif self.hybrid == 5:
			self.xbmcearth_communication.get_Google_Analytics( referer_url,  urllib.quote("VirtualEarth Hybrid"), "/xbmc_earth/browse/VirtualEarth/Hybrid_act.html",self)
		elif self.hybrid == 6:
			self.xbmcearth_communication.get_Google_Analytics( referer_url,  urllib.quote("VirtualEarth Map"), "/xbmc_earth/browse/VirtualEarth/Map_act.html",self)
		

	def redraw_markers(self):
		if self.playYoutube == False:
			for v,x in self.markercontainer.items():
				x.redraw_Marker()
	
	def hide_markers(self):
		for v,x in self.markercontainer.items():
			x.hide_Marker()
			
	def pulse_markers(self,pulse):
		for v,x in self.markercontainer.items():
			x.pulse_Marker(0)
		self.markercontainer[pulse].pulse_Marker(1)		
					
			
	def delete_markers(self):
		#for v,x in self.markercontainer.items():
		#	x.pop()
		try:
			while 1==1:
				self.markercontainer.popitem()
		except:
			pass
		
	def makeRoute(self, LineString ):
		text = 'test-string'
		fmt='PNG'
		im = Image.new('RGBA', (self.map_size_x*self.pic_size,self.map_size_y*self.pic_size), (0,0,0,0))
		d = ImageDraw.Draw(im)
		x, y = im.size
		d = aggdraw.Draw(im)
		p = aggdraw.Pen("blue", 5, 180)
		path = aggdraw.Path()
		line = LineString.split(' ')
		for point in line:
			if len(point) > 0:
				point_lon = float(point[0:point.find(',')])
				point_lat = float(point[point.find(',')+1:point.find(',', point.find(',')+1)])
				pos = self.get_current_POS(point_lon,point_lat)
				path.lineto(pos[0],pos[1])
		if self.map_move == 1:
			d.path((0,75),path,p)
		else:
			d.path((-130,-80),path,p)
		d.flush()

		im = im.filter(ImageFilter.EDGE_ENHANCE_MORE)
		# write image to filesystem
		im.save(TEMPFOLDER + '\\Route\\Route.png', format=fmt,**{"optimize":1})
		self.route_pic.setImage('')
		self.route_pic.setImage(TEMPFOLDER + '\\Route\\Route.png')
		
	
	def get_current_POS(self, lon_marker, lat_marker):
		self.x_offset = 0
		self.y_offset = 0
		self.x_size = 1
		self.y_size = 1
		self.lat_marker = lat_marker
		self.lon_marker = lon_marker
		googleearth_coordinates = Googleearth_Coordinates()
		coord=googleearth_coordinates.getTileRef(self.lon, self.lat, self.zoom)
		self.coord_dist = googleearth_coordinates.getLatLong(coord)
		map_center_x = int(self.map_size_x / 2)
		map_center_y = int(self.map_size_y / 2)
		self.pos = self.satBlocks[map_center_x][map_center_y].getPosition()
		self.x_res = self.coord_dist[2]/self.pic_size
		self.y_res = self.coord_dist[3]/self.pic_size
		lon_marker = self.lon_marker-self.coord_dist[0]
		lat_marker = self.lat_marker-self.coord_dist[1]
		gui_pos = []
		gui_pos.append(self.pos[0]+int((lon_marker/self.x_res))-self.x_offset)
		gui_pos.append(self.pos[1]+(self.pic_size)-int((lat_marker/self.y_res))-self.y_offset)
		return gui_pos
		
	def findTileURLs(self, maps_js):
		#URL_satPic = "http://khm2.google.com/kh?v=   44"
		#              http://khm0.google.com/kh?v\x3d34\x26hl\x3dde\x26
		#                                    /kh?v=   34&   hl=   de&   x=22&y=10&z=5&s=Gali
		#URL_mapHybrid = "http://mt0.google.com/mt?v=   w2t.88            &   x="
		#                 http://mt0.google.com/mt?v\x3dapt.88\x26hl\x3dde\x26
		#                                      /mt?v=w2   t.88&   hl=   de&   x=22&y=10&z=5&s=Gali 
		#URL_mapStreet = "http://mt0.google.com/mt?v=   w2.88&x="
		#                 http://mt0.google.com/mt?v\x3dap.88\x26hl\x3dde\x26
		#                                      /mt?v=   w2.89&   hl=   de&   x=22&y=12&z=5&s=Galile
		#URL_mapArea = "http://mt0.google.com/mt?v=   w2p.87&               x="
		#               http://mt0.google.com/mt?v\x3dapp.87\x26hl\x3dde\x26
		#                                    /mt?v=   w2p.87&   hl=   de&   x=15&y=9&z=5&s=Galile 
		apiCallback = maps_js[maps_js.find('apiCallback('):maps_js.find(';',maps_js.find('apiCallback('))]
		apiCallback = apiCallback.split('[')
		api_mapStreet = apiCallback[1][1:apiCallback[1].find(']')].replace('"','').split(',')
		mapStreet = api_mapStreet[0].replace('\\x3d','=').replace('\\x26','&').replace('ap','w2')
		print mapStreet[0:len(mapStreet)-1]
		self.URL_mapStreet = mapStreet[0:len(mapStreet)-1]
		
		api_satPIC = apiCallback[2][1:apiCallback[2].find(']')].replace('"','').split(',')
		satPIC = api_satPIC[0].replace('\\x3d','=').replace('\\x26','&').replace('ap','w2')
		print satPIC[0:len(satPIC)-1]
		self.URL_satPic = satPIC[0:len(satPIC)-1]
		
		api_mapHybrid = apiCallback[3][1:apiCallback[3].find(']')].replace('"','').split(',')
		mapHybrid = api_mapHybrid[0].replace('\\x3d','=').replace('\\x26','&').replace('ap','w2')
		print mapHybrid[0:len(mapHybrid)-1]
		self.URL_mapHybrid = mapHybrid[0:len(mapHybrid)-1]
		
		api_mapArea = apiCallback[4][1:apiCallback[4].find(']')].replace('"','').split(',')
		mapArea = api_mapArea[0].replace('\\x3d','=').replace('\\x26','&').replace('ap','w2')
		print mapArea[0:len(mapArea)-1]
		self.URL_mapArea = mapArea[0:len(mapArea)-1]
		
class marker:
	x_res = 0.0
	y_res = 0.0
	pos = []
	coord_dist = []
	lat_marker = 0.0
	lon_marker = 0.0
	def __init__ (self,window, lat_marker, lon_marker, pic_path =  BASE_RESOURCE_PATH + '\\skins\\Default\\media\\arrow.png', x_offset=8,y_offset=39, x_size=34,y_size=39):
		self.window = window
		self.lat_marker = lat_marker
		self.lon_marker = lon_marker
		self.pic_path = pic_path
		self.x_offset = x_offset
		self.y_offset = y_offset
		self.x_size = x_size
		self.y_size = y_size
		self.add_Marker()
		
	def add_Marker(self):
		pos = self.get_current_POS()
		self.marker_pic = xbmcgui.ControlImage(pos[0],pos[1],self.x_size,self.y_size, self.pic_path)
		self.window.addControl(self.marker_pic)
	
	def pulse_Marker(self, on_off):
		if on_off == 1:
			self.marker_pic.setAnimations([('conditional', 'effect=zoom pulse=true start=100 end=120 center=auto time=1000 condition=Control.HasFocus(50)')])
		else:
			self.marker_pic.setAnimations([('conditional', 'effect=zoom start=100 end=100 center=auto time=1000 condition=Control.HasFocus(50)')])

	def hide_Marker(self):
		self.marker_pic.setVisible(0)
	
	def redraw_Marker(self):
		pos = self.get_current_POS()
		self.marker_pic.setPosition(pos[0],pos[1])
		if pos[2] == 0:
			self.marker_pic.setVisible(0)
		else:
			self.marker_pic.setVisible(1)
		
	def get_current_POS(self):
		googleearth_coordinates = Googleearth_Coordinates()
		coord=googleearth_coordinates.getTileRef(self.window.lon, self.window.lat, self.window.zoom)
		self.coord_dist = googleearth_coordinates.getLatLong(coord)
		map_center_x = int(self.window.map_size_x / 2)
		map_center_y = int(self.window.map_size_y / 2)
		self.pos = self.window.satBlocks[map_center_x][map_center_y].getPosition()
		self.x_res = self.coord_dist[2]/self.window.pic_size
		self.y_res = self.coord_dist[3]/self.window.pic_size
		lon_marker = self.lon_marker-self.coord_dist[0]
		lat_marker = self.lat_marker-self.coord_dist[1]
		gui_pos = []
		gui_pos.append(self.pos[0]+int((lon_marker/self.x_res))-self.x_offset)
		gui_pos.append(self.pos[1]+(self.window.pic_size)-int((lat_marker/self.y_res))-self.y_offset)
		gui_pos.append(1) #draw Marker =1 ; hideMarker = 0
		# check if marker is in window
		pos = self.window.satBlocks[0][0].getPosition()
		if gui_pos[0] < pos[0] or gui_pos[1] < pos[1]:
			gui_pos[2] = 0
		pos = self.window.satBlocks[self.window.map_size_x-1][self.window.map_size_y-1].getPosition()
		if gui_pos[0] > (pos[0] + self.window.pic_size) or gui_pos[1] > (pos[0] + self.window.pic_size):
			gui_pos[2] = 0
		return gui_pos
		
	def __del__(self):
		self.window.removeControl(self.marker_pic)
		pass

class draw_sat(Thread):
	xbmcearth_communication = Xbmcearth_communication()
	def __init__ (self, window, satBlocks):
		Thread.__init__(self)
		self.window = window
		self.satBlocks = satBlocks


	def run(self):
		if self.window.hybrid <= 1:
			googleearth_coordinates = Googleearth_Coordinates()
			Lon = self.window.lon
			Lat = self.window.lat
			Zoom = self.window.zoom
			coord=googleearth_coordinates.getTileRef(Lon, Lat, Zoom)
			tileCoord = []
			tileCoord = googleearth_coordinates.getTileCoord(Lon, Lat, Zoom-1)
			resultset =[]
			coord_dist = googleearth_coordinates.getLatLong(coord)
			
			spn = str(coord_dist[2])+','+str(coord_dist[3])
			t = 'k'
			z = str(Zoom)
			vp = str(coord_dist[0]) + ',' + str(coord_dist[1])
			ev = 'p'
			v = '24'
			
			self.xbmcearth_communication.connect("maps.google.com")
			copyright_xml = self.xbmcearth_communication.get_Maps_Copyright(referer_url, maps_key, spn, t, z, vp, ev, v)
			
			satlist = []
			map_center_x = int(self.window.map_size_x / 2)
			map_center_y = int(self.window.map_size_y / 2)
			for x in range(self.window.map_size_x):
				for y in range(self.window.map_size_y):
					Lon = (self.window.lon - coord_dist[2]*map_center_x)+coord_dist[2]*x
					Lat = (self.window.lat + coord_dist[3]*map_center_y)-coord_dist[3]*y
					coord=googleearth_coordinates.getTileRef(Lon, Lat, Zoom)
					current = get_file(self.window.URL_satPic + coord, "Sat\\z"+str(Zoom)+"\\"+coord+".png", referer_url,self.satBlocks[x][y])
					satlist.append(current)
					thread_starter=0
					while thread_starter<10:
						try:
							current.start()
							thread_starter=100
						except:
							time.sleep(1)
							thread_starter +=1
					#current.join(100)
		else:
			try:
				for x in range(self.window.map_size_x):
					for y in range(self.window.map_size_y):
						self.satBlocks[x][y].setVisible(False)
			except: pass
			
		
class draw_map(Thread):
	def __init__ (self, window, mapBlocks):
		Thread.__init__(self)
		self.mapBlocks = mapBlocks
		self.window = window
	def run(self):
		if self.window.hybrid == 1:
			googleearth_coordinates = Googleearth_Coordinates()
			Lon = self.window.lon
			Lat = self.window.lat
			Zoom = self.window.zoom
			coord=googleearth_coordinates.getTileRef(Lon, Lat, Zoom)
			coord_dist =[]
			coord_dist = googleearth_coordinates.getLatLong(coord)
			maplist = []
			map_center_x = int(self.window.map_size_x / 2)
			map_center_y = int(self.window.map_size_y / 2)
			for x in range(self.window.map_size_x):
				for y in range(self.window.map_size_y):
					Lon = (self.window.lon - coord_dist[2]*map_center_x)+coord_dist[2]*x
					Lat = (self.window.lat + coord_dist[3]*map_center_y)-coord_dist[3]*y					
					coord=googleearth_coordinates.getTileRef(Lon, Lat, Zoom)
					Map_Tile = googleearth_coordinates.getTileCoord(Lon, Lat, Zoom-1)
					current = get_file(self.window.URL_mapHybrid + "&x="+ str(Map_Tile[0]) + "&y=" + str(Map_Tile[1]) + "&z=" + str(18-Zoom), "Hyb\\z"+str(Zoom)+"\\"+str(Map_Tile[0]) + str(Map_Tile[1])+".png", referer_url,self.mapBlocks[x][y])
					maplist.append(current)
					thread_starter=0
					while thread_starter<10:
						try:
							current.start()
							thread_starter=100
						except:
							time.sleep(1)
							thread_starter +=1
					#current.join(100)
		elif self.window.hybrid == 2:
			googleearth_coordinates = Googleearth_Coordinates()
			Lon = self.window.lon
			Lat = self.window.lat
			Zoom = self.window.zoom
			coord=googleearth_coordinates.getTileRef(Lon, Lat, Zoom)
			coord_dist =[]
			coord_dist = googleearth_coordinates.getLatLong(coord)
			maplist = []
			map_center_x = int(self.window.map_size_x / 2)
			map_center_y = int(self.window.map_size_y / 2)
			for x in range(self.window.map_size_x):
				for y in range(self.window.map_size_y):
					Lon = (self.window.lon - coord_dist[2]*map_center_x)+coord_dist[2]*x
					Lat = (self.window.lat + coord_dist[3]*map_center_y)-coord_dist[3]*y					
					coord=googleearth_coordinates.getTileRef(Lon, Lat, Zoom)
					Map_Tile = googleearth_coordinates.getTileCoord(Lon, Lat, Zoom-1)
					current = get_file(self.window.URL_mapStreet + "&x="+ str(Map_Tile[0]) + "&y=" + str(Map_Tile[1]) + "&z=" + str(18-Zoom), "Map\\z"+str(Zoom)+"\\m"+str(Map_Tile[0]) + str(Map_Tile[1])+".png", referer_url,self.mapBlocks[x][y])
					maplist.append(current)
					thread_starter=0
					while thread_starter<10:
						try:
							current.start()
							thread_starter=100
						except:
							time.sleep(1)
							thread_starter +=1
					#current.join(100)
		elif self.window.hybrid == 3:
			googleearth_coordinates = Googleearth_Coordinates()
			Lon = self.window.lon
			Lat = self.window.lat
			Zoom = self.window.zoom
			if Zoom < 3:
				Zoom = 3
			coord=googleearth_coordinates.getTileRef(Lon, Lat, Zoom)
			coord_dist =[]
			coord_dist = googleearth_coordinates.getLatLong(coord)
			maplist = []
			map_center_x = int(self.window.map_size_x / 2)
			map_center_y = int(self.window.map_size_y / 2)
			for x in range(self.window.map_size_x):
				for y in range(self.window.map_size_y):
					Lon = (self.window.lon - coord_dist[2]*map_center_x)+coord_dist[2]*x
					Lat = (self.window.lat + coord_dist[3]*map_center_y)-coord_dist[3]*y					
					coord=googleearth_coordinates.getTileRef(Lon, Lat, Zoom)
					Map_Tile = googleearth_coordinates.getTileCoord(Lon, Lat, Zoom-1)
					current = get_file(self.window.URL_mapArea + "&x="+ str(Map_Tile[0]) + "&y=" + str(Map_Tile[1]) + "&z=" + str(18-Zoom), "Area\\z"+str(Zoom)+"\\a"+str(Map_Tile[0]) + str(Map_Tile[1])+".png", referer_url,self.mapBlocks[x][y])
					maplist.append(current)
					thread_starter=0
					while thread_starter<10:
						try:
							current.start()
							thread_starter=100
						except:
							time.sleep(1)
							thread_starter +=1
					#current.join(100)
		else:
			try:
				for x in range(self.window.map_size_x):
					for y in range(self.window.map_size_y):
						self.mapBlocks[x][y].setVisible(False)
			except: pass
			
class draw_virtualearth(Thread):
	xbmcearth_communication = Xbmcearth_communication()
	def __init__ (self, window, satBlocks):
		Thread.__init__(self)
		self.window = window
		self.satBlocks = satBlocks


	def run(self):
		if self.window.hybrid >=4:
			virtualEarthTileSystem = VirtualEarthTileSystem()
			Lon = self.window.lon
			Lat = self.window.lat
			Zoom = 18 - self.window.zoom
			coord = virtualEarthTileSystem.LatLongToPixelXY(Lat, Lon, Zoom)
			coord[0] = int(coord[0]) - 256
			coord[1] = int(coord[1]) - 256
			
			satlist = []
			for x in range(self.window.map_size_x):
				for y in range(self.window.map_size_y):
					pixelx = coord[0] + 256*x
					pixely = coord[1] + 256*y
					tile = virtualEarthTileSystem.PixelXYToTileXY(pixelx,pixely)
					Key= virtualEarthTileSystem.TileXYToQuadKey( tile[0], tile[1], Zoom)
					if self.window.hybrid ==4: #VirtualEarth Sat
						current = get_file("http://t2.tiles.virtualearth.net/tiles/a"+Key+".jpeg?g=234&mkt=de-de", "MSHSat\\z"+str(Zoom)+"\\"+Key+".jpg", referer_url,self.satBlocks[x][y])
					elif self.window.hybrid ==5: #VirtualEarth Hybrid
						current = get_file("http://t2.tiles.virtualearth.net/tiles/h"+Key+".jpeg?g=234&mkt=de-de", "MSHybrid\\z"+str(Zoom)+"\\"+Key+".jpg", referer_url,self.satBlocks[x][y])
					elif self.window.hybrid ==6: #VirtualEarth Map
						current = get_file("http://t2.tiles.virtualearth.net/tiles/r"+Key+".png?g=234&mkt=de-de", "MSMap\\z"+str(Zoom)+"\\"+Key+".png", referer_url,self.satBlocks[x][y])
					
					satlist.append(current)
					thread_starter=0
					while thread_starter<10:
						try:
							current.start()
							thread_starter=100
						except:
							time.sleep(1)
							thread_starter +=1
					#current.join(100)
		else:
			try:
				for x in range(self.window.map_size_x):
					for y in range(self.window.map_size_y):
						self.satBlocks[x][y].setVisible(False)
			except: pass


						
						
class file_remove(Thread):
	def __init__(self,MainWindow):
		Thread.__init__(self)
		self.mainWindow = MainWindow
	
	def run(self):
		while(run_backgroundthread > 0 ):
			for folder in glob.glob(TEMPFOLDER + "\\*\\*"):        
				# select the type of file, for instance *.jpg or all files *.*    
				if (run_backgroundthread > 0):
					i = 0
					#while(run_backgroundthread > 0 and i < 2):
					#	time.sleep(1)
					#	i += 1
					date_file_list = []
					if len(glob.glob(folder + '/*.*'))>50:
						for file in glob.glob(folder + '/*.*'):               
							stats = os.stat(file)    
							lastmod_date = time.localtime(stats[8])        
							date_file_tuple = lastmod_date, file        
							date_file_list.append(date_file_tuple) 
						date_file_list.sort()
						for file in date_file_list[0:len(glob.glob(folder + '/*.*'))-50]:      
							try:                                
								os.remove(file[1])      
							except OSError:                
								print 'Could not remove', file_name
			i = 0
			while(run_backgroundthread > 0 and i < 120):
				time.sleep(1)
				i += 1


class background_thread(Thread):
	def __init__(self,window):
		Thread.__init__(self)
		self.window = window
		self.temp = 0
	
	def run(self):
		while(run_backgroundthread > 0):
			try:
				time.sleep(1)
				if self.window.getCurrentListPosition() != -1:
					self.window.pulse_markers(self.window.getListItem(self.window.getCurrentListPosition()).getProperty('id'))
				if self.window.showLargeOverlay == True:
					self.window.getControl(2004).setVisible(True) #Show VideoOverlay
				else:
					self.window.getControl(2004).setVisible(False) #Hide VideoOverlay
			except:
				pass
				#LOG( LOG_ERROR, self.__class__.__name__, "[%s]", sys.exc_info()[ 1 ] )	



######################################################################################
def updateScript(silent=False, notifyNotFound=False):
        print "> updateScript() silent=%s" %silent

        updated = False
        up = update.Update(__language__, __scriptname__)
        version = up.getLatestVersion(silent)
        print "Current Version: %s Tag Version: %s" % (__version__,version)
        if version and version != "-1":
                if __version__ < version:
                        if xbmcgui.Dialog().yesno( __language__(0), \
                                                                "%s %s %s." % ( __language__(1006), version, __language__(1002) ), \
                                                                __language__(1003 )):
                                updated = True
                                up.makeBackup()
                                up.issueUpdate(version)
                elif notifyNotFound:
                        dialogOK(__language__(0), __language__(1000))
#       elif not silent:
#               dialogOK(__language__(0), __language__(1030))                           # no tagged ver found

        del up
        print "< updateScript() updated=%s" % updated
        return updated

if __name__ == '__main__':
	# This is the main call 
	#mydisplay = MainClass()
	scriptUpdated = updateScript(False, False)
	if scriptUpdated == False:
		mydisplay = MainClass("script-%s-main.xml" % ( __scriptname__.replace( " ", "_" ), ), os.getcwd(), "Default", 0)
		mydisplay.doModal()
		del mydisplay