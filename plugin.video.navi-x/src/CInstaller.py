#############################################################################
#
# Navi-X Playlist browser
# by rodejo (rodejo16@gmail.com)
#############################################################################

#############################################################################
#
# CInstaller:
# Intaller for scripts and plugins.
#############################################################################

from string import *
import sys, os.path
import urllib
import urllib2
import re, random, string
import xbmc, xbmcgui
import re, os, time, datetime, traceback
import shutil
import zipfile
from settings import *
from CFileLoader import *
from libs2 import *

try: Emulating = xbmcgui.Emulating
except: Emulating = False

#RootDir = os.getcwd()
#if RootDir[-1]==';': RootDir=RootDir[0:-1]
#if RootDir[-1]!='\\': RootDir=RootDir+'\\'
#imageDir = RootDir + "\\images\\"
#cacheDir = RootDir + "\\cache\\"
#imageCacheDir = RootDir + "\\cache\\imageview\\"
#scriptDir = "Q:\\scripts\\"
#pluginDir = "Q:\\plugins\\"
#myDownloadsDir = RootDir + "My Downloads\\"
#initDir = RootDir + "\\init\\"

######################################################################
# Description: Handles installation of scripts and plugins
######################################################################
class CInstaller(xbmcgui.Window):

    ######################################################################
    # Description: Handles Installation of a scripts ZIP file.
    # Parameters : URL = URL of the file
    #              mediaitem=CMediaItem object to load
    # Return     : -
    ######################################################################
    def InstallScript(self, URL='', mediaitem=CMediaItem()):
        if URL != '':
            self.URL = URL
        else:
            self.URL = mediaitem.URL
        
        #download the file.
        loader = CFileLoader()
        loader.load(self.URL, cacheDir + 'script.zip')
        if loader.state != 0:
            return -2
        filename = loader.localfile

        result = self.unzip_file_into_dir(filename, scriptDir)   

        return result
                
    ######################################################################
    # Description: Handles Installation of a plugin ZIP file.
    # Parameters : URL = URL of the file
    #              mediaitem=CMediaItem object to load
    # Return     : -
    ######################################################################
    def InstallPlugin(self, URL='', mediaitem=CMediaItem()):            
        if URL != '':
            self.URL = URL
        else:
            self.URL = mediaitem.URL
               
        #retrieve the type of plugin
        index=mediaitem.type.find(":")
        if index != -1:
            subdir = mediaitem.type[index+1:] + '\\'
        else:
            subdir = ''
        
        #download the file.
        loader = CFileLoader()
        loader.load(self.URL, cacheDir + 'plugin.zip', content_type='zip')

        if loader.state != 0:
            if loader.state == -2:
                dialog = xbmcgui.Dialog()
                dialog.ok(" Installer", "Failed. Not a ZIP file.", "Use the standard Download feature.")
            return -2
        filename = loader.localfile
             
        result = self.unzip_file_into_dir(filename, pluginDir + subdir)    
       
        return result

    ######################################################################
    # Description: Unzip a file into a dir
    # Parameters : file = the zip file
    #              dir = destination directory
    # Return     : -
    ######################################################################                    
    def unzip_file_into_dir(self, file, dir):
        chk_confirmation = False

        dir = xbmc.translatePath(dir)
        if os.path.exists(dir) == False:
            try:
                os.makedirs(dir) #create the directory
            except IOError:
                return -1 #failure
            
        zfobj = zipfile.ZipFile(file)

        for name in zfobj.namelist():
            index = name.rfind('/')
            if index != -1:
                #entry contains path
                if os.path.exists(dir+name[:index+1]):
                    #directory exists
                    if chk_confirmation == False:
                        dialog = xbmcgui.Dialog()
                        if dialog.yesno("Installer", "Directory " + dir+name[:index] + " already exists, continue?") == False:
                            return -1
                else:
                    #directory does not exist. Create it.
                    try:
                        #create the directory structure
                        os.makedirs(os.path.join(dir, name[:index+1]))
                    except IOError:
                        return -1 #failure
                    
            if not name.endswith('/'):
                #entry contains a filename
                try:
                    outfile = open(os.path.join(dir, name), 'wb')
                    outfile.write(zfobj.read(name))
                    outfile.close()
                except IOError:
                    pass #There was a problem. Continue...
                 
            chk_confirmation = True
        return 0 #succesful

                