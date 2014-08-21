#############################################################################
#
# Navi-X Playlist browser
# v2.7 by rodejo (rodejo16@gmail.com)
#
# -v1.01  (2007/04/01) first release
# -v1.2   (2007/05/10)
# -v1.21  (2007/05/20)
# -v1.22  (2007/05/26)
# -v1.3   (2007/06/15)
# -v1.31  (2007/06/30)
# -v1.4   (2007/07/04)
# -v1.4.1 (2007/07/21)
# -v1.5   (2007/09/14)
# -v1.5.1 (2007/09/17)
# -v1.5.2 (2007/09/22)
# -v1.6   (2007/09/29)
# -v1.6.1 (2007/10/19)
# -v1.7 beta (2007/11/14)
# -v1.7   (2007/11/xx)
# -v1.7.1 (2007/12/15)
# -v1.7.2 (2007/12/20)
# -v1.8 (2007/12/31)
# -v1.9 (2008/02/10)
# -v1.9.1 (2008/02/10)
# -v1.9.2 (2008/02/23)
# -v1.9.3 (2008/06/20)
# -v2.0   (2008/07/21)
# -v2.1   (2008/08/08)
# -v2.2   (2008/08/31)
# -v2.3   (2008/10/18)
# -v2.4   (2008/12/04)
# -v2.5   (2009/01/24)
# -v2.6   (2009/03/21)
# -v2.7   (2009/04/11)
# -v2.7   (2009/05/01) - Plugin release
#
# Changelog (v2.7)
# -First release Navi-X plugin version
#
# Changelog (v2.7)
# -Added new playlist item called 'processor'. Points to a playlist item processing server.
# -Youtube fix
# -Added PLX playlist multiline comment tag (""").
#
# Changelog (v2.6)
# -Added parental control.
# -Update Apple movie trailer. List shows new releases.
# -Solved problem with download + shutdown
#
# Changelog (v2.5)
# -Solved a problem in the script/plugin installer.
# -Added release date attribute for playlist item.
# -Improved thumb image loader (separate thread).
# -background downloading support.
# -Solved minor problems.
#
# Changelog (v2.4)
# -improved Shoutcast playlist loading.
# -improved PLX loading. Support both LF and CRLF.
# -Support new media type called 'plugin'. (plugin file needs to be a ZIP file).
# -Support description= field for every media item in PLX file.
# -Youtube fix.
#
# Changelog (v2.3)
# -Added new playlist "description=" element.
# -Youtube parser added playlist support.
# -Youtube parser fix.
# -Youtube long video name display.
# -Improved caching for a better user experience.
# -Apple movie trailer parser fix.
# -Other minor improvements.
#
# Changelog (v2.2)
# -Improved RSS reader to support image elements in XML file.
# -Y-button starts image slide show.
# -Youtube: Minor bug fixed HTML parser.
# -Apple movie trailers: Changed the sorting order to "release date".
# -Stability improvements.
#
# Changelog (v2.1)
# -Added a new type called 'download'. This type can be used to download
#  any type of file from a webserver to the XBOX (e.g a plugin rar file).
# -Improved text viewer: Added setting of text viewer background image
# -Improved RSS parser. Fix some problems and added thumb images.
# -Improved Youtube: Next page is now added to the existing page.
# -Minor problems solved.
# 
# Changelog (v2.0)
# - Youtube: Switched to high resolution mode. Also downloaded possible.
# - Added search history. Remembers last searches.
# - Updated context menu options (Play... and View...).
# - Added view mode option in menu: Ascencding/Descencing
# - Play using menu accessible via Y-button.
# - New playlist option called 'playmode. Example: 
#   playmode=autonext #plays all entries in playlist
#
#############################################################################

from string import *
import sys, os.path
import urllib
import re, random, string
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import re, os, time, datetime, traceback
import shutil
import zipfile
import copy
#import threading

sys.path.append(os.path.join(xbmcaddon.Addon(id='plugin.video.navi-x').getAddonInfo('path').replace(";",""),'src'))
from libs2 import *
from settings import *
from CPlayList import *
from CFileLoader import *
#from CDownLoader import *
from CPlayer import *
#from CDialogBrowse import *
from CTextView import *
from CInstaller import *
#from skin import *
#from CBackgroundLoader import *

try: Emulating = xbmcgui.Emulating
except: Emulating = False

#####################################################################
# Description: 
######################################################################
def Init():

#    delFiles(cacheDir) #clear the cache first

    #Create default DIRs if not existing.
    if not os.path.exists(cacheDir):
        os.mkdir(os.path.dirname(str(cacheDir)))
    if not os.path.exists(imageCacheDir): 
        os.mkdir(os.path.dirname(str(imageCacheDir)))
    
    if not os.path.exists(myDownloadsDir): 
        os.mkdir(os.path.dirname(str(myDownloadsDir)))
 
######################################################################
# Description: Parse playlist file. Playlist file can be a:
#              -PLX file;
#              -RSS v2.0 file (e.g. podcasts);
#              -RSS daily Flick file (XML1.0);
#              -html Youtube file;
# Parameters : URL (optional) =URL of the playlist file.
#              mediaitem (optional)=Playlist mediaitem containing 
#              playlist info. Replaces URL parameter.
#              start_index (optional) = cursor position after loading 
#              playlist.
#              reload (optional)= indicates if the playlist shall be 
#              reloaded or only displayed.
# Return     : 0 on success, -1 if failed.
######################################################################
def ParsePlaylist(mediaitem=CMediaItem() , proxy="CACHING"):
    playlist = CPlayList()  
   
    type=mediaitem.type
    URL=''

    #load the playlist
    if type == 'rss_flickr_daily':
        result = playlist.load_rss_flickr_daily(URL, mediaitem, proxy)
    elif type[0:3] == 'rss':
        result = playlist.load_rss_20(URL, mediaitem, proxy)
    elif type == 'html_youtube':
        result = playlist.load_html_youtube(URL, mediaitem, proxy)
    elif type == 'xml_shoutcast':
        result = playlist.load_xml_shoutcast(URL, mediaitem, proxy)
    elif type == 'xml_applemovie':
        result = playlist.load_xml_applemovie(URL, mediaitem, proxy)
    elif type == 'directory':
        result = playlist.load_dir(URL, mediaitem, proxy)
    else: #assume playlist file
        result = playlist.load_plx(URL, mediaitem, proxy)
            
    if result == -1: #error
        dialog = xbmcgui.Dialog()
        dialog.ok("Error", "This playlist requires a newer Navi-X version")
    elif result == -2: #error
        dialog = xbmcgui.Dialog()
        dialog.ok("Error", "The requested file could not be opened.")
                
    if result != 0: #failure
        return -1
            
    #succesful
    playlist.save(RootDir + 'source.plx')
                   
    today=datetime.date.today()
    #fill the main list
    
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE)
    #xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    
    for m in playlist.list:
        if m.thumb != 'default':
            thumb = m.thumb            
##            loader = CFileLoader2()
##            ext = getFileExtension(m.thumb)
##            loader.load(m.thumb, cacheDir + "thumb." + ext, timeout=1, proxy="ENABLED", content_type='image')
##            if loader.state == 0:
##                thumb = loader.localfile
##            else:
##                thumb = getPlEntryThumb(m.type) 
        else:
            thumb = getPlEntryThumb(m.type)

        label2 = ''
        if m.date != '':
            l=m.date.split('-')
            entry_date = datetime.date(int(l[0]), int(l[1]), int(l[2]))
            days_past = (today-entry_date).days
            if days_past <= 10:
                if days_past <= 0:
                    label2 = '          NEW today'
                elif days_past == 1:
                    label2 = '          NEW yesterday'
                else:
                    label2 = '          NEW ('+ str(days_past) + ' days ago)'
                        
        folder=False
        if (m.type == 'playlist') or (m.type == 'rss') or\
           (m.type == 'rss_flickr_daily') or (m.type == 'html_youtube') or \
           (m.type == 'xml_applemovie') or (m.type == 'directory') or \
           (m.type == 'xml_shoutcast') or (m.type == 'search_shoutcast') or \
           (m.type == 'search_youtube') or (m.type == 'search'):
            folder = True
            
        desc=''
        if m.description:
            desc=m.description
        
        item = xbmcgui.ListItem(urllib.unquote_plus(unicode(urllib.quote_plus(m.name+label2), "utf-8" )), iconImage=thumb, thumbnailImage=thumb)
        item.setInfo( type=m.type, infoLabels={ "Title": m.name , "Plot": desc } )


        URL = sys.argv[0] + "?mode=0&name=" + urllib.quote_plus(m.name) + \
                             "&type=" + urllib.quote_plus(m.type) + \
                             "&url=" + urllib.quote_plus(m.URL) + \
                             "&processor=" + urllib.quote_plus(m.processor) + \
                             "&date=" + urllib.quote_plus(m.date)                           
                       
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), URL, item, folder, playlist.size())                            
           
        #addSortMethod
        #xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_PLAYLIST_ORDER)
      
    return 0 #success

######################################################################
# Description: Gets the playlist entry thumb image for different types
# Parameters : type = playlist entry type
# Return     : thumb image (local) file name
######################################################################
def getPlEntryThumb(type):
    if type == 'playlist':
        return ''
    elif type == 'rss_flickr_daily':
        return imageDir+'icon_rss.png'
    elif type == 'xml_applemovie':
        return ''#imageDir+'icon_playlist.png'
    elif type == 'html_youtube':
        return ''#imageDir+'icon_playlist.png'
    elif type == 'search_youtube':
        return imageDir+'icon_search.png'
    elif type == 'xml_shoutcast':
        return ''#imageDir+'icon_playlist.png'
    elif type == 'search_shoutcast':
        return imageDir+'icon_search.png'
    elif type == 'directory':
        return ''#imageDir+'icon_playlist.png'
    elif type == 'window':
        return ''#imageDir+'icon_playlist.png'
    elif type[0:6] == 'script':
        return imageDir+'icon_script.png'               
    elif type[0:6] == 'plugin':
        return imageDir+'icon_script.png'
            
    return imageDir+'icon_'+str(type)+'.png'
    
    
######################################################################
# Description: Handles the selection of an item in the list.
# Parameters : playlist(optional)=the source playlist;
#              pos(optional)=media item position in the playlist;
#              append(optional)=true is playlist must be added to 
#              history list;
#              URL(optional)=link to media file;
# Return     : -
######################################################################
def SelectItem(mediaitem=CMediaItem()):
    type = mediaitem.type
    if type == 'playlist' or type == 'favorite' or type[0:3] == 'rss' or \
       type == 'rss_flickr_daily' or type == 'directory' or \
       type == 'html_youtube' or type == 'xml_shoutcast' or \
       type == 'xml_applemovie':
                if 'special://' in mediaitem.URL:
                        mediaitem.URL = xbmc.translatePath(mediaitem.URL)
                result = ParsePlaylist(mediaitem)             

    elif type == 'video' or type == 'audio' or type == 'html':
#these lines are used for debugging only
#                self.onDownload()
#                self.state_busy = 0
#                self.selectBoxMainList()
#                self.state_busy = 0                
#                return
                
#       if (playlist != 0) and (playlist.playmode == 'autonext'):
#            size = playlist.size()
#            if playlist.player == 'mplayer':
#                MyPlayer = CPlayer(xbmc.PLAYER_CORE_MPLAYER, function=myPlayerChanged)
#            elif playlist.player == 'dvdplayer':
#                MyPlayer = CPlayer(xbmc.PLAYER_CORE_DVDPLAYER, function=myPlayerChanged)
#            else:
#                MyPlayer = CPlayer(xbmc.PLAYER_CORE_AUTO, function=.myPlayerChanged)                
#            result = MyPlayer.play(playlist, pos, size-1)
#        else:
        if(True):
#            xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).play(mediaitem.URL)
#            if mediaitem.player == 'mplayer':
#                MyPlayer = CPlayer(xbmc.PLAYER_CORE_MPLAYER, function=myPlayerChanged)
#            elif mediaitem.player == 'dvdplayer':
#                MyPlayer = CPlayer(xbmc.PLAYER_CORE_DVDPLAYER, function=myPlayerChanged)
#            else:
                MyPlayer = CPlayer(xbmc.PLAYER_CORE_AUTO, function=myPlayerChanged)
                result = MyPlayer.play_URL(mediaitem.URL, mediaitem)      
#            dialog.close()   
            
                if result != 0:
                    dialog = xbmcgui.Dialog()
                    dialog.ok("Error", "Could not open file.")
                
    elif type == 'image':
        viewImage(mediaitem.URL) #single file show
    elif type == 'text':
        OpenTextFile(mediaitem=mediaitem)
    elif type == 'window':
        xbmc.executebuiltin("xbmc.ActivateWindow(" + mediaitem.URL + ",Root)")             
    elif type[0:6] == 'script' or type[0:6] == 'plugin':
        InstallApp(mediaitem=mediaitem)
#            elif type == 'download':
#                self.onDownload()
    elif (type[0:6] == 'search'):
        PlaylistSearch(mediaitem, True)
    else:
        dialog = xbmcgui.Dialog()
        dialog.ok("Playlist format error", '"' + type + '"' + " is not a valid type.")
#    

######################################################################
# Description: Player changed info can be catched here
# Parameters : action=user key action
# Return     : -
######################################################################
def myPlayerChanged(state):
    #At this moment nothing to handle.
    pass


######################################################################
# Description: Handles display of a text file.
# Parameters : URL=URL to the text file.
# Return     : -
######################################################################
def OpenTextFile(URL='', mediaitem=CMediaItem()):
    #if (mediaitem.background == 'default') and (self.pl_focus.background != 'default'):
    #    mediaitem = copy.copy(mediaitem)
    #    mediaitem.background = self.pl_focus.background

#    pass
                    
    textwnd = CTextView()
    result = textwnd.OpenDocument(URL, mediaitem)
#    setInfoText(visible=0) #loading text off            

    if result == 0:
        textwnd.doModal()
        #textwnd.show()
    else:
        dialog = xbmcgui.Dialog()
        dialog.ok("Error", "Could not open file.")
    
######################################################################
# Description: Handles image slideshow.
# Parameters : playlist=the source playlist
#              pos=media item position in the playlist
#              mode=view mode (0=slideshow, 1=recursive slideshow)
#              URL(optional) = URL to image
# Return     : -
######################################################################
def viewImage(iURL=''):
    mode = 0
#    self.setInfoText("Loading...")
    #clear the imageview cache
#    self.delFiles(imageCacheDir)

    if not os.path.exists(imageCacheDir): 
        os.mkdir(imageCacheDir) 

    if mode == 0: #single file show
        localfile= imageCacheDir + '0.'
        if iURL != '':
            URL = iURL
#        else:    
#            URL = playlist.list[pos].URL
        ext = getFileExtension(URL)

        if URL[:4] == 'http':
            loader = CFileLoader()
            loader.load(URL, localfile + ext, proxy="DISABLED")
            if loader.state == 0:
                xbmc.executebuiltin('xbmc.slideshow(' + imageCacheDir + ')')
            else:
                dialog = xbmcgui.Dialog()
                dialog.ok("Error", "Unable to open image.")
        else:
            #local file
            shutil.copyfile(URL, localfile + ext)
            xbmc.executebuiltin('xbmc.slideshow(' + imageCacheDir + ')')
            
#    elif mode == 1: #recursive slideshow
#        #in case of slideshow store default image
#        count=0
#        for i in range(self.list.size()):
#            if playlist.list[i].type == 'image':
#                localfile=imageCacheDir+'%d.'%(count)
#                URL = playlist.list[i].URL
#                ext = getFileExtension(URL)
#                shutil.copyfile(imageDir+'imageview.png', localfile + ext)
#                count = count + 1
#        if count > 0:
#            count = 0
#            index = pos
#            for i in range(self.list.size()):
#                if count == 2:
#                    xbmc.executebuiltin('xbmc.recursiveslideshow(' + imageCacheDir + ')')
#                    self.state_action = 0
#                elif (count > 2) and (self.state_action == 1):
#                    break
#                            
#                if playlist.list[index].type == 'image':
#                    localfile=imageCacheDir+'%d.'%(count)
#                    URL = playlist.list[index].URL
#                    ext = getFileExtension(URL)
#                    self.loader.load(URL, localfile + ext, proxy="DISABLED")
#                    if self.loader.state == 0:
#                        count = count + 1
#                index = (index + 1) % self.list.size()
#
#            if self.list.size() < 3:
#                #start the slideshow after the first two files. load the remaining files
#                #in the background
#                xbmc.executebuiltin('xbmc.recursiveslideshow(' + imageCacheDir + ')')
#        if count == 0:
#            dialog = xbmcgui.Dialog()
#            dialog.ok("Error", "No images in playlist.")
            
#    self.setInfoText(visible=0)
                
######################################################################
# Description: Handles Installation of Applications
# Parameters : URL=URL to the script ZIP file.
# Return     : -
######################################################################
def InstallApp(URL='', mediaitem=CMediaItem()):
    dialog = xbmcgui.Dialog()
    if mediaitem.type[0:6] == 'script':
        index=mediaitem.type.find(":")
        if index != -1:
            type = mediaitem.type[index+1:]
        else:
            type = ''
        if dialog.yesno("Message", "Install Script?") == False:
            return
        SetInfoText("Installing...")
        installer = CInstaller()
        result = installer.InstallScript(URL, mediaitem)

    elif mediaitem.type[0:6] == 'plugin':
        index=mediaitem.type.find(":")
        if index != -1:
            type = mediaitem.type[index+1:] + " "
        else:
            type = ''
        if dialog.yesno("Message", "Install " + type + "Plugin?") == False:
            return
        SetInfoText("Installing...")
        installer = CInstaller()
        result = installer.InstallPlugin(URL, mediaitem)
    else:
        result = -1 #failure
            
    SetInfoText("")
            
    if result == 0:
        dialog.ok(" Installer", "Installation successful.")
        if type == 'navi-x':
            dialog.ok(" Installer", "Please restart Navi-X.")
    elif result == -1:
        dialog.ok(" Installer", "Installation aborted.")
    elif result == -3:
        dialog.ok(" Installer", "Invalid ZIP file.")
    else:
        dialog.ok(" Installer", "Installation failed.")                
             
######################################################################
# Description: Handle selection of playlist search item (e.g. Youtube)
# Parameters : item=CMediaItem
#              append(optional)=true is playlist must be added to 
#              history list;
# Return     : -
######################################################################
def PlaylistSearch(item, append):
#    possibleChoices = []
#    possibleChoices.append("New Search")
    #for m in self.SearchHistory:
    #    possibleChoices.append(m)
#    possibleChoices.append("Cancel")                
#    dialog = xbmcgui.Dialog()
#    choice = dialog.select("Search", possibleChoices)

#    if (choice == -1) or (choice == (len(possibleChoices)-1)):
#        return #canceled

    #if choice > 0:
    #    string = self.SearchHistory[choice-1]
    #else:  #New search
    string = ''
            
    keyboard = xbmc.Keyboard(string, 'Search')
    keyboard.doModal()
    if (keyboard.isConfirmed() == False):
        return #canceled
    searchstring = keyboard.getText()
    if len(searchstring) == 0:
        return  #empty string search, cancel
            
    #if search string is different then we add it to the history list.
    #if searchstring != string:
    #    self.SearchHistory.insert(0,searchstring)
    #    if len(self.SearchHistory) > 8: #maximum 8 items
    #        self.SearchHistory.pop()
    #    self.onSaveSearchHistory()
    
    index=item.type.find(":")
    if index != -1:
        search_type = item.type[index+1:]
    else:
        search_type = ''
            
    #youtube search
    if item.type == 'search_youtube' or (search_type == 'html_youtube'):
        fn = searchstring.replace(' ','+')
        if item.URL != '':
            URL = item.URL
        else:
            URL = 'http://www.youtube.com/results?search_query='
        URL = URL + fn
                  
        #ask the end user how to sort
        possibleChoices = ["Relevance", "Date Added", "View Count", "Rating"]
        dialog = xbmcgui.Dialog()
        choice = dialog.select("Sort by", possibleChoices)

        #validate the selected item
        if choice == 1: #Date Added
            URL = URL + '&search_sort=video_date_uploaded'
        elif choice == 2: #View Count
            URL = URL + '&search_sort=video_view_count'
        elif choice == 3: #Rating
            URL = URL + '&search_sort=video_avg_rating'
               
        mediaitem=CMediaItem()
        mediaitem.URL = URL
        mediaitem.type = 'html_youtube'
        mediaitem.name = 'search results: ' + searchstring
        mediaitem.player = item.player

        #create history item
#        tmp = CHistorytem()
#        tmp.index = self.list.getSelectedPosition()
#        tmp.mediaitem = self.mediaitem

#        self.pl_focus = self.playlist
        result = ParsePlaylist(mediaitem=mediaitem)
                
#        if result == 0 and append == True: #successful
#            self.History.append(tmp)
#            self.history_count = self.history_count + 1
    elif item.type == 'search_shoutcast' or (search_type == 'xml_shoutcast'):
        fn=urllib.quote(searchstring)
        URL = 'http://www.shoutcast.com/sbin/newxml.phtml?search='
        URL = URL + fn
        
        mediaitem=CMediaItem()
        mediaitem.URL = URL
        mediaitem.type = 'xml_shoutcast'
        mediaitem.name = 'search results: ' + searchstring
        mediaitem.player = item.player

        #create history item
#        tmp = CHistorytem()
#        tmp.index = self.list.getSelectedPosition()
#        tmp.mediaitem = self.mediaitem

#        self.pl_focus = self.playlist
        result = ParsePlaylist(mediaitem=mediaitem)      
#        if result == 0 and append == True: #successful
#            self.History.append(tmp)
#            self.history_count = self.history_count + 1
    elif item.type == 'search_flickr' or (search_type == 'html_flickr'):
        fn = searchstring.replace(' ','+')
        URL = 'http://www.flickr.com/search/?q='
        URL = URL + fn
        
        mediaitem=CMediaItem()
        mediaitem.URL = URL
        mediaitem.type = 'html_flickr'
        mediaitem.name = 'search results: ' + searchstring
        mediaitem.player = item.player

        #create history item
#        tmp = CHistorytem()
#        tmp.index = self.list.getSelectedPosition()
#        tmp.mediaitem = self.mediaitem

#        self.pl_focus = self.playlist
        result = ParsePlaylist(mediaitem=mediaitem)
                
#        if result == 0 and append == True: #successful
#            self.History.append(tmp)
#            self.history_count = self.history_count + 1

    else: #generic search
        fn = urllib.quote(searchstring)
        URL = item.URL
        URL = URL + fn
                       
        mediaitem=CMediaItem()
        mediaitem.URL = URL
        if search_type != '':
            mediaitem.type = search_type
        else: #default
            mediaitem.type = 'playlist'
                    
        mediaitem.name = 'search results: ' + searchstring
        mediaitem.player = item.player

        #create history item
        #tmp = CHistorytem()

        #tmp.index = self.getPlaylistPosition()
        #tmp.mediaitem = self.mediaitem

        #self.pl_focus = self.playlist
        result = ParsePlaylist(mediaitem=mediaitem)
                
        #if result == 0 and append == True: #successful
            #self.History.append(tmp)
            #self.history_count = self.history_count + 1             

######################################################################
# Description: Deletes all files in a given folder and sub-folders.
#              Note that the sub-folders itself are not deleted.
# Parameters : folder=path to local folder
# Return     : -
######################################################################
def delFiles(folder):
    try:        
        for root, dirs, files in os.walk(folder , topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
    except IOError:
        return
        
                
############End of file
