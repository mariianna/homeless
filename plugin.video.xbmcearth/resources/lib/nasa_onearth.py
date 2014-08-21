#http://wms.jpl.nasa.gov/tiled.html

import xbmc, xbmcgui, datetime, tarfile, os, glob, urllib, httplib, sys, os.path, time, datetime, urllib2
from threading import Thread

BASE_RESOURCE_PATH = os.path.join( os.getcwd().replace( ";", "" ), "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

__language__ = xbmc.Language( os.getcwd() ).getLocalizedString 

from threading import Thread
from googleearth_coordinates import  Googleearth_Coordinates
from xbmcearth_communication import Xbmcearth_communication
from xbmcearth_communication import get_file
from global_data import *
TEMPFOLDER = os.path.join( os.getcwd().replace( ";", "" ), "temp" )

class draw_nasa(Thread):
	xbmcearth_communication = Xbmcearth_communication()
	def __init__ (self, window, image):
		Thread.__init__(self)
		self.window = window
		self.image = image


	def run(self):
		googleearth_coordinates = Googleearth_Coordinates()
		Lon = self.window.lon
		Lat = self.window.lat
		Zoom = self.window.zoom
		coord=googleearth_coordinates.getTileRef(Lon, Lat, Zoom)
		coord_dist = googleearth_coordinates.getLatLong(coord)
		self.xbmcearth_communication.connect("wms.jpl.nasa.gov")
		map_center_x = int(self.window.map_size_x / 2)
		map_center_y = int(self.window.map_size_y / 2)
		current = get_file("http://wms.jpl.nasa.gov/wms.cgi?request=GetMap&layers=daily_planet&srs=EPSG:4326&format=image/jpeg&styles=&width="+str(768)+"&height="+str(768)+"&bbox="+str(coord_dist[0]-coord_dist[2])+","+str(coord_dist[1]-coord_dist[3])+","+str(coord_dist[0]+coord_dist[2]*2)+","+str(coord_dist[1]+coord_dist[3]*2),"Nasa\\z"+str(Zoom)+"\\"+coord+".jpg", referer_url,self.image)
		thread_starter=0
		while thread_starter<10:
			try:
				current.start()
				thread_starter=100
			except:
				time.sleep(1)
				thread_starter +=1