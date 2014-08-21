# -*- coding: utf-8 -*-

# Debug
Debug = False

# Imports
import re, urllib, urllib2, simplejson, datetime, BeautifulSoup
import xbmc, xbmcgui, xbmcplugin, xbmcaddon

__addon__ = xbmcaddon.Addon(id='plugin.audio.google.listen')
__info__ = __addon__.getAddonInfo
__plugin__ = __info__('name')
__version__ = __info__('version')
__icon__ = __info__('icon')
__fanart__ = __info__('fanart')
__path__ = __info__('path')
__cachedir__ = __info__('profile')
__language__ = __addon__.getLocalizedString
__settings__ = __addon__.getSetting
__set_settings__ = __addon__.setSetting

#SEARCH_URL = 'http://lfe-alpo-gm.appspot.com/search?q=%s&n=100'
SEARCH_URL = 'http://lfe-alpo-gm.appspot.com/search?q=%s&start=%s&n=' + __settings__('perpage')
#POPULAR_URL = 'http://lfe-alpo-gm.appspot.com/popular'
SUBSCRIPTIONS_URL = 'http://www.google.com/reader/public/subscriptions/user/-/label/Listen%20Subscriptions'
SUBSCRIPTIONS_URL_ALL = 'http://www.google.com/reader/api/0/subscription/list?output=json&client=XBMC'
UNREAD_COUNT = 'http://www.google.com/reader/api/0/unread-count?all=true&output=json&client=XBMC'
NEW_ITEMS = 'http://www.google.com/reader/api/0/stream/contents/user/-/label/Listen%20Subscriptions?r=n&xt=user/-/state/com.google/read&refresh=true'
FEED_URL = 'http://www.google.com/reader/api/0/stream/contents/feed/%s?n=%s&client=XBMC'
FEED_URL_MORE = 'http://www.google.com/reader/api/0/stream/contents/%s?n=%s&client=XBMC&c=%s'
TOKEN_URL = 'http://www.google.com/reader/api/0/token'
EDIT_URL = 'http://www.google.com/reader/api/0/subscription/edit?client=XBMC'
AUTH_URL = 'https://www.google.com/accounts/ClientLogin'

class Main:
  def __init__(self):
    if ("action=list" in sys.argv[2]):
      self.LIST()
    elif ("action=search" in sys.argv[2]):
      self.LIST()
    elif ("action=mylist" in sys.argv[2]):
      self.MYLIST()
    elif ("action=add_remove" in sys.argv[2]):
      self.ADD_REMOVE()
    elif ("action=add" in sys.argv[2]):
      self.ADD()
    elif ("action=playall" in sys.argv[2]):
      self.PLAYALL()
    else:
      self.AUTH()
      self.START()

  def START(self):
    if Debug: self.LOG('\nSTART function')
    if __settings__('google') == 'true':
      if Debug: self.LOG('\nGoogle subscription activated!')
      # Get Authorization and store in settings
      self.AUTH()
      Directories = [{'title':'%s - %s' % (__language__(30101), self._COUNTNEW()), 'action':'mylist'},
                     {'title':__language__(30102), 'action':'add'},
                     {'title':__language__(30103), 'action':'search'}]
    else:
      if Debug: self.LOG('\nGoogle subscription inactive!')
      Directories = [{'title':'Search', 'action':'search'}]

    if __settings__('firststart') == 'true':
      self.FIRSTSTART()
    else:
      for i in Directories:
        listitem = xbmcgui.ListItem(i['title'], iconImage='DefaultFolder.png', thumbnailImage=__icon__)
        parameters = '%s?action=%s&title=%s' % (sys.argv[0], i['action'], i['title'])
        xbmcplugin.addDirectoryItems(int(sys.argv[1]), [(parameters, listitem, True)])
      # Sort methods and content type...
      xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_NONE)
      # End of directory...
      xbmcplugin.endOfDirectory(int(sys.argv[1]), True)

  def LIST(self):
    if Debug: self.LOG('\nLIST function')
    if ("action=search" in sys.argv[2]):
      try:
        search_next_page = True
        search_page = int(self.Arguments('search_page', unquote=False)) + int(__settings__('perpage')) + 1
        query = self.Arguments('q', unquote=False)
        URL = SEARCH_URL % (query, str(search_page))
        print URL
      except:
        search_next_page = True
        search_page = 0
        query = self.SEARCH()
        URL = SEARCH_URL % (query, search_page)
        print URL
    if ("action=list" in sys.argv[2]):
      try:
        URL = FEED_URL % (self.Arguments('url', unquote=False), __settings__('perpage'))
      except:
        URL = FEED_URL_MORE % (self.Arguments('id', unquote=False), __settings__('perpage'), self.Arguments('page'))
    json = simplejson.loads(urllib.urlopen(URL).read())
    try:
      next_page = json['continuation']
      id = json['id']
    except:
      next_page = False
    for entry in json['items']:
      infoLabels = {}

      title = infoLabels['title'] = entry['title']
      try: infoLabels['plotoutline'] = entry['subtitle']
      except: infoLabels['plotoutline'] = ''
      try:
        try: infoLabels['plot'] = entry['summary']
        except: infoLabels['plot'] = entry['summary'][0]['content']
      except: infoLabels['plot'] = ''
      try:
        try: feedurl = entry['feed_url']
        except: feedurl = entry['origin'][0]['htmlurl']
      except: feedurl = ''
      print feedurl
      try:
        try: url = entry['enclosure_href']
        except: url = entry['enclosure'][0]['href']
      except: url = ''
      try: thumb = entry['image_href']
      except: thumb = __icon__
      try: infoLabels['author'] = entry['author']
      except: infoLabels['author'] = ''
      try: infoLabels['duration'] = str(entry['duration'])
      except: infoLabels['duration'] = str('')
      try:
        try: infoLabels['date'] = entry['date']
        except: infoLabels['date'] = datetime.datetime.fromtimestamp(int(entry['crawlTimeMsec']) / 1000).strftime('%d.%m.%Y')
      except: infoLabels['date'] = ''
      try:
        try: infoLabels['size'] = int(entry['enclosure_length'])
        except: infoLabels['size'] = int(entry['enclosure'][0]['length'])
      except: infoLabels['size'] = ''

      listitem = xbmcgui.ListItem(title, iconImage='DefaultVideo.png', thumbnailImage=thumb)
      listitem.setInfo(type='video', infoLabels=infoLabels)
      listitem.setProperty('IsPlayable', 'true')
      contextmenu = [(__language__(30303), 'XBMC.RunPlugin(%s?action=list&url=%s)' % (sys.argv[0], urllib.quote_plus(FEED_URL % (feedurl, __settings__('perpage')))))]
      if __settings__('google') == 'true':
        contextmenu += [(__language__(30301), 'XBMC.RunPlugin(%s?action=add_remove&url=%s&ac=%s)' % (sys.argv[0], urllib.quote_plus(feedurl), 'subscribe'))]
      # Play All context menu
      contextmenu += [(__language__(30304), 'XBMC.RunPlugin(%s?action=playall&url=%s)' % (sys.argv[0], urllib.quote_plus(URL)))]
      listitem.addContextMenuItems(contextmenu, replaceItems=False)
      xbmcplugin.addDirectoryItems(int(sys.argv[1]), [(url, listitem, False)])
    if next_page:
      listitem = xbmcgui.ListItem(__language__(30104), iconImage='DefaultVideo.png', thumbnailImage=__icon__)
      parameters = '%s?action=list&id=%s&page=%s' % (sys.argv[0], urllib.quote_plus(id), next_page)
      xbmcplugin.addDirectoryItem(int(sys.argv[1]), parameters, listitem, True)
    ## Google Listen api not allowedmore than >20. so it's not usefull.
    #if search_next_page:
    #  listitem = xbmcgui.ListItem(__language__(30104), iconImage='DefaultVideo.png', thumbnailImage=__icon__)
    #  parameters = '%s?action=search&q=%s&search_page=%s' % (sys.argv[0], query, str(search_page))
    #  xbmcplugin.addDirectoryItem(int(sys.argv[1]), parameters, listitem, True)
    # Sort methods and content type...
    #print '%s?playall_url=%s' % (sys.argv[0], playallitems)
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_TITLE)
    if infoLabels['date']:
      xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)
    if infoLabels['duration']:
      xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)
    if infoLabels['size']:
      xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_SIZE)
    # End of directory...
    xbmcplugin.endOfDirectory(int(sys.argv[1]), True)
    # for playall

  def MYLIST(self):
    request = urllib2.Request(SUBSCRIPTIONS_URL)
    #request.add_data(urllib.urlencode(query_args))
    request.add_header('Authorization', 'GoogleLogin auth=%s' % __settings__('auth'))
    BeautifulSoup.BeautifulStoneSoup.NESTABLE_TAGS['outline'] = []
    soup = BeautifulSoup.BeautifulSOAP(urllib2.urlopen(request).read())
    for entry in soup.body.outline.findAll('outline'):
      title = entry['title']
      url = entry['xmlurl']
      thumb = 'http://lfe-alpo-gm.appspot.com/img?url=' + entry['xmlurl']
      listitem = xbmcgui.ListItem(title, iconImage='DefaultFolder.png', thumbnailImage=thumb)
      contextmenu = [(__language__(30302), 'XBMC.RunPlugin(%s?action=add_remove&url=%s&ac=%s)' % (sys.argv[0], urllib.quote_plus(entry['xmlurl']), 'unsubscribe'))]
      listitem.addContextMenuItems(contextmenu, replaceItems=True)
      parameters = '%s?action=list&url=%s' % (sys.argv[0], urllib.quote_plus(url))
      xbmcplugin.addDirectoryItems(int(sys.argv[1]), [(parameters, listitem, True)])
    # Sort methods and content type...
    xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_NONE)
    # End of directory...
    xbmcplugin.endOfDirectory(int(sys.argv[1]), True)

  def AUTH(self):
    if Debug: self.LOG('\nAUTH function')
    url = urllib2.Request(AUTH_URL)
    url.add_header('Content-Type', 'application/x-www-form-urlencoded')
    url.add_header('GData-Version', 2)
    data = urllib.urlencode({'Email': str(__settings__('gUser')),
                             'Passwd': str(__settings__('gPass')),
                             'service': 'reader',
                             'source': 'XBMC'})
    try:
      con = urllib2.urlopen(url, data)
      value = con.read()
      con.close()
      #print value
      result = re.compile('Auth=(.*)').findall(value)
      __set_settings__('auth', result[0])
      return result[0]
    except:
      if Debug: self.LOG('\nAuthorization error!')
      xbmc.executebuiltin('XBMC.Notification("%s", "%s")' % ('Google Listen', 'Authorization error!'))

  def TOKEN(self):
    if Debug: self.LOG('\nTOKEN function')
    request = urllib2.Request(TOKEN_URL)
    request.add_header('Authorization', 'GoogleLogin auth=%s' % __settings__('auth'))
    try:
      con = urllib2.urlopen(request)
      result = con.read()
      con.close()
      return result
    except:
      if Debug: self.LOG('\nTOKEN error!')
      xbmc.executebuiltin('XBMC.Notification("%s", "%s")' % ('Google Listen', 'Token error!'))

  def ADD_REMOVE(self, feed='', ac=''):
    if Debug: self.LOG('\nADD_REMOVE function')
    if feed == '':
      feed = self.Arguments('url')
    if ac == '':
      ac = self.Arguments('ac')
    #POST to add: s=$streams&t=$title&T=$token&ac=subscribe
    #POST to remove: s=$stream&T=$token&ac=unsubscribe
    #ADD = 'http://www.google.com/reader/api/0/subscription/quickadd?client=listen'
    query_args = {'a':'user/-/label/Listen Subscriptions',
                  's':'feed/' + feed,
                  'T':self.TOKEN(),
                  'ac':ac,
                  }
    request = urllib2.Request(EDIT_URL)
    request.add_data(urllib.urlencode(query_args))
    request.add_header('Authorization', 'GoogleLogin auth=%s' % __settings__('auth'))

    if urllib2.urlopen(request).read() == 'OK':
      if Debug: self.LOG('\n%s success' % ac)
      xbmc.executebuiltin('XBMC.Notification("%s", "%s")' % (__language__(30000), '%s success' % ac))
      self.MYLIST()
    else:
      if Debug: self.LOG('\nError while %s' % ac)
      xbmc.executebuiltin('XBMC.Notification("%s", "%s")' % (__language__(30000), 'Error whlie %s' % ac))

  def SEARCH(self):
    if Debug: self.LOG('\nSEARCH function')
    kb = xbmc.Keyboard()
    kb.setHeading(__language__(30403))
    kb.doModal()
    if (kb.isConfirmed()):
      text = kb.getText()
      return re.sub(' ', '+', text)
    else:
      self.START()

  def ADD(self):
    if Debug: self.LOG('\nADD function')
    kb = xbmc.Keyboard()
    kb.setHeading(__language__(30404))
    kb.setDefault('http://')
    kb.doModal()
    if (kb.isConfirmed()):
      url = kb.getText()
      self.ADD_REMOVE(feed=url, ac='subscribe')
    else:
      self.START()

  def _COUNTNEW(self):
    request = urllib2.Request(NEW_ITEMS)
    request.add_header('Authorization', 'GoogleLogin auth=%s' % __settings__('auth'))
    json = simplejson.loads(urllib2.urlopen(request).read())
    if len(json['items']) > 0:
      return '%s' % (__language__(30105) % str(len(json['items'])))
    else:
      return '%s' % __language__(30106)

  def PLAYALL(self):
    if Debug: self.LOG('\nPLAYALL function')
    # Create Playlist video...
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    json = simplejson.loads(urllib.urlopen(self.Arguments('url')).read())
    for entry in json['items']:
      title = entry['title']
      try:
        try: url = entry['enclosure_href']
        except: url = entry['enclosure'][0]['href']
      except: url = ''
      # add item to our playlist
      listitem = xbmcgui.ListItem(title, iconImage="DefaultVideo.png", thumbnailImage=__icon__)
      playlist.add(url, listitem)
    # Play video...
    xbmcPlayer = xbmc.Player()
    xbmcPlayer.play(playlist)

  def FIRSTSTART(self):
    dialog = xbmcgui.Dialog()
    ret = dialog.yesno(__language__(30000),
                       __language__(30401),
                       __language__(30402))
    if ret:
      __addon__.openSettings()
      __set_settings__('firststart', 'false')
      self.START()
    else:
      __set_settings__('firststart', 'false')
      self.START()

  def Arguments(self, arg, unquote=True):
    Arguments = dict(part.split('=') for part in sys.argv[2][1:].split('&'))
    if unquote:
      return urllib.unquote_plus(Arguments[arg])
    else:
      return Arguments[arg]

  def LOG(self, description):
    xbmc.log("[ADD-ON] '%s v%s': '%s'" % (__plugin__, __version__, description), xbmc.LOGNOTICE)

if __name__ == '__main__':
  Main()
