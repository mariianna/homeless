# -*- coding: utf-8 -*-

# Debug
Debug = False

# plugin constants
__plugin__ = "The Guild"
__boxee_author__ = "Jeremy Milum"
__xbmc_author__ = "queeup"
__url__ = "http://code.google.com/p/queeup/"
__date__ = "29.03.2010"
__version__ = "1.0.5"

# imports
import urllib, sys, os
import xbmcplugin, xbmcgui, xbmc
from resources.lib import theguild

# Append Directories
ROOT_DIR, LIB_DIR = (xbmc.translatePath(os.path.join(os.getcwd(), '')),
                     xbmc.translatePath(os.path.join(os.getcwd(), 'resources', 'lib')))
sys.path.append (ROOT_DIR)
sys.path.append (LIB_DIR)

# Fanart
xbmcplugin.setPluginFanart(int(sys.argv[1]), ROOT_DIR + 'fanart.jpg')

shows = theguild.get_theguild()

class Main:
  def __init__(self):
    if ('action=list' in sys.argv[2]):
      self.list(self.Arguments('name'))
    else:
      self.start()

  def start(self):
    if Debug: self.LOG(description='List available directories.')
    for season in sorted(shows.keys()):
      name = str(season)
      self.addDir(name)
    xbmcplugin.endOfDirectory(int(sys.argv[1]), True)

  def list(self, name):
    self.LOG(description='List available episodes.')
    for video in shows[name]:
      _label = str(video.title)
      _title = str(video.title)
      _description = str(video.description.encode('utf-8'))
      _thumbnail = str(video.thumb_path)
      _url = str(video.video_path)
      _duration = str(video.duration)
      self.addLink(_title, _url, _thumbnail, _description, _duration, _label)
    xbmcplugin.endOfDirectory(int(sys.argv[1]), True)

  def addLink(self, name, url, iconimage, desc, duration, label):
    listitem = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    listitem.setInfo(type="Video",
                     infoLabels={"Title": name,
                                 "Duration": duration,
                                 "Plot": desc,
                                 "Label": label,
                                 'tvshowtitle' : __plugin__, })
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem, False)
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')

  def addDir(self, name):
    listitem = xbmcgui.ListItem(name)
    parameters = '%s?action=list&name=%s' % (sys.argv[0], name)
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), parameters, listitem, True)

  def Arguments(self, arg):
    Arguments = dict(part.split('=') for part in sys.argv[2][1:].split('&'))
    return urllib.unquote_plus(Arguments[arg])

  def LOG(self, plugin=__plugin__, version=__version__, description=''):
    xbmc.log("\t[PLUGIN] '%s: version %s' initialized!\n\t\t '%s'" % \
            (plugin, version, description), xbmc.LOGNOTICE)


if (__name__ == '__main__'):
  Main()
