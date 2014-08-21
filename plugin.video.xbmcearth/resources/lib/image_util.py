"""
    Module for creating images / Such as route overlays
"""

import sys
import os
import random

# Log status codes
LOG_ERROR, LOG_INFO, LOG_NOTICE, LOG_DEBUG = range( 1, 5 )


#sys.path.append( os.path.join( os.path.dirname( sys.modules[ "pil_util" ].__file__ ), "_PIL.zip" ) )
from PIL import Image, ImageFont, ImageDraw, ImageFilter

def makeRoute( ImageName ):
	try:
		text = 'test-string'
		print('1')
		fnt = BASE_RESOURCE_PATH + '\\skins\\Default\\media\\1.ttf'
		fnt_sz = 25
		fmt='JPEG'
		fgcolor = random.randint(0,0xffff00)
		bgcolor = fgcolor ^ 0xffffff
		font = ImageFont.truetype(fnt,fnt_sz)
		print('2')
		dim = font.getsize(text)
		im = Image.new('RGB', (dim[0]+5,dim[1]+5), bgcolor)
		d = ImageDraw.Draw(im)
		x, y = im.size
		r = random.randint
		print('3')
		for num in range(100):
			d.rectangle((r(0,x),r(0,y),r(0,x),r(0,y)),fill=r(0,0xffffff))
		d.text((3,3), text, font=font, fill=fgcolor)
		im = im.filter(ImageFilter.EDGE_ENHANCE_MORE)
		file_name = 'testpic.jpg'
		print('4')
		# write image to filesystem
		im.save('Q:\\temp\\test.jpg', format=fmt)
		print('5')
		return True
	except:
		LOG( LOG_ERROR,  "[%s]", sys.exc_info()[ 1 ] )	
		return False


def LOG( status,  format, *args ):
	_function_ = "(%s) ::%s" % ( sys._getframe( 1 ).f_code.co_filename,  sys._getframe( 1 ).f_code.co_name, )
	xbmc.output( "%s: %s - %s\n" % ( ( "ERROR", "INFO", "NOTICE", "DEBUG", )[ status - 1 ], _function_, format % args, ) )
