import xbmc, xbmcgui

# Script constants
__author__ = 'BigBellyBilly [BigBellyBilly@gmail.com]'
__date__ = '10-06-2009'
xbmc.log( "[MODULE]: %s Dated: %s loaded!" % (__name__, __date__))

#################################################################################################################
class TextViewDialog( xbmcgui.WindowXMLDialog ):
	""" A TextView window """

	XML_FILENAME = "DialogScriptInfo.xml"
	EXIT_CODES = (9, 10, 216, 257, 275, 216, 61506, 61467,)

	def __init__( self, *args, **kwargs):
		pass
		
	def onInit( self ):
		try:
			self.getControl( 5 ).setText( self.text )
			self.getControl( 3 ).setLabel( self.title )
		except: pass

	def onClick( self, controlId ):
		pass

	def onFocus( self, controlId ):
		pass

	def onAction( self, action ):
		try:
			buttonCode =  action.getButtonCode()
			actionID   =  action.getId()
		except: return
		if actionID in self.EXIT_CODES or buttonCode in self.EXIT_CODES:
			self.close()

	def ask(self, title="", text="", fn=None ):
		if not title and fn:
			self.title = fn
		else:
			self.title = title
		if fn:
			try:
				self.text = file(xbmc.translatePath(fn)).read()
			except:
				self.text = "Failed to load file: %s" % fn
		else:
			self.text = text

		self.doModal()
