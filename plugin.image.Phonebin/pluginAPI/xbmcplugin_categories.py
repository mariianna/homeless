"""
	Category module: list of categories to use as folders
"""

# main imports
import os, sys
import time
import string
import xbmc, xbmcgui, xbmcplugin
from urllib import quote_plus, unquote_plus
from urlparse import urljoin
#from pprint import pprint

from pluginAPI.bbbLib import *

HOME_DIR = os.getcwd()
TEMP_DIR = "special://temp"

__plugin__ = sys.modules[ "__main__" ].__plugin__
__lang__ = xbmc.Language( HOME_DIR ).getLocalizedString

log("Module: %s loaded!" % __name__)

#################################################################################################################
class _Info:
	def __init__(self, *args, **kwargs ):
		self.__dict__.update( kwargs )
		log( "Info() __dict__=%s" % self.__dict__ )


#################################################################################################################
#################################################################################################################
class Main:
	# base paths
	BASE_URL = "http://www.phonebin.com"
	PHOTOS_URL = BASE_URL + "/photos.cfm/s/%s"
	COMMENTS_URL = BASE_URL + "/comments.cfm"
	YESTERDAY_TOP_URL = BASE_URL + "/today.cfm"
	MONTH_TOP_URL = BASE_URL + "/month.cfm"
	VIDEOS_URL = BASE_URL + "/videos.cfm"
	VIDEO_PLAYER_URL = BASE_URL + "/scripts/pbplayer.swf?id="
	ALBUMS_URL = BASE_URL + "/albums.cfm"

	BASE_PLUGIN_THUMBNAIL_PATH = os.path.join( HOME_DIR, "thumbnails" )
	NEXT_IMG =  os.path.join( BASE_PLUGIN_THUMBNAIL_PATH, "next.png" )

	def __init__( self ):
		self._parse_argv()                      # parse sys.argv

		if ( not sys.argv[ 2 ] ):
			# cleanup for new start
			for f in os.listdir(TEMP_DIR):
				if f.startswith(__plugin__):
#					print f
					deleteFile("/".join( [TEMP_DIR, f] ))

			# start
			ok = self.get_categories()
		else:
			exec "ok = self.%s()" % ( self.args.category, )

		log("call endOfDirectory() %s" % ok)
		xbmcplugin.endOfDirectory( int( sys.argv[ 1 ] ), ok) #, self.updateListing, self.cacheToDisc)

	########################################################################################################################
	def _parse_argv(self):
		if ( not sys.argv[ 2 ] ):
			self.args = _Info( title="" )
		else:
			# call Info() with our formatted argv to create the self.args object
			# replace & with , first as they're the args split char.  Then decode.
			try:
				exec "self.args = _Info(%s)" % ( unquote_plus( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ) ), )
			except:
				handleException("_parse_argv")

	########################################################################################################################
	def get_categories( self ):
		log( "> get_categories()")
		try:
			ok = True

			categories = (
					( __lang__( 30950 ), "fetch_photos", self.PHOTOS_URL % 1, ),
					( __lang__( 30951 ), "fetch_comments", None, ),
					( __lang__( 30952 ), "fetch_photos", self.YESTERDAY_TOP_URL, ),
					( __lang__( 30953 ), "fetch_photos", self.MONTH_TOP_URL, ),
					( __lang__( 30954 ), "fetch_photos", self.VIDEOS_URL, ),
					( __lang__( 30955 ), "list_albums", "open", ),
					( __lang__( 30956 ), "list_albums", "lib", ),
				)
			sz = len( categories )
			for ( ltitle, method, arg ) in categories:
				# set the callback url
				url = '%s?title=%s&category=%s' % ( sys.argv[ 0 ], encodeText( ltitle ), repr( method ), )
				if arg:
					url += "&arg=%s" % repr( arg )

				# only need to add label, icon and thumbnail, setInfo() and addSortMethod() takes care of label2
				li=xbmcgui.ListItem( ltitle )
				# add the item to the media list
				ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=li, isFolder=True, totalItems=sz )

			xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
			xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content="files")
			xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=self.args.title )
		except:
			handleException("get_categories")
			ok = False

		log( "< get_categories() ok=%s" % ok)
		return ok


	########################################################################################################################
	def fetch_comments(self):
		log("> fetch_comments()")
		ok = False

		try:
			page_url = self.COMMENTS_URL
			parsed_fn =  "%s_comments.dat" % (__plugin__)
			parsed_filepath = "/".join( [TEMP_DIR, parsed_fn] )

			# load existing parsed details obj file
			items = loadFileObj(parsed_filepath)
			if not items:
				dialogProgress.create(__plugin__,  __lang__(30921), self.args.title)
				doc = fetchURL(page_url)
				dialogProgress.close()
				if not doc: raise "empty"

				# extract main table section
				section = self._find_main_table(doc)
				if not section: raise "empty"

				# parse webpage
				# find photo links
				items = findAllRegEx(section, '<img src="(photos/thumbs/.+?)".*?>Comment:<.*?/img/\d+">(.*?)<')
#				pprint (items)
				if items:
					saveFileObj(parsed_filepath, items)

			if not items:
				raise "empty"
			else:
				sz = len(items)
				# PHOTOS
				icon = "defaultPicture.png"
				for item in items:
					photo_thumb = urljoin(self.BASE_URL, item[0])
					photo_img = photo_thumb.replace("thumbs","main")
					photo_comment = item[1].replace("\n"," ").replace("\r"," ").strip()

					li=xbmcgui.ListItem( photo_comment,  "", icon, photo_thumb)
					li.setInfo("Pictures", {"Title" : photo_comment})
					# add the item to the media list
					ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=photo_img, listitem=li, isFolder=False, totalItems=sz )

			xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
			xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content="pictures")
			xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=self.args.title )
		except "empty":
			messageOK(self.args.title, __lang__(30901), self.args.title, page_url)
		except:
			handleException("fetch_comments")
			ok = False

		log( "< fetch_comments() ok=%s" % ok)
		return ok

	########################################################################################################################
	def fetch_photos(self):
		log("> fetch_photos()")
		ok = False

		try:
			page_url = self.args.arg
			page_title = self.args.title
			# get website section
			web_section = searchRegEx(page_url, ".com/(\w+)")       # eg. photos or videos or animals or babes etc
			log("web_section=" + web_section)
			page_from_url_regex = "/s/(\d+)"

			try:
				photo_idx = int(searchRegEx(page_url, page_from_url_regex))   # photo start idx of this page, from url
			except:
				# amend url to point to first page
				photo_idx = 1
				if "/s/" not in page_url:
					if web_section == "videos":
						page_url += "/s/1"
					else:
						page_url += "/photos.cfm/s/1"
					log("amending page url to have first page idx: " + page_url)
			parsed_fn =  "%s_%s_%s.dat" % (__plugin__, web_section, photo_idx)
			parsed_filepath = "/".join( [TEMP_DIR, parsed_fn] )

			# set regex according to web_section
			if web_section == "videos":
				web_section_img_src = "videos"
			else:
				web_section_img_src = "photos"
			log("web_section_img_src=" + web_section_img_src)

			# load existing parsed details obj file
			items = loadFileObj(parsed_filepath)
			if not items:
				log("no pre-parsed file, download from web")
				items = []
				dialogProgress.create(__plugin__, "")

				# fetch as many pages required - based on setting
				items_regex = 'img src="(%s.*?)".*?title="(.*?)"' % web_section_img_src
				log("items_regex=" + items_regex)
				next_page_regex = 'href="(\w*.\w+.cfm/s/\d+)'
				max_photos_regex = '>\d+ - \d+ of (.*?) '
				webpage_photo_max = 20
				first_photo_idx = photo_idx
				max_photos = 0

				# loop to fetch pages according to photos to show in settings
				pagesize = int(xbmcplugin.getSetting( "pagesize" ))
				max_pages = int(pagesize / webpage_photo_max)
				
				for count in range(max_pages):
					to_photo_idx = photo_idx + webpage_photo_max-1
					if max_photos and to_photo_idx > max_photos:
						to_photo_idx = max_photos
					msg = "%s (%s -> %s)" % (self.args.title, photo_idx, to_photo_idx)
					log("processing: " + msg)
					percent = int( (count * 100.0) / max_pages )
					dialogProgress.update(percent, __lang__(30921), msg)
					doc = fetchURL(page_url)
					if not doc: break

					# extract main table section
					section = self._find_main_table(doc)
					if not section:
						log("table section missing!")
						break

					# parse webpage
					# find photo links
					items += findAllRegEx(section, items_regex)

					# find next page url
					next_page_url = searchRegEx(doc, next_page_regex)
					log("next_page_url="+ next_page_url)
					if next_page_url:
						page_url = urljoin(self.BASE_URL, next_page_url)
						photo_idx = int(searchRegEx(next_page_url, page_from_url_regex))
						log("photo_idx=%s" % photo_idx)
						if not max_photos:
							try:
								# exists if more than one page
								max_photos = int(searchRegEx(doc, max_photos_regex).replace(',',''))
							except: pass
							log("max_photos=%s" % max_photos)

						# break if looped all photo pages
						if photo_idx >= max_photos or photo_idx < first_photo_idx:
							log("photo_idx maxed, no more pages")
							photo_idx = max_photos
							page_url = ""
							break
					else:
						# no more pages
						photo_idx += webpage_photo_max
						page_url = ""
						break

#				pprint (items)
				if items:
					photo_range = "(%s - %s)" % (first_photo_idx, photo_idx)
					log("photo_range=" + photo_range)
					items.insert(0, (photo_range, page_url))
					saveFileObj(parsed_filepath, items)
				dialogProgress.close()

			sz = len(items)
			if sz <= 1:
				raise "empty"
			else:
				page_info = items[0]
				page_title = "%s %s" % (self.args.title, page_info[0])	# photo_range

				# NEXT PAGE - saved to 1st line in items
				next_url = page_info[1]
				if next_url:
					li_url = '%s?title=%s&category=%s&arg=%s' % \
							( sys.argv[ 0 ], repr( self.args.title), repr( 'fetch_photos' ), repr( next_url ))
					li=xbmcgui.ListItem( __lang__(30922), "", self.NEXT_IMG, self.NEXT_IMG )	# next page
					ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=li_url, listitem=li, isFolder=True, totalItems=sz)

				# PHOTOS
				if web_section == "videos":
					icon = "defaultVideo.png"
				else:
					icon = "defaultPicture.png"
				for item in items[1:]:
					photo_thumb = urljoin(self.BASE_URL, item[0])
					log("photo_thumb=" + photo_thumb)
					photo_title = item[1]

					li=xbmcgui.ListItem( photo_title,  "", icon, photo_thumb)
					if web_section == "videos":
#						"http://www.phonebin.com/scripts/pbplayer.swf?id=2009-04/715F5A28-7E9D-444B-97669F04BDDC16B8"
						url = (photo_thumb.replace(".jpg","")) + ".flv"
						li_url = '%s?title=%s&category=%s&arg=%s' % \
								( sys.argv[ 0 ], encodeText( photo_title ), repr( "playVideo" ), repr( url ), )
						li.setInfo("video", {"Title" : photo_title})
					else:
						li_url = photo_thumb.replace("thumbs","main")
						li.setInfo("Pictures", {"Title" : photo_title})

					# add the item to the media list
					ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=li_url, listitem=li, isFolder=False, totalItems=sz )

			xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
			if web_section == "videos":
				xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content="movies")
			else:
				xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content="pictures")
			xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=page_title )
		except "empty":
			deleteFile(parsed_filepath) # delete any old file
			messageOK(self.args.title, __lang__(30901), self.args.title, page_url)
		except:
			handleException("fetch_photos")
			ok = False

		log( "< fetch_photos() ok=%s" % ok)
		return ok

	########################################################################################################################
	def list_albums(self):
		""" Folder list of Album Library A..Z and 9 """
		log("> list_albums()")
		ok = False

		try:
			# FOLDERS
			if self.args.arg == "open":
				items = ( "Animals", "Arty", "Babe", "Celeb", "Drunk", "Friends", "Holiday", "Nude", "Office", "Oops",
						  "Ouch", "Party", "Portrait", "Pub", "Scenic", "Sport", "Vehicles", "Hall Of Fame" )
			else:
				items = string.uppercase + "9"
			sz = len(items)

			for item in items:
				ltitle = self.args.title + ": " + item
				# adjust url for a special categorys
				if item == "Hall Of Fame":
					arg = "hof"
				elif self.args.arg == "open":
					arg = urljoin(self.ALBUMS_URL, item.lower())
					url = '%s?title=%s&category=%s&arg=%s' % ( sys.argv[ 0 ], repr( ltitle ), repr( "fetch_photos" ), repr( arg ))
				else:
					url = '%s?title=%s&category=%s&arg=%s' % ( sys.argv[ 0 ], repr( ltitle ), repr( "list_album_lib" ), repr( item ))
	
				li=xbmcgui.ListItem( item )
				ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=li, isFolder=True, totalItems=sz )

			xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
			xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content="files")
			xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=self.args.title )
		except:
			handleException("list_albums")
			ok = False

		log( "< list_albums() ok=%s" % ok)
		return ok

	########################################################################################################################
	def list_album_lib(self):
		log("> list_album_lib()")
		ok = False

		try:
			page_url = "/".join( [self.ALBUMS_URL, "l", self.args.arg] )
			parsed_fn =  "%s_album_lib_%s.dat" % (__plugin__, self.args.arg)
			log("parsed_fn=" + parsed_fn)
			parsed_filepath = "/".join( [TEMP_DIR, parsed_fn] )

			# load existing parsed details obj file
			items = loadFileObj(parsed_filepath)
			if not items:
				dialogProgress.create(__plugin__,  __lang__(30921), self.args.title)
				doc = fetchURL(page_url)
				dialogProgress.close()
				if not doc: raise "empty"

				# extract main table section
				section = self._find_main_table(doc)
				if section:
					# get 2nd occurance section
					section = self._find_main_table(section)
				if not section: raise "empty"

				# parse webpage
				# find link, title, count
				items = findAllRegEx(section, '<a href="(.*?)/"><b>(.*?)</b></a>(.*?)</')
#				pprint (items)
				if items:
					saveItems = []
					for item in items:
						try:
							if int(searchRegEx(item[2], "(\d+)")) > 0:
								saveItems.append(item)
						except:
							log("no photos, folder ignored: " + item[1])

					log("items: %d of which saved: %d" % (len(items), len(saveItems)))
					if saveItems:
						saveFileObj(parsed_filepath, saveItems)
					items = saveItems

			if not items:
				raise "empty"
			else:
				sz = len(items)
				# FOLDERS
				for item in items:
					arg = urljoin(self.BASE_URL, item[0])
					ltitle = item[1] + item[2]
					url = '%s?title=%s&category=%s&arg=%s' % ( sys.argv[ 0 ], repr( ltitle ), repr( "fetch_photos" ), repr( arg ))

					li=xbmcgui.ListItem( ltitle)
					ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=li, isFolder=True, totalItems=sz )

			xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
			xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content="files")
			xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=self.args.title )
		except "empty":
			deleteFile(parsed_filepath) # delete any old file
			messageOK(self.args.title, __lang__(30901), self.args.title, page_url)
		except:
			handleException("list_album_lib")
			ok = False

		log( "< list_album_lib() ok=%s" % ok)
		return ok


	########################################################################################################################
	def _find_main_table(self, doc):
		try:
			start = find(doc, "images/main/box_bgn.gif")
			return doc[start+23:]
		except:
			log("_find_main_table() not found")
			return doc

	########################################################################################################################
	def playVideo(self):
		""" play flash video file """
		return playMedia(self.args.arg)
