import xbmc, xbmcgui, time, threading, datetime, os, math
from math import pi, sin, cos, log, exp, atan, floor


class Googleearth_Coordinates:
	"""
	returns a keyhole string for a longitude (x), latitude (y), and zoom
	"""
	def getTileRef(self, lon, lat, zoom):
		zoom = 18 - zoom
		
		# first convert the lat lon to transverse mercator coordintes.
		if lon > 180.0:
			lon -= 360.0
		
		lon /= 180.0
		
		# convert latitude to a range -1..+1
		lat = math.log(math.tan((math.pi / 4.0) + ((0.5 * math.pi * lat) / 180.0))) / math.pi
		
		tLat      = -1.0
		tLon      = -1.0
		lonWidth  = 2.0
		latHeight = 2.0
		keyholeString = 't'
		
		for i in range(0 , zoom, +1):
			lonWidth /= 2.0
			latHeight /= 2.0
		
			if ((tLat + latHeight) >= lat):
				if ((tLon + lonWidth) > lon):
					keyholeString = keyholeString + 't'
				else:
					tLon += lonWidth
					keyholeString = keyholeString + 's'
			else:
				tLat += latHeight
				if ((tLon + lonWidth) >= lon):
					keyholeString = keyholeString + 'q'
				else:
					tLon = tLon + lonWidth
					keyholeString = keyholeString + 'r'
				
		return keyholeString;
		
	def getDistance ( self, latitudeA, longitudeA, latitudeB, longitudeB ):
		EQUATORIAL_RADIUS_KM = 6378.137

		latA = latitudeA / 180.0 * math.pi
		lonA = longitudeA / 180.0 * math.pi
		latB = latitudeB / 180.0 * math.pi
		lonB = longitudeB / 180.0 * math.pi
		return math.acos (math.sin (latA) * math.sin (latB) + math.cos (latA) * math.cos (latB) * math.cos (lonB - lonA)) * EQUATORIAL_RADIUS_KM;
		
	"""
	returns a Rectangle2D with x = lon, y = lat, width=lonSpan, height=latSpan for a keyhole string.
	"""
	def getLatLong(self, keyholeStr):
		#must start with "t"
		resultset = []
		if ((len(keyholeStr) == 0) or (keyholeStr[0] != 't')):
			print("Keyhole string must start with 't'")
			return resultset
		
		
		lon      = -180.0 #x
		lonWidth = 360.0 #width 360
		
		#lat = -90  # y
		#latHeight = 180 # height 180
		lat       = -1.0
		latHeight = 2.0
		
		#for (int i = 1; i < keyholeStr.length(); i++) {
		for i in range(1, len(keyholeStr), +1):
			lonWidth /= 2.0
			latHeight /= 2.0
		
			c = keyholeStr[i]
		
			if c == 's':
				#lat += latHeight
				lon += lonWidth
			elif c == 'r':
				lat += latHeight
				lon += lonWidth
			elif c == 'q':
				lat += latHeight
				#lon += lonWidth
			elif c == 't':		
				#lat += latHeight
				#lon += lonWidth
				pass
			else:
				print("unknown char '" + c + "' when decoding keyhole string.")
				return resultset
		
		# convert lat and latHeight to degrees in a transverse mercator projection
		# note that in fact the coordinates go from about -85 to +85 not -90 to 90! 85.05112877980660
		
		latHeight += lat
		latHeight = (2.0 * math.atan(math.exp(math.pi * latHeight))) - (math.pi / 2.0)
		#var latitude =  (math.pi/2) - (2 * Math.atan(Math.exp(-1.0 * y / this.radius)));
		latHeight *= (180.0 / math.pi)
		
		lat = (2.0 * math.atan(math.exp(math.pi * lat))) - (math.pi / 2.0)
		lat *= (180.0 / math.pi)
		latHeight -= lat
		#latHeight = (math.pi/2.0)-(2.*math.atan(math.exp(-1*128/((256*math.pow(2,zoom))/(2*math.pi)))))
		
		if (lonWidth < 0.0):
			lon      = lon + lonWidth
			lonWidth = -lonWidth
		
		if (latHeight < 0.0):
			lat       = lat + latHeight
			latHeight = -latHeight
		
		#lat = Math.asin(lat) * 180 / Math.PI
		resultset.append(lon)
		resultset.append(lat)
		resultset.append(lonWidth)
		resultset.append(latHeight)
		return resultset

	def getTileCoord(self, lon, lat, zoom):
		resultset = []
		#making Constants
		bc = 2*math.pi
		Wa = math.pi/180
		c = 256
		for i in range (17, zoom, -1):
			c = c*2
		pixelsPerLonDegree = c / 360.0
		pixelsPerLonRadian = c / bc
		bitmapOrigo_X = c / 2
		bitmapOrigo_Y = c / 2
		numTiles = c / c
		
		#getTileCoordinate
		d_X = 0
		d_Y = 0
		thispplon = pixelsPerLonDegree
		sp_X = bitmapOrigo_X
		sp_Y = bitmapOrigo_Y
		
		newX = int(math.floor((sp_X) + (lon * thispplon)))
		d_X = newX
		e = math.sin(lat*Wa)
		if(e > 0.9999):
			e = 0.9999        
		if(e < -0.9999):
			e = -0.9999
		thispplonrad = pixelsPerLonRadian
		newY = int(math.floor(sp_Y + 0.5 * math.log((1+e)/(1-e)) * -1 * thispplonrad))
		d_Y = newY
		d_X = int(math.floor(d_X/256))
		d_Y = int(math.floor(d_Y/256))
		
		resultset.append(d_X)
		resultset.append(d_Y)
		"""
		#Constants used for degree to radian conversion, and vice-versa.
		DTOR = pi / 180.
		RTOD = 180. / pi
		TILE_SIZE = 256
		num_zoom=18
		# Google's tilesize is 256x256, square tiles are assumed.
		tilesize = TILE_SIZE
		zoom = 17 - zoom
		# Initializing arrays to hold the parameters for each
		#  one of the zoom levels.
		degpp = [] # Degrees per pixel
		radpp = [] # Radians per pixel
		npix  = [] # 1/2 the number of pixels for a tile at the given zoom level
		resultset = []
		# Incrementing through the zoom levels and populating the
		#  parameter arrays.
		z = TILE_SIZE # The number of pixels per zoom level.
		for i in xrange(num_zoom):
			# Getting the degrees and radians per pixel, and the 1/2 the number of
			#  for every zoom level.
			degpp.append(z / 360.) # degrees per pixel
			radpp.append(z / (2 * pi)) # radians per pixl
			npix.append(z / 2) # number of pixels to center of tile

			# Multiplying `z` by 2 for the next iteration.
			z *= 2

		# Calculating the pixel x coordinate by multiplying the longitude
		#  value with with the number of degrees/pixel at the given
		#  zoom level.
		px_x = round(npix[zoom] + (lon * degpp[zoom]))

		# Creating the factor, and ensuring that 1 or -1 is not passed in as the 
		#  base to the logarithm.  Here's why:
		#   if fac = -1, we'll get log(0) which is undefined; 
		#   if fac =  1, our logarithm base will be divided by 0, also undefined.
		fac = min(max(sin(DTOR * lat), -0.9999), 0.9999)

		# Calculating the pixel y coordinate.
		px_y = round(npix[zoom] + (0.5 * log((1 + fac)/(1 - fac)) * (-1.0 * radpp[zoom])))
		
		# Returning the pixel x, y to the caller of the function.
		d_X = floor(px_x / TILE_SIZE)
		d_Y = floor(px_y / TILE_SIZE)
		resultset.append(int(d_X))
		resultset.append(int(d_Y))
		"""

		return resultset
