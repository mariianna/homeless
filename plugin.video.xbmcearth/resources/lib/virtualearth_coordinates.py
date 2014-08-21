import xbmc, xbmcgui, time, threading, datetime, os, math
from math import pi, sin, cos, log, exp, atan, floor

class VirtualEarthTileSystem:   
	EarthRadius = 6378137
	MinLatitude = -85.05112878
	MaxLatitude = 85.05112878
	MinLongitude = -180
	MaxLongitude = 180

	"""
	/// <summary>
	/// Clips a number to the specified minimum and maximum values.
	/// </summary>
	/// <param name="n">The number to clip.</param>
	/// <param name="minValue">Minimum allowable value.</param>
	/// <param name="maxValue">Maximum allowable value.</param>
	/// <returns>The clipped value.</returns>
	"""
	def Clip(self, n, minValue, maxValue):
		return min(max(n, minValue), maxValue)


	"""
	/// <summary>
	/// Determines the map width and height (in pixels) at a specified level
	/// of detail.
	/// </summary>
	/// <param name="levelOfDetail">Level of detail, from 1 (lowest detail)
	/// to 23 (highest detail).</param>
	/// <returns>The map width and height in pixels.</returns>
	"""
	def MapSize(self, levelOfDetail):
		return 256 << levelOfDetail


	"""
	/// <summary>
	/// Determines the ground resolution (in meters per pixel) at a specified
	/// latitude and level of detail.
	/// </summary>
	/// <param name="latitude">Latitude (in degrees) at which to measure the
	/// ground resolution.</param>
	/// <param name="levelOfDetail">Level of detail, from 1 (lowest detail)
	/// to 23 (highest detail).</param>
	/// <returns>The ground resolution, in meters per pixel.</returns>
	"""
	def GroundResolution(self, latitude, levelOfDetail):
		latitude = self.Clip(latitude, self.MinLatitude, self.MaxLatitude)
		return math.cos(latitude * math.pi / 180) * 2 * math.pi * self.EarthRadius / self.MapSize(levelOfDetail)


	"""
	/// <summary>
	/// Determines the map scale at a specified latitude, level of detail,
	/// and screen resolution.
	/// </summary>
	/// <param name="latitude">Latitude (in degrees) at which to measure the
	/// map scale.</param>
	/// <param name="levelOfDetail">Level of detail, from 1 (lowest detail)
	/// to 23 (highest detail).</param>
	/// <param name="screenDpi">Resolution of the screen, in dots per inch.</param>
	/// <returns>The map scale, expressed as the denominator N of the ratio 1 : N.</returns>
	"""
	def MapScale(self, latitude, levelOfDetail, screenDpi):
		return self.GroundResolution(latitude, levelOfDetail) * screenDpi / 0.0254


	"""
	/// <summary>
	/// Converts a point from latitude/longitude WGS-84 coordinates (in degrees)
	/// into pixel XY coordinates at a specified level of detail.
	/// </summary>
	/// <param name="latitude">Latitude of the point, in degrees.</param>
	/// <param name="longitude">Longitude of the point, in degrees.</param>
	/// <param name="levelOfDetail">Level of detail, from 1 (lowest detail)
	/// to 23 (highest detail).</param>
	/// <param name="pixelX">Output parameter receiving the X coordinate in pixels.</param>
	/// <param name="pixelY">Output parameter receiving the Y coordinate in pixels.</param>
	"""
	def LatLongToPixelXY(self, latitude, longitude, levelOfDetail):
		latitude = self.Clip(latitude, self.MinLatitude, self.MaxLatitude)
		longitude = self.Clip(longitude, self.MinLongitude, self.MaxLongitude)

		x = (longitude + 180) / 360; 
		sinLatitude = math.sin(latitude * math.pi / 180);
		y = 0.5 - math.log((1 + sinLatitude) / (1 - sinLatitude)) / (4 * math.pi)

		mapSize = self.MapSize(levelOfDetail)
		pixelX = int(self.Clip(x * mapSize + 0.5, 0, mapSize - 1))
		pixelY = int(self.Clip(y * mapSize + 0.5, 0, mapSize - 1))
		return [pixelX, pixelY]


	"""
	/// <summary>
	/// Converts pixel XY coordinates into tile XY coordinates.
	/// </summary>
	/// <param name="pixelX">Pixel X coordinate.</param>
	/// <param name="pixelY">Pixel Y coordinate.</param>
	/// <param name="tileX">Output parameter receiving the tile X coordinate.</param>
	/// <param name="tileY">Output parameter receiving the tile Y coordinate.</param>
	"""
	def PixelXYToTileXY(self, pixelX, pixelY):
		tileX = pixelX / 256
		tileY = pixelY / 256
		return [tileX, tileY]


	"""
	/// <summary>
	/// Converts tile XY coordinates into a QuadKey at a specified level of detail.
	/// </summary>
	/// <param name="tileX">Tile X coordinate.</param>
	/// <param name="tileY">Tile Y coordinate.</param>
	/// <param name="levelOfDetail">Level of detail, from 1 (lowest detail)
	/// to 23 (highest detail).</param>
	/// <returns>A string containing the QuadKey.</returns>
	"""
	def TileXYToQuadKey(self, tileX, tileY, levelOfDetail):
		quadKey = ''
		i = levelOfDetail
		while i>0:
			digit = 0
			mask = 1 << (i - 1)
			if ((tileX & mask) != 0):
				digit += 1
			if ((tileY & mask) != 0):
				digit += 1
				digit += 1
			quadKey += str(digit)
			i -= 1
		return quadKey