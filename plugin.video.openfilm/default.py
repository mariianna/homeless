# -*- coding: utf-8 -*-

# Debug
Debug = False

# Imports
import sys, urllib
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from BeautifulSoup import SoupStrainer, BeautifulSoup as BS

__addon__ = xbmcaddon.Addon(id='plugin.video.openfilm')
__info__ = __addon__.getAddonInfo
__plugin__ = __info__('name')
__version__ = __info__('version')
__icon__ = __info__('icon')

URL = 'http://www.openfilm.com'
RSS_URL = 'rss://www.openfilm.com/mrss/boxee/?&v=1&a=1'

# Main
class Main:
  def __init__(self):
    if ("action=categories" in sys.argv[2]):
      self.CATEGORIES()
    elif ("action=sort" in sys.argv[2]):
      self.GET_SORT()
    else:
      self.START()

  def START(self):
    if Debug: self.LOG('START')
    folders = [{'title':"Editor's Picks", 'url':'rss://www.openfilm.com/mrss/boxee/?pid=1&s=-6'},
               {'title':'Most Popular', 'url':'rss://www.openfilm.com/mrss/boxee/?s=1'},
               {'title':'Most Recent', 'url':'rss://www.openfilm.com/mrss/boxee/?s=3'},
               {'title':'Categories', 'url':'%s?action=categories' % sys.argv[0]},
               ]
    for i in folders:
      self.addDirectoryItem(i['title'], i['url'])
    xbmcplugin.endOfDirectory(int(sys.argv[1]), True)

  def CATEGORIES(self):
    if Debug: self.LOG('CATEGORIES')
    html = urllib.urlopen(URL).read()
    soup = BS(html, parseOnlyThese=SoupStrainer('ul', {'id':'header_main_menu'}))
    for a in soup.li.div.ul.findAll('a'):
      title = a.string.replace('&amp;', '&')
      link = URL + a['href']
      parameters = '%s?action=sort&url=%s' % (sys.argv[0], urllib.quote_plus(link))
      self.addDirectoryItem(title, parameters)
    xbmcplugin.endOfDirectory(int(sys.argv[1]), True)

  def GET_SORT(self):
    if Debug: self.LOG('GET_SORT')
    html = urllib.urlopen(self.Arguments('url')).read()
    soup = BS(html, parseOnlyThese=SoupStrainer('ul', {'class':'sortingMenu sortBlock'}))
    for li in soup('li'):
      title = li.a.string
      link = RSS_URL + li.a['href'].split('?')[1].replace('&amp;', '&')
      self.addDirectoryItem(title, link)
    xbmcplugin.endOfDirectory(int(sys.argv[1]), True)

  def addDirectoryItem(self, title, link):
    listitem = xbmcgui.ListItem(title, thumbnailImage=__icon__)
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), link, listitem, True)

  def Arguments(self, arg):
    Arguments = dict(part.split('=') for part in sys.argv[2][1:].split('&'))
    return urllib.unquote_plus(Arguments[arg])

  def LOG(self, description):
    xbmc.log("[ADD-ON] '%s v%s': '%s'" % (__plugin__, __version__, description), xbmc.LOGNOTICE)

if __name__ == '__main__':
  Main()
