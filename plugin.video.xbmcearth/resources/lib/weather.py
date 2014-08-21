import xbmc, xbmcgui, datetime, tarfile, os, glob, urllib, httplib, sys, os.path, time, datetime, urllib2, traceback
from threading import Thread

BASE_RESOURCE_PATH = os.path.join( os.getcwd().replace( ";", "" ), "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

__language__ = xbmc.Language( os.getcwd() ).getLocalizedString 
from xml.dom import minidom 
from threading import Thread
from googleearth_coordinates import  Googleearth_Coordinates
from xbmcearth_communication import Xbmcearth_communication
from xbmcearth_communication import get_file
from global_data import *
TEMPFOLDER = os.path.join( os.getcwd().replace( ";", "" ), "temp" )

class get_weather(Thread):

	xbmcearth_communication = Xbmcearth_communication()
	def __init__ (self, window):
		Thread.__init__(self)
		self.window = window
	
	def run(self):
		googleearth_coordinates = Googleearth_Coordinates()
		Lon = str(int(self.window.lon*1000000))
		Lat = str(int(self.window.lat*1000000))
		self.xbmcearth_communication.connect("www.google.com")
		result = self.xbmcearth_communication.get_Weather(referer_url,"?weather=,,,"+Lat+","+Lon)
		try:
			if result != '':
				resultcontainer = dict()
				xmldoc = minidom.parseString(result)
				nodelist = xmldoc.getElementsByTagName("current_conditions")
				resultcontainer["current_conditions"] = dict()
				self.window.getControl(951).setLabel("aktuell")
				for node in nodelist:
					sub_nodes = node.getElementsByTagName("condition")
					for sub_node in sub_nodes:
						resultcontainer["current_conditions"]["condition"] = sub_node.getAttribute("data").encode('latin-1', 'ignore')
						self.window.getControl(953).setLabel(str(resultcontainer["current_conditions"]["condition"]))
					sub_nodes = node.getElementsByTagName("temp_f")
					for sub_node in sub_nodes:
						resultcontainer["current_conditions"]["temp_f"] = sub_node.getAttribute("data").encode('latin-1', 'ignore')
					sub_nodes = node.getElementsByTagName("temp_c")
					for sub_node in sub_nodes:
						resultcontainer["current_conditions"]["temp_c"] = sub_node.getAttribute("data").encode('latin-1', 'ignore')
						self.window.getControl(952).setLabel(str(resultcontainer["current_conditions"]["temp_c"]) + "°C / " + str(resultcontainer["current_conditions"]["temp_f"]) + "°F")
					sub_nodes = node.getElementsByTagName("humidity")
					for sub_node in sub_nodes:	
						resultcontainer["current_conditions"]["humidity"] = sub_node.getAttribute("data").encode('latin-1', 'ignore')
						self.window.getControl(954).setLabel(str(resultcontainer["current_conditions"]["humidity"]))
					sub_nodes = node.getElementsByTagName("icon")
					for sub_node in sub_nodes:	
						resultcontainer["current_conditions"]["icon"] = sub_node.getAttribute("data").encode('latin-1', 'ignore')
						filename = resultcontainer["current_conditions"]["icon"][resultcontainer["current_conditions"]["icon"].rfind('/')+1:len(resultcontainer["current_conditions"]["icon"])].replace(' ','')
					current = get_file("http://www.google.com"+resultcontainer["current_conditions"]["icon"],"weather\\icons\\"+str(filename), referer_url,self.window.getControl(950))
					thread_starter=0
					while thread_starter<10:
						try:
							current.start()
							thread_starter=100
						except:
							time.sleep(1)
							thread_starter +=1
					sub_nodes = node.getElementsByTagName("wind_condition")
					for sub_node in sub_nodes:	
						resultcontainer["current_conditions"]["wind_condition"] = sub_node.getAttribute("data")
						self.window.getControl(955).setLabel(str(resultcontainer["current_conditions"]["wind_condition"]))
				nodelist = xmldoc.getElementsByTagName("forecast_conditions")
				resultcontainer["forecast_conditions"] = []
				index = 0
				for node in nodelist:
					resultcontainer["forecast_conditions"].append(dict())
					sub_nodes = node.getElementsByTagName("day_of_week")
					for sub_node in sub_nodes:
						resultcontainer["forecast_conditions"][index]["day_of_week"] = sub_node.getAttribute("data").encode('latin-1', 'ignore')
						self.window.getControl(961+(index*10)).setLabel(str(resultcontainer["forecast_conditions"][index]["day_of_week"]))
					sub_nodes = node.getElementsByTagName("low")
					for sub_node in sub_nodes:
						resultcontainer["forecast_conditions"][index]["low"] = sub_node.getAttribute("data").encode('latin-1', 'ignore')
						if xbmc.getLanguage() == 'German':
							self.window.getControl(965+(index*10)).setLabel("min: " +str(resultcontainer["forecast_conditions"][index]["low"]) + "°C")
						else:
							self.window.getControl(965+(index*10)).setLabel("min: " +str(resultcontainer["forecast_conditions"][index]["low"]) + "°F")
					sub_nodes = node.getElementsByTagName("high")
					for sub_node in sub_nodes:	
						resultcontainer["forecast_conditions"][index]["high"] = sub_node.getAttribute("data").encode('latin-1', 'ignore')
						if xbmc.getLanguage() == 'German':
							self.window.getControl(964+(index*10)).setLabel("max: "+str(resultcontainer["forecast_conditions"][index]["high"]) + "°C")
						else:
							self.window.getControl(964+(index*10)).setLabel("max: "+str(resultcontainer["forecast_conditions"][index]["high"]) + "°F")
					sub_nodes = node.getElementsByTagName("icon")
					for sub_node in sub_nodes:	
						resultcontainer["forecast_conditions"][index]["icon"] = sub_node.getAttribute("data").encode('latin-1', 'ignore')
						filename = resultcontainer["forecast_conditions"][index]["icon"][resultcontainer["forecast_conditions"][index]["icon"].rfind('/')+1:len(resultcontainer["forecast_conditions"][index]["icon"])].replace(' ','')
					current = get_file("http://www.google.com"+resultcontainer["forecast_conditions"][index]["icon"],"weather\\icons\\"+str(filename), referer_url,self.window.getControl(960+(index*10)))
					thread_starter=0
					while thread_starter<10:
						try:
							current.start()
							thread_starter=100
						except:
							time.sleep(1)
							thread_starter +=1
					sub_nodes = node.getElementsByTagName("condition")
					for sub_node in sub_nodes:	
						resultcontainer["forecast_conditions"][index]["condition"] = sub_node.getAttribute("data").encode('latin-1', 'ignore')
						self.window.getControl(963+(index*10)).setLabel(str(resultcontainer["forecast_conditions"][index]["condition"]))
					index += 1
		except:
			traceback.print_exc()