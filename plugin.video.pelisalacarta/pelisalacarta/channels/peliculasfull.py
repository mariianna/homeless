# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para peliculasfull
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "peliculasfull"
__category__ = "F,S"
__type__ = "xbmc"
__title__ = "Peliculasfull"
__language__ = "ES"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[peliculasfull.py] mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Listar todas"     , action="peliculas", url="http://www.peliculasfull.net"))
    itemlist.append( Item(channel=__channel__, title="Listar por categorias" , action="listado_categorias", url=""))
    itemlist.append( Item(channel=__channel__, title="Listar por géneros" , action="listado_generos", url=""))
    itemlist.append( Item(channel=__channel__, title="Listar por calidades" , action="listado_calidades", url=""))
    itemlist.append( Item(channel=__channel__, title="Listar por años" , action="listado_anys", url=""))
    itemlist.append( Item(channel=__channel__, title="Listar por paises" , action="listado_paises", url=""))
    itemlist.append( Item(channel=__channel__, title="Buscador" , action="search", url=""))
    return itemlist

def search(item,texto):
    logger.info("[peliculasfull.py] search")
    if item.url=="":
        item.url="http://www.peliculasfull.net/search?q="
    texto = texto.replace(" ","+")
    item.url = item.url+texto
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []


def listado_categorias(item):
    logger.info("[peliculasfull.py] mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Estrenos"     , action="peliculas", url="http://www.peliculasfull.net/search/label/Estrenos?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="Clásicos"     , action="peliculas", url="http://www.peliculasfull.net/search/label/Clasicos?max-results=32"))
    return itemlist

def listado_generos(item):
    logger.info("[peliculasfull.py] mainlist")
    itemlist = []    
    itemlist.append( Item(channel=__channel__, title="Animación"     , action="peliculas", url="http://www.peliculasfull.net/search/label/Animacion?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="Acción"     , action="peliculas", url="http://www.peliculasfull.net/search/label/Accion?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="Animación"     , action="peliculas", url="http://www.peliculasfull.net/search/label/Animacion?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="Aventura"     , action="peliculas", url="http://www.peliculasfull.net/search/label/Aventura?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="Ciencia-Ficción"     , action="peliculas", url="http://www.peliculasfull.net/search/label/Ciencia-ficcion?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="Comedia"     , action="peliculas", url="http://www.peliculasfull.net/search/label/Comedias?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="Animación"     , action="peliculas", url="http://www.peliculasfull.net/search/label/Animacion?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="Crimen"     , action="peliculas", url="http://www.peliculasfull.net/search/label/Crimen?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="Documentales"     , action="peliculas", url="http://www.peliculasfull.net/search/label/Documental?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="Drama"     , action="peliculas", url="http://www.peliculasfull.net/search/label/Drama?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="Fantasía"     , action="peliculas", url="http://www.peliculasfull.net/search/label/Fantasia?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="Musical"     , action="peliculas", url="http://www.peliculasfull.net/search/label/Musical?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="Romance"     , action="peliculas", url="http://www.peliculasfull.net/search/label/Romance?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="Suspense"     , action="peliculas", url="http://www.peliculasfull.net/search/label/Suspense?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="Terror"     , action="peliculas", url="http://www.peliculasfull.net/search/label/Terror?max-results=32"))
    return itemlist
    
    
def listado_calidades(item):
    logger.info("[peliculasfull.py] mainlist")
    itemlist = []    
    itemlist.append( Item(channel=__channel__, title="3D"     , action="peliculas", url="http://www.peliculasfull.net/search/label/3D?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="HD"     , action="peliculas", url="http://www.peliculasfull.net/search/label/HD?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="DVD"     , action="peliculas", url="http://www.peliculasfull.net/search/label/DVD?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="BR-Screener"     , action="peliculas", url="http://www.peliculasfull.net/search/label/Bluray-Screener?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="CAM"     , action="peliculas", url="http://www.peliculasfull.net/search/label/Camara?max-results=32"))
    return itemlist
    
def listado_anys(item):
    logger.info("[peliculasfull.py] mainlist")
    itemlist = []    
    itemlist.append( Item(channel=__channel__, title="2013"     , action="peliculas", url="http://www.peliculasfull.net/search/label/2013?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="2012"     , action="peliculas", url="http://www.peliculasfull.net/search/label/2012?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="2011"     , action="peliculas", url="http://www.peliculasfull.net/search/label/2011?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="2010"     , action="peliculas", url="http://www.peliculasfull.net/search/label/2010?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="2009"     , action="peliculas", url="http://www.peliculasfull.net/search/label/2009?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="2008"     , action="peliculas", url="http://www.peliculasfull.net/search/label/2008?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="2007"     , action="peliculas", url="http://www.peliculasfull.net/search/label/2007?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="2006"     , action="peliculas", url="http://www.peliculasfull.net/search/label/2006?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="2005"     , action="peliculas", url="http://www.peliculasfull.net/search/label/2005?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="2004"     , action="peliculas", url="http://www.peliculasfull.net/search/label/2004?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="2003"     , action="peliculas", url="http://www.peliculasfull.net/search/label/2003?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="2002"     , action="peliculas", url="http://www.peliculasfull.net/search/label/2002?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="2001"     , action="peliculas", url="http://www.peliculasfull.net/search/label/2001?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="2000"     , action="peliculas", url="http://www.peliculasfull.net/search/label/2000?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="Anteriores a 2000"     , action="peliculas", url="http://www.peliculasfull.net/search/label/antes-2000?max-results=32"))
    return itemlist
    
    
def listado_paises(item):
    logger.info("[peliculasfull.py] mainlist")
    itemlist = []    
    itemlist.append( Item(channel=__channel__, title="Colómbia"     , action="peliculas", url="http://www.peliculasfull.net/search/label/Colombianas?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="España"     , action="peliculas", url="http://www.peliculasfull.net/search/label/Espa%C3%B1a?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="México"     , action="peliculas", url="http://www.peliculasfull.net/search/label/Mexicanas?max-results=32"))
    itemlist.append( Item(channel=__channel__, title="EEUU"     , action="peliculas", url="http://www.peliculasfull.net/search/label/Usa?max-results=32"))
    return itemlist
    
   
def peliculas(item):
    logger.info("[peliculasfull.py] peliculas")
    itemlist = []
    data = scrapertools.cache_page(item.url)    
    patron = "<div class='post bar hentry'>[^<]+<h2 class='post-title entry-title'>[^<]+<a href='([^']+)'>([^<]+)</a>.*?"
    patron += "<div><span style='color: #fec700;'>calidad : </span>([^<]+)</div>.*?"
    patron += '<div id=.*?summary.*?><div style="float: left; margin-bottom: 1em; margin-right: 1em;">[^<]+<a href="([^"]+)".*?target="_blank">.*?<span class="ficha">SINOPSIS : :</span>(.*?)</div>'    
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle,scrapedquality, scrapedthumbnail, scrapedplot in matches:    
            url = scrapedurl
            scrapedtitle = scrapertools.htmlclean(scrapedtitle)
            scrapedquality = scrapedquality.replace('\n','')
            title = scrapedtitle + " - Calidad:" + scrapedquality
            thumbnail = scrapedthumbnail
            plot = scrapertools.htmlclean(scrapedplot)            
            # Añade al listado
            itemlist.append( Item(channel=__channel__, action="findvideos", title= title, url=url , thumbnail=thumbnail , plot=plot , folder=True) )
            
    # EXTREA EL LINK DE LA SIGUIENTE PAGINA    
    patron = "<a class='blog-pager-older-link'.*?href='([^']+)' id='Blog1_blog-pager-older-link' title='Next Post'>Next Movie"
    matches = re.compile(patron,re.DOTALL).findall(data)
    for match in matches:
        if len(matches) > 0:
            url = match
            url = scrapertools.htmlclean(url)
            title = ">> Página Siguiente "
            thumbnail = ""
            plot = ""
            # Añade al listado
            itemlist.append( Item(channel=__channel__, action="peliculas", title=title , url=url , thumbnail=thumbnail , plot=plot , folder=True) )
    return itemlist

def findvideos(item):
    logger.info("[peliculasfull.py] peliculas")
    itemlist = []
    data = scrapertools.cache_page(item.url)   
    data = data.replace('(','')
    data = data.replace(')','')
    patron = '<script>online"([^"]+)","([^"]+)","([^"]+)","([^"]+)","([^"]+)","([^"]+)","[^"]+";</script>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl, scrapedserver,scrapedlenguaje, scrapedsubs, scrapedcalidad, scrapedcalidad2 in matches:   
            url = scrapedurl
            url = scrapertools.htmlclean(url)
            scrapedserver = scrapedserver.upper()
            title = "Ver en " +  scrapedserver + " [" + scrapedlenguaje + " " + scrapedsubs + " " + scrapedcalidad + " " + scrapedcalidad2+"] "
            thumbnail = ""
            plot = ""
            # Añade al listado
            itemlist.append( Item(channel=__channel__, action="play", title= title, url=url , thumbnail=thumbnail , plot=plot , folder=False) )    
    return itemlist
    

def play(item):    
    itemlist=[]
    itemlist = servertools.find_video_items(data=item.url)
    i=1
    for videoitem in itemlist:
        videoitem.title = "Mirror %d%s" % (i,videoitem.title)
        videoitem.channel=channel=__channel__
        i=i+1
    return itemlist