# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para seriespepito
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import xbmc, xbmcgui

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools
from pelisalacarta import buscador

__channel__ = "peliculaspepito"
__category__ = "F"
__type__ = "generic"
__title__ = "PeliculasPepito"
__language__ = "ES"

DEBUG = config.get_setting("debug")

PELICULASPEPITO_REQUEST_HEADERS = []
PELICULASPEPITO_REQUEST_HEADERS.append(["User-Agent", "Mozilla/5.0 (Windows NT 6.1; rv:28.0) Gecko/20100101 Firefox/28.0"])
PELICULASPEPITO_REQUEST_HEADERS.append(["Accept-Encoding","gzip, deflate"])
PELICULASPEPITO_REQUEST_HEADERS.append(["Accept-Language","es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"])
PELICULASPEPITO_REQUEST_HEADERS.append(["Accept","text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"])
PELICULASPEPITO_REQUEST_HEADERS.append(["Connection","keep-alive"])
PELICULASPEPITO_REQUEST_HEADERS.append(["Cookie","_ga=GA1.2.1377145840.1398328462"])
PELICULASPEPITO_REQUEST_HEADERS.append(["Referer","http://www.peliculaspepito.com/"])

def isGeneric():
    return True

def mainlist(item):
    logger.info("[seriespepito.py] mainlist")

    itemlist = []
	
    itemlist.append( Item(channel=__channel__, action="novedades"        , title="Estrenos", url="http://www.peliculaspepito.com/",fanart="http://pelisalacarta.mimediacenter.info/fanart/seriespepito.jpg"))
    itemlist.append( Item(channel=__channel__, action="nuevas"        , title="Últimas añadidas", url="http://www.peliculaspepito.com/",fanart="http://pelisalacarta.mimediacenter.info/fanart/seriespepito.jpg"))
    itemlist.append( Item(channel=__channel__, action="listalfabetico"   , title="Listado alfabético",fanart="http://pelisalacarta.mimediacenter.info/fanart/seriespepito.jpg"))
    itemlist.append( Item(channel=__channel__, action="lomasvisto"    , title="Lo mas visto",    url="http://www.peliculaspepito.com/",fanart="http://pelisalacarta.mimediacenter.info/fanart/seriespepito.jpg"))
    itemlist.append( Item(channel=__channel__, action="buscar"        , title="Buscador", url="http://www.peliculaspepito.com/",fanart="http://pelisalacarta.mimediacenter.info/fanart/seriespepito.jpg"))
    
    return itemlist

def buscar(item):
    keyboard = xbmc.Keyboard()
    keyboard.doModal()
    busqueda=keyboard.getText()
    data = scrapertools.cachePage("http://www.peliculaspepito.com/buscador/" + busqueda + "/")
    data = scrapertools.get_match(data,'<ul class="lista_peliculas">(.*?)</ul>')
    patron  = '<li>'
    patron += '<a.*?href="([^"]+)"[^<]+'
    patron += '<img.*?alt="([^"]+)" src="([^"]+)"[^>]+>'
    
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    
    itemlist = []
    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        logger.info("title="+scrapedtitle)
        title = scrapertools.htmlclean(scrapedtitle).strip()
        title = title.replace("\r","").replace("\n","")
        #title = unicode( title, "iso-8859-1" , errors="replace" ).encode("utf-8")
        title = re.compile("\s+",re.DOTALL).sub(" ",title)
        logger.info("title="+title)
        url = scrapedurl
        thumbnail = scrapedthumbnail
        plot = ""
        plot = unicode( plot, "iso-8859-1" , errors="replace" ).encode("utf-8")
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        
        itemlist.append( Item(channel=__channel__, action="findvideos" , title=title , url=url, thumbnail=thumbnail, plot=plot, show=title, viewmode="movie", fanart="http://pelisalacarta.mimediacenter.info/fanart/seriespepito.jpg"))

    return itemlist


   
def novedades(item):
    logger.info("[peliculaspepito.py] novedades")

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    data = scrapertools.get_match(data,'<ul class="lista_peliculas">(.*?)</ul>')
    
    '''
    <ul class="lista_peliculas">
    <li>
    <a class="tilcelpel" href="http://capitan-america-el-soldado-de-invierno.peliculaspepito.com/" title="Capitán América: El soldado de invierno">
    <img id="img_11011" src="http://s.peliculaspepito.com/peliculas/11011-capitan-america-2-el-retorno-del-primer-vengador-thumb.jpg" alt="Capitán América: El soldado de invierno" data-id="11011"></img>
	
	<ul class="lista_peliculas">
	<li>
	<a class="tilcelpel" title="Capitán América: El soldado de invierno" href="http://capitan-america-el-soldado-de-invierno.peliculaspepito.com/">
	<img id="img_11011" data-id="11011" alt="Capitán América: El soldado de invierno" src="http://s.peliculaspepito.com/peliculas/11011-capitan-america-2-el-retorno-del-primer-vengador-thumb.jpg" />
	</a>
	'''
    patron  = '<li>'
    patron += '<a.*?href="([^"]+)"[^<]+'
    patron += '<img.*?alt="([^"]+)" src="([^"]+)"[^>]+>.*?<p class="pidilis">(.*?)</p>'


    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    itemlist = []
    for scrapedurl,scrapedtitle,scrapedthumbnail, scrapedquality in matches:
        logger.info("title="+scrapedtitle)
        title = scrapertools.htmlclean(scrapedtitle).strip()
        title = title.replace("\r","").replace("\n","")+ ' [' + scrapedquality.replace("&nbsp;","") + ']'
        #title = unicode( title, "iso-8859-1" , errors="replace" ).encode("utf-8")
        title = re.compile("\s+",re.DOTALL).sub(" ",title)
        logger.info("title="+title)

        url = scrapedurl
        thumbnail = scrapedthumbnail
        plot = ""
        plot = unicode( plot, "iso-8859-1" , errors="replace" ).encode("utf-8")
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        itemlist.append( Item(channel=__channel__, action="findvideos" , title=title , url=url, thumbnail=thumbnail, plot=plot, show=title, viewmode="movie", fanart="http://pelisalacarta.mimediacenter.info/fanart/seriespepito.jpg"))

    return itemlist
	
def nuevas(item):
    logger.info("[peliculaspepito.py] novedades")

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    data = scrapertools.get_match(data,'<div class="subtitulo">Nuevos contenidos(.*?)</ul>')
    
    '''
   <li>
   <a class="tilcelpel" title="El diablo metió la mano" href="http://el-diablo-metio-la-mano.peliculaspepito.com/">
   <img id="img_2834" data-id="2834" alt="El diablo metió la mano" src="http://s.peliculaspepito.com/peliculas/2834-el-diablo-metio-la-mano-thumb.jpg" />
   </a>
   <div id="imgtilinfo2834" class="til_info">
   <p>
   <a title="El diablo metió la mano" href="http://el-diablo-metio-la-mano.peliculaspepito.com/">El diablo metió la mano</a>
   </p>
   <p class="pcalidi"><span class="flag flag_0"></span></p><p class="pidilis">DVD&nbsp;RIP</p></div>
   <a title="El diablo metió la mano" href="http://el-diablo-metio-la-mano.peliculaspepito.com/">
   <div data-id="2834" id="til_info_sensor2834" data-on="0" data-an="0" class="til_info_sensor">
   </div></a></li>
   '''
    patron  = '<li>'
    patron += '<a.*?href="([^"]+)"[^<]+'
    patron += '<img.*?alt="([^"]+)" src="([^"]+)"[^>]+>'
    patron += '.*?<p class="pidilis">([^<]+)</p>.*?</div>'


    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    itemlist = []
    for scrapedurl,scrapedtitle,scrapedthumbnail, scrapedquality in matches:
        logger.info("title="+scrapedtitle)
        title = scrapertools.htmlclean(scrapedtitle).strip()
        title = title.replace("\r","").replace("\n","")+ ' [' + scrapedquality.replace("&nbsp;"," ")+ ']'
        #title = unicode( title, "iso-8859-1" , errors="replace" ).encode("utf-8")
        title = re.compile("\s+",re.DOTALL).sub(" ",title)
        logger.info("title="+title)

        url = scrapedurl
        thumbnail = scrapedthumbnail
        plot = ""
        plot = unicode( plot, "iso-8859-1" , errors="replace" ).encode("utf-8")
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        itemlist.append( Item(channel=__channel__, action="findvideos" , title=title , url=url, thumbnail=thumbnail, plot=plot, show=title, viewmode="movie", fanart="http://pelisalacarta.mimediacenter.info/fanart/seriespepito.jpg"))

    return itemlist

def lomasvisto(item):
    logger.info("[seriespepito.py] lomasvisto")

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    data = scrapertools.get_match(data,'Lo más visto ayer(.*?)</ul>')
    #<a class="clearfix top" href="http://arrow.seriespepito.com/"><img class="thumb_mini" alt="Arrow" src="http://www.seriespepito.com/uploads/series/1545-arrow-thumb.jpg" />Arrow</a></li>
    '''
	<li>
	<a class="clearfix top" title="Ocho apellidos vascos con 1.215 visitas." href="http://ocho-apellidos-vascos.peliculaspepito.com/">
	<img class="thumb_mini" alt="Ocho apellidos vascos" src="http://s.peliculaspepito.com/peliculas/13558-ocho-apellidos-vascos-thumb.jpg" />Ocho apellidos vascos
	</a>
	</li>
    '''
    patron  = '<a.*?href="([^"]+)"[^<]+'
    patron += '<img.*?src="([^"]+)"[^>]+>([^<]+)</a>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    itemlist = []
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        logger.info("title="+scrapedtitle)
        title = scrapertools.htmlclean(scrapedtitle).strip()
        title = title.replace("\r","").replace("\n","")
        #title = unicode( title, "iso-8859-1" , errors="replace" ).encode("utf-8")
        title = re.compile("\s+",re.DOTALL).sub(" ",title)
        logger.info("title="+title)

        url = scrapedurl
        thumbnail = scrapedthumbnail
        plot = ""
        plot = unicode( plot, "iso-8859-1" , errors="replace" ).encode("utf-8")
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        itemlist.append( Item(channel=__channel__, action="findvideos" , title=title , url=url, thumbnail=thumbnail, plot=plot, show=title, viewmode="movie", fanart="http://pelisalacarta.mimediacenter.info/fanart/seriespepito.jpg"))

    return itemlist

def allserieslist(item):
    logger.info("[peliculaspepito.py] allserieslist")

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    data = scrapertools.get_match(data,"<ul class='nav' id='lista_completa_series_ul'>(.*?)</ul>")
    patron = "<li><a href='([^']+)'>([^<]+)</a></li>"

    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    itemlist = []
    for match in matches:
        scrapedtitle = unicode( match[1].strip(), "iso-8859-1" , errors="replace" ).encode("utf-8")
        scrapedurl = match[0]
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        # Ajusta el encoding a UTF-8
        scrapedtitle = unicode( scrapedtitle, "iso-8859-1" , errors="replace" ).encode("utf-8")
        scrapedplot = unicode( scrapedplot, "iso-8859-1" , errors="replace" ).encode("utf-8")

        itemlist.append( Item(channel=__channel__, action="episodios" , title=scrapedtitle , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, show=title,fanart="http://pelisalacarta.mimediacenter.info/fanart/seriespepito.jpg"))

    return itemlist

def listalfabetico(item):
    logger.info("[peliculaspepito.py] mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, action="peliculas" , title="0-9",url="http://www.peliculaspepito.com/lista-peliculas/num/"))
    for letra in ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']:
        itemlist.append( Item(channel=__channel__, action="peliculas" , title=letra,url="http://www.peliculaspepito.com/lista-peliculas/"+letra.lower()+"/",fanart="http://pelisalacarta.mimediacenter.info/fanart/seriespepito.jpg"))

    return itemlist

def peliculas(item):
    logger.info("[peliculaspepito.py] peliculas")

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    data = scrapertools.get_match(data,'<ul class="ullistadoalfa">(.*?)</ul>')

    patron = '<li><a title="([^"]+)" href="([^"]+)"[^<]'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    itemlist = []
    for scrapedtitle,scrapedurl in matches:
        #title = unicode( scrapedtitle.strip(), "iso-8859-1" , errors="replace" ).encode("utf-8")
        title = scrapedtitle.strip()
        url = scrapedurl
        plot = ""
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos" , title=title , url=url, plot=plot, show=title,viewmode="movie", fanart="http://pelisalacarta.mimediacenter.info/fanart/seriespepito.jpg"))

    return itemlist


def detalle_programa(item,data=""):
    if data=="":
        data = scrapertools.cachePage(item.url)
    
    #<img class="img-polaroid imgcolserie" alt="Battlestar Galactica 2003" src="http://www.seriespepito.com/uploads/series/121-battlestar-galactica-2003.jpg"></center>
    try:
        data2 = scrapertools.get_match(data,'<img class="img-polaroid imgcolserie" alt="[^"]+" src="([^"]+)"')
        item.thumbnail = data2.replace("%20"," ")
    except:
        pass

    # Argumento
    try:
        data2 = scrapertools.get_match(data,'<div class="subtitulo">\s+Sinopsis.*?</div>(.*?)</div>')
        item.plot = scrapertools.htmlclean(data2)
    except:
        pass

    return item

def episodios(item):
    logger.info("[seriespepito.py] list")

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    
    # Completa plot y thumbnail
    item = detalle_programa(item,data)

    data = scrapertools.get_match(data,'<div class="accordion"(.*?)<div class="subtitulo">')
    logger.info(data)

    # Extrae los capítulos
    '''
    <tbody>
    <tr>
    <td>
    <a class="asinenlaces" title="&nbsp;0x01&nbsp;-&nbsp;Battlestar Galactica 2003&nbsp;-&nbsp;Capitulo 1" href="http://battlestar-galactica-2003.seriespepito.com/temporada-0/capitulo-1/">
    <i class="icon-film"></i>&nbsp;&nbsp;
    <strong>0x01</strong>
    &nbsp;-&nbsp;Battlestar Galactica 2003&nbsp;-&nbsp;Capitulo 1&nbsp;</a><button id="capvisto_121_0_1" class="btn btn-warning btn-mini sptt pull-right bcapvisto ctrl_over" data-tt_my="left center" data-tt_at="right center" data-tt_titulo="Marca del último capítulo visto" data-tt_texto="Este es el último capítulo que has visto de esta serie." data-id="121" data-tem="0" data-cap="1" type="button"><i class="icon-eye-open"></i></button></td></tr><tr><td><a  title="&nbsp;0x02&nbsp;-&nbsp;Battlestar Galactica 2003&nbsp;-&nbsp;Capitulo 2" href="http://battlestar-galactica-2003.seriespepito.com/temporada-0/capitulo-2/"><i class="icon-film"></i>&nbsp;&nbsp;<strong>0x02</strong>&nbsp;-&nbsp;Battlestar Galactica 2003&nbsp;-&nbsp;Capitulo 2&nbsp;<span class="flag flag_0"></span></a><button id="capvisto_121_0_2" class="btn btn-warning btn-mini sptt pull-right bcapvisto ctrl_over" data-tt_my="left center" data-tt_at="right center" data-tt_titulo="Marca del último capítulo visto" data-tt_texto="Este es el último capítulo que has visto de esta serie." data-id="121" data-tem="0" data-cap="2" type="button"><i class="icon-eye-open"></i></button></td></tr></tbody>
    '''
    patron  = '<tr>'
    patron += '<td>'
    patron += '<a.*?href="([^"]+)"[^<]+'
    patron += '<i[^<]+</i[^<]+'
    patron += '<strong>([^<]+)</strong>'
    patron += '([^<]+)<(.*?)<button'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    itemlist = []
    for scrapedurl,scrapedepisode,scrapedtitle,idiomas in matches:
        #title = unicode( scrapedtitle.strip(), "iso-8859-1" , errors="replace" ).encode("utf-8")
        title = scrapedepisode + " " + scrapedtitle.strip()
        title = scrapertools.entityunescape(title)
        if "flag_0" in idiomas:
            title = title + " (Español)"
        if "flag_1" in idiomas:
            title = title + " (Latino)"
        if "flag_2" in idiomas:
            title = title + " (VO)"
        if "flag_3" in idiomas:
            title = title + " (VOS)"
        url = scrapedurl
        thumbnail = item.thumbnail
        plot = item.plot
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        itemlist.append( Item(channel=__channel__, action="findvideos" , title=title , url=url, thumbnail=thumbnail, plot=plot, show=item.show, viewmode="movie_with_plot"))

    if (config.get_platform().startswith("xbmc") or config.get_platform().startswith("boxee")) and len(itemlist)>0:
        itemlist.append( Item(channel=item.channel, title="Añadir esta serie a la biblioteca de XBMC", url=item.url, action="add_serie_to_library", extra="episodios", show=item.show,fanart="http://pelisalacarta.mimediacenter.info/fanart/seriespepito.jpg"))
        itemlist.append( Item(channel=item.channel, title="Descargar todos los episodios de la serie", url=item.url, action="download_all_episodes", extra="episodios", show=item.show,fanart="http://pelisalacarta.mimediacenter.info/fanart/seriespepito.jpg"))

    return itemlist

def findvideos(item):
    logger.info("[peliculaspepito.py] findvideos")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cachePage(item.url)
    #logger.info(data)
    '''	
	<tr>
	<td id="tdidioma193869" class="tdidioma"><span class="flag flag_0">0</span></td>
	<td id="tdcalidad193869" class="tdcalidad">DVD&nbsp;RIP</td>
	<td class="tdfecha">24/03/2014</td>
	<td id="tdservidor193869" class="tdservidor"><img src="http://s.peliculaspepito.com/servidores/41-63845.png" alt="Magnovideo" />&nbsp;Magnovideo</td>
	<td class="tdenlace"><a class="btn btn_link" data-servidor="41" rel="nofollow" target="_blank" title="Ver&nbsp;(1)..." href="http://www.enlacespepito.com/02dead0f64bd970839e781f51eb48e86/193869/ef86bada70b2d0b58e3c21650195102e/c5529e8146dc4e3e642d647a91906e95/8d0e3e03b693eeb8dd20b35566362828/e1beb13340a813596ba87569b325ca67/9c98233803c502d86dcaad2fc6a31a4a/41f845928fd331b6e1478488e9864c8eaf15e2cc595c2e4e8259c02e44ac19ee1e7218f96bf81b32d52479b76992c12d/cefebb79e4d90ed1e8a2702c331025bf/57b22bd2a1f634dafd55ae1437daacb0/3d7eae712706ec33cc3a7566ac937114.html"><i class="icon-play"></i>&nbsp;&nbsp;Ver&nbsp;(1)</a></td>
	<td class="tdusuario"><a  title="Barbie"  href="http://www.peliculaspepito.com/usuarios/perfil/472b07b9fcf2c2451e8781e944bf5f77cd8457c8">Barbie</a></td>
			<td class="tdcomentario"></td>
			<td class="tdreportar">
				<button data-envio="193869" class="btn btn-danger btn-mini hide sptt pull-right breportar" data-tt_my="left center" data-tt_at="right center" data-tt_titulo="Reportar problemas..." data-tt_texto="¿Algún problema con el enlace?, ¿esta roto?, ¿el audio esta mal?, ¿no corresponde el contenido?, repórtalo y lo revisaremos, ¡gracias!." type="button"><i class="icon-warning-sign icon-white"></i></button>			</td>
			</tr>	
    '''

    # Listas de enlaces
    patron = '<td id="tdidioma[^"]+" class="tdidioma"><span class="[^"]+">(.*?)</span></td>.*?'
    patron += '<td id="tdservidor[^"]+" class="tdservidor"><img src="([^"]+)"[^>]+>([^<]+)</td[^<]+'
	# patron += '<td class="tdenlace"><a class="btn btn-mini enlace_link" data-servidor="([^"]+)" rel="nofollow" target="_blank" title="[^"]+" href="([^"]+)"'
    patron += '<td class="tdenlace"><a class="btn btn_link" data-servidor="([^"]+)" rel="nofollow" target="_blank" title="([^"]+)" href="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for idiomas,scrapedthumbnail,servidor,dataservidor,scrapedtitle, scrapedurl in matches:
        url = urlparse.urljoin(item.url,scrapedurl)
        title = item.title + " [" + servidor.replace("&nbsp;","") + "]"
        plot = ""

        if "0" in idiomas:
            title = title + " [Español]"
        if "1" in idiomas:
            title = title + " [Latino]"
        if "2" in idiomas:
            title = title + " [VO]"
        if "3" in idiomas:
            title = title + " [VOS]"

        itemlist.append( Item(channel=__channel__, action="play" , title=title , url=url, thumbnail=item.thumbnail, plot=item.plot, show=item.show, folder=False,fanart="http://pelisalacarta.mimediacenter.info/fanart/seriespepito.jpg"))

    return itemlist

def play(item):
    logger.info("[seriespepito.py] play")
    itemlist=[]
    
    data = scrapertools.cache_page(item.url, headers = PELICULASPEPITO_REQUEST_HEADERS)
    videoitemlist = servertools.find_video_items(data=data)
    i=1
    for videoitem in videoitemlist:
        if not "favicon" in videoitem.url:
            videoitem.title = "Mirror %d%s" % (i,videoitem.title)
            videoitem.fulltitle = item.fulltitle
            videoitem.channel=channel=__channel__
            videoitem.show = item.show
            itemlist.append(videoitem)
            i=i+1

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si está ok el canal.
def test():
    from servers import servertools
    
    # mainlist
    mainlist_items = mainlist(Item())
    
    # Da por bueno el canal si alguno de los vídeos de "Novedades" devuelve mirrors
    series_items = novedades(mainlist_items[0])
    bien = False
    for serie_item in series_items:
        episode_items = episodios( item=serie_item )

        for episode_item in episode_items:
            mediaurls = findvideos( episode_item )
            for mediaurl in mediaurls:
                if len( play(mediaurl) )>0:
                    return True

    return False