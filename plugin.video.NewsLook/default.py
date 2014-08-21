# -*- coding: utf-8 -*-

# Debug
Debug = False

# Imports
import os, sys, urllib, simplejson, time
import xbmc, xbmcgui, xbmcplugin, xbmcaddon

__addon__ = xbmcaddon.Addon(id='plugin.video.newslook')
__info__ = __addon__.getAddonInfo
__plugin__ = __info__('name')
__version__ = __info__('version')
__icon__ = __info__('icon')
__language__ = __addon__.getLocalizedString

URL = 'http://iptv.newslook.com/api/v2/categories/%s.json'

class Main:
  def __init__(self):
    if ("action=list" in sys.argv[2]):
      self.LIST(self.Arguments('url'))
    else:
      self.START()

  def START(self):
    if Debug: self.LOG('START()')
    Main = [{'title':__language__(30201), 'url':URL % 'top-news'},
            {'title':__language__(30202), 'url':URL % 'world'},
            {'title':__language__(30203), 'url':URL % 'u-s-news'},
            {'title':__language__(30204), 'url':URL % 'finance'},
            {'title':__language__(30205), 'url':URL % 'science'},
            {'title':__language__(30206), 'url':URL % 'technology'},
            {'title':__language__(30207), 'url':URL % 'health-medicine'},
            {'title':__language__(30208), 'url':URL % 'artsculture'},
            {'title':__language__(30209), 'url':URL % 'lifestyle'},
            ]
    for i in Main:
      listitem = xbmcgui.ListItem(i['title'], iconImage='DefaultFolder.png', thumbnailImage=__icon__)
      url = '%s?action=list&url=%s' % (sys.argv[0], urllib.quote_plus(i['url']))
      xbmcplugin.addDirectoryItems(int(sys.argv[1]), [(url, listitem, True)])
    # Sort methods and content type...
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE)
    # End of directory...
    xbmcplugin.endOfDirectory(int(sys.argv[ 1 ]), True)

  def LIST(self, url):
    if Debug: self.LOG('LIST()')
    json = simplejson.loads(urllib.urlopen(url).read())
    for entry in json['videos']:
      id = entry['id']
      title = entry['title']
      description = entry['description']
      _duration = entry['duration']
      if _duration >= 3600 * 1000:
          duration = time.strftime('%H:%M:%S', time.gmtime(_duration / 1000))
      else:
        duration = time.strftime('%M:%S', time.gmtime(_duration / 1000))
      video = entry['cdn_asset_url']
      channel = entry['channel_name']
      thumbnail_version = entry['thumbnail_version']
      thumbnail = 'http://img1.newslook.com/images/dyn/videos/%s/%s/pad/324/231/%s.jpg' % (id, thumbnail_version, id)

      listitem = xbmcgui.ListItem(title, iconImage='DefaultVideo.png', thumbnailImage=thumbnail)
      listitem.setProperty('IsPlayable', 'true')
      listitem.setProperty('mimetype', 'video/mp4')
      listitem.setInfo(type='video',
                       infoLabels={'title' : title,
                                   'plot' : description,
                                   'duration': duration,
                                   })
      xbmcplugin.addDirectoryItems(int(sys.argv[1]), [(video, listitem, False)])
    # Content Type
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    # Sort methods
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE, label2Mask='%D')
    # End of directory...
    xbmcplugin.endOfDirectory(int(sys.argv[1]), True)

  def Arguments(self, arg):
    Arguments = dict(part.split('=') for part in sys.argv[2][1:].split('&'))
    return urllib.unquote_plus(Arguments[arg])

  def LOG(self, description):
    xbmc.log("[ADD-ON] '%s v%s': DEBUG: %s" % (__plugin__, __version__, description), xbmc.LOGNOTICE)

if __name__ == '__main__':
  Main()