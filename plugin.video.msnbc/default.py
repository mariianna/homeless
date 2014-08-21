import time
import os, sys
import cgi
import xbmc, xbmcaddon, xbmcgui, xbmcplugin
import logging
logging.basicConfig(level=logging.DEBUG)
import urllib
from utils import *

from elementtree import ElementTree
    
__plugin__ = "MSNBC"
__author__ = 'Andre <andrepleblanc@gmail.com>'
__url__ = 'http://github.com/andrepl/plugin.video.msnbc/'
__date__ = '03-24-2011'
__version__ = '0.0.4'
__settings__ = xbmcaddon.Addon(id='plugin.video.msnbc')



class MSNBCPlugin(object):
    cache_timeout = 120
    base_url = 'http://www.msnbc.msn.com'
            
        
    def get_url(self,urldata):
        """
        Constructs a URL back into the plugin with the specified arguments.
        
        """
        return "%s?%s" % (self.script_url, urllib.urlencode(urldata,1))

    
    def get_dialog(self):
        return xbmcgui.Dialog()
    
    def set_stream_url(self, url, info=None):
        """
        Resolve a Stream URL and return it to XBMC. 
        
        'info' is used to construct the 'now playing' information
        via add_list_item.
        
        """
        listitem = xbmcgui.ListItem(label='clip', path=url)
        xbmcplugin.setResolvedUrl(self.handle, True, listitem)
        
        
    
    def end_list(self): 
        xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.endOfDirectory(self.handle, succeeded=True)


    
    def get_cache_dir(self):
        """
        return an acceptable cache directory.
        
        """
        # I have no idea if this is right.
        path = xbmc.translatePath('special://profile/addon_data/plugin.video.msnbc/cache/')
        if not os.path.exists(path):
            os.makedirs(path)
        return path


    def get_setting(self, id):
        """
        return a user-modifiable plugin setting.
        
        """
        return __settings__.getSetting(id)

    
    def get_xml(self, docid):
        path = os.path.join(self.get_cache_dir(), "%s.xml" % (docid,))
        if (not os.path.exists(path)) or (time.time() - os.path.getmtime(path) > self.cache_timeout):
            logging.debug("Downloading New Copy: %s" % (docid,))
            fh = open(path, 'w')
            fh.write(get_page(self.base_url + "/id/%s/displaymode/1219/" % (docid,)).read())
            fh.close()
        else:
            logging.debug("Using Cached Copy: %s" % (path,))
        return ElementTree.parse(path)
            
        

    def add_list_item(self, info, is_folder=True, return_only=False, 
                      context_menu_items=None, clear_context_menu=False, bookmark_parent=None, bookmark_id=None, bookmark_folder_id=None):
        """
        Creates an XBMC ListItem from the data contained in the info dict.
        
        if is_folder is True (The default) the item is a regular folder item
        
        if is_folder is False, the item will be considered playable by xbmc
        and is expected to return a call to set_stream_url to begin playback.

        if return_only is True, the item item isn't added to the xbmc screen but 
        is returned instead.
        
        
        Note: This function does some renaming of specific keys in the info dict.
        you'll have to read the source to see what is expected of a listitem, but in 
        general you want to pass in self.args + a new 'action' and a new 'remote_url'
        'Title' is also required, anything *should* be optional
        
        """
        if context_menu_items is None:
            context_menu_items = []
        
        if bookmark_parent is None:
            bookmark_url = self.get_url({'action': 'add_to_bookmarks', 'url': self.get_url(info)})
#            context_menu_items.append(("Bookmark", "XBMC.RunPlugin(%s)" % (bookmark_url,)))
        else:
            bminfo = {'action': 'remove_from_bookmarks', 'url': self.get_url(info), 'folder_id': bookmark_parent}
            if bookmark_id is not None:
                bminfo['bookmark_id'] = bookmark_id
            elif bookmark_folder_id is not None:
                bminfo['bookmark_folder_id'] = bookmark_folder_id
                
            bookmark_url = self.get_url(bminfo)
#            context_menu_items.append(("Remove From Bookmarks", "XBMC.RunPlugin(%s)" % (bookmark_url,)))
            
        info.setdefault('Thumb', 'None')
        info.setdefault('Icon', info['Thumb'])
        if 'Rating' in info:
            del info['Rating']
        
        li=xbmcgui.ListItem(
            label=info['Title'], 
            iconImage=info['Icon'], 
            thumbnailImage=info['Thumb']
        )
        
        
        if not is_folder:
            li.setProperty("IsPlayable", "true") 
            context_menu_items.append(("Queue Item", "Action(Queue)"))
        li.setInfo(type='Video', infoLabels=dict((k, unicode(v)) for k, v in info.iteritems()))
        
        # Add Context Menu Items
        if context_menu_items:
            li.addContextMenuItems(context_menu_items, 
                                   replaceItems=clear_context_menu)
            
            
        # Handle the return-early case
        if not return_only:
            kwargs = dict(
                handle=self.handle, 
                url=self.get_url(info),
                listitem=li,
                isFolder=is_folder
            )            
            return xbmcplugin.addDirectoryItem(**kwargs)
        
        return li
        
    def get_resource_path(self, *path):
        """
        Returns a full path to a plugin resource.
        
        eg. self.get_resource_path("images", "some_image.png")
        
        """
        p = os.path.join(__settings__.getAddonInfo('path'), 'resources', *path)
        if os.path.exists(p):
            return p
        raise ChannelException("Couldn't Find Resource: %s" % (p, ))

    def get_modal_keyboard_input(self, default=None, heading=None, hidden=False):
        keyb = xbmc.Keyboard(default, heading, hidden)
        keyb.doModal()
        val = keyb.getText()
        if keyb.isConfirmed():
            return val
        return None
    
        
    def action_browse(self):
        docid = self.args.get('docid', None)
        if not docid:
            docid = self.args['docid'] = '3096433'
            
        tree = self.get_xml(docid)
        
        logging.debug("Looking up %s" % (docid,))
        folders = []
        vids = []
        for i in tree.getroot():
            if i.tag == 'list':
                data = self.build_folder(i)
                folders.append(data)
                
            elif i.tag == 'video':
                data = self.build_video(i)
                vids.append(data)
                
        for f in folders:
            self.add_list_item(f)
            
        for v in vids:
            self.add_list_item(v, is_folder=False)
                
        self.end_list()

    def action_play(self):
        url = self.base_url + "/default.cdnx/id/%s/displaymode/1157/?t=.flv" % (self.args['docid'],)
        self.set_stream_url(url)
        
    def build_folder(self, el):
        data = {}
        data.update(self.args)
        data['Title'] = "[" + el.attrib['name'] + "]"
        data['action'] = 'browse'
        data['docid'] = el.attrib['docid']
        return data
    
    def build_video(self, el):
        data = {}
        data.update(self.args)
        data['action'] = 'play'
        data['Title'] = el.find("headline").text.strip()
        data['Plot'] = el.find("caption").text.strip()
        data['docid'] = el.attrib["docid"]
        for mtag in el.findall("./media"):
            if mtag.attrib['type'] == 'thumbnail':
                data['Thumb'] = mtag.text.strip()
                break
        
        return data
        
    def __call__(self):
        """
        This is the main entry point of the plugin.
        the querystring has already been parsed into self.args
        
        """
        
        action = self.args.get('action', None)
        
        if not action:
            action = 'browse'
        
        
        if hasattr(self, 'action_%s' % (action,)):
            func = getattr(self, 'action_%s' % (action,))
            return func()
        
        
        
        
    def __init__(self, script_url, handle, querystring):
        proxy = self.get_setting("http_proxy")
        port = self.get_setting("http_proxy_port")
        if proxy and port:
            proxy_handler = urllib2.ProxyHandler({'http':'%s:%s'%(proxy,port)})
            opener = urllib2.build_opener(proxy_handler)
            urllib2.install_opener(opener)

        self.script_url = script_url
        self.handle = int(handle)
        if len(querystring) > 2:
            self.querystring = querystring[1:]
            items = urldecode(self.querystring)
            self.args = dict(items)
        else:
            self.querystring = querystring
            self.args = {}
        logging.debug("Constructed Plugin %s" % (self.__dict__,))
        
if __name__ == '__main__':
    plugin = MSNBCPlugin(*sys.argv)
    plugin()
