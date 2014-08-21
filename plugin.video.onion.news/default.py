'''
    jerryseinfeld.com XBMC Plugin
    Copyright (C) 2011 t0mm0

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import re
import urllib2
import xbmcgui, xbmcplugin

plugin_handle = int(sys.argv[1])

def add_video_item(url, infolabels, img=''):
    listitem = xbmcgui.ListItem(infolabels['title'], iconImage=img, 
                                thumbnailImage=img)
    listitem.setInfo('video', infolabels)
    listitem.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(plugin_handle, url, listitem, isFolder=False)
                                

# base_url = 'http://cdn.jerryseinfeld.com/assets'
html = urllib2.urlopen('http://www.theonion.com/feeds/onn/').read()
for v in re.finditer('file=(http.+?.mp4)|<title>(.+?)<\/title>|<pubDate>(.+?)<\/pubDate>', html):
    filename, title, date = v.groups()
    if filename:
       s1 = filename
    if title:
       s2 = title
    if date:
       y = date.split(" ")[3]
       if date.split(" ")[2] == 'Jan':
          m = "01"
       if date.split(" ")[2] == 'Feb':
          m = "02"
       if date.split(" ")[2] == 'Mar':
          m = "03"
       if date.split(" ")[2] == 'Apr':
          m = "04"
       if date.split(" ")[2] == 'May':
          m = "05"
       if date.split(" ")[2] == 'Jun':
          m = "06"
       if date.split(" ")[2] == 'Jul':
          m = "07"
       if date.split(" ")[2] == 'Aug':
          m = "08"
       if date.split(" ")[2] == 'Sep':
          m = "09"
       if date.split(" ")[2] == 'Oct':
          m = "10"
       if date.split(" ")[2] == 'Nov':
          m = "11"
       if date.split(" ")[2] == 'Dec':
          m = "12"
       d = date.split(" ")[1]
#       print "s1 = ", s1, " s2 = ", s2, " date = ", date, " y = ", y, " m = ", m, " d = ", d
#       add_video_item('%s' % (s1), {'title': '%s (%s)' % (s2, date), 'aired': '%s-%s-%s' % y, m, d}, 'http://o.onionstatic.com/img/onn/podcast_300300.jpg')  # for some reason it crashes on this line so i stubbed in the random date below.
       add_video_item('%s' % (s1), {'title': '%s (%s)' % (s2, date), 'aired': '11-11-2010'}, 'http://o.onionstatic.com/img/onn/podcast_300300.jpg')


xbmcplugin.endOfDirectory(plugin_handle)      

