import urllib,urllib2,os,random,xbmcplugin,xbmcgui
import ClassHandler, TestClient

handler = ClassHandler.ClassHandler()

#######################################################################################
def ShowMainMenu():
    classInstance = handler.exists(TestClient.TestClass) or handler.new(TestClient.TestClass, ())
    addDir("1. Show Class","",1,"")
    addDir("2. Change Test Value","",2,"")

#######################################################################################
def ChangeValue():
    classInstance = handler.exists(TestClient.TestClass)

    newValue = random.randint(1,99)
    classInstance.testValue = newValue
    
    # Then save local changes to the server
    handler.save(classInstance)

    # And reacquire the remote version of the instance, to make sure our changes persisted
    handler.update(classInstance)
    ShowResults()

#######################################################################################
def ShowResults():
    classInstance = handler.exists(TestClient.TestClass)
    value = classInstance.testValue
    addLink("Test Value is now %s" % value, "", "")

#######################################################################################
# Utility Functions
#######################################################################################
def get_params():
    param=[]
    paramstring=sys.argv[2]
    print "Params:", paramstring
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
    return param

def addLink(name,url,iconimage):
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
    return ok

def addDir(name,url,mode,iconimage):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok
        
              
#######################################################################################
# Main
#######################################################################################

params=get_params()
url=None
name=None
mode=None
try:
    url=urllib.unquote_plus(params["url"])
except:
    pass
try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode=int(params["mode"])
except:
    pass
print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
if mode==None:# or url==None or len(url)<1:
    print "MAIN MENU : "
    ShowMainMenu()
if mode==1:
    ShowResults()
elif mode==2:
    ChangeValue()

xbmcplugin.endOfDirectory(int(sys.argv[1]))