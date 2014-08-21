#!/usr/bin/env python
# -*- coding: utf-8 -*-
# epg.py - An implementation of different EPG grabber cores in Python 
# (C) 2012 HansMayer - http://supertv.3owl.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import urllib, urllib2, cookielib, time,re,os,socket,gzip,StringIO,zlib,inspect,sys,string
from datetime import datetime, timedelta,tzinfo

try: 
    try:
        raise
        import xml.etree.cElementTree as ElementTree
    except:
        from xml.etree import ElementTree
except: from elementtree import ElementTree

try: import simplejson as json
except: import json

try:
  from cStringIO import StringIO
except:
  from StringIO import StringIO
import zipfile


    
def decode (page):
    encoding = page.info().get("Content-Encoding")    
    if encoding in ('gzip', 'x-gzip', 'deflate'):
        content = page.read()
        if encoding == 'deflate':
            data = StringIO(zlib.decompress(content))
        else:
            data = gzip.GzipFile('', 'rb', 9, StringIO(content))
        page = data.read()
    else:
        page = page.read()

    return page
    
def getURL(url ,enc='utf-8',post=None,headers=None,ct=False):
    #try:
    cj = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-Agent', 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2;)'),('Accept-Encoding', 'gzip,deflate'),('Accept-Charset','utf-8')]
    if headers:
        opener.addheaders = [('User-Agent', 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2;)'),('Accept-Encoding', 'gzip,deflate'),('Accept-Charset','utf-8')]+headers
    if url[:7] == "file://":
        usock=open(url[7:],'r')
        response=usock.read()
    else:
        if ct:
            a={}
            for x in opener.addheaders:
                a[x[0]] = x[1] 
            req = urllib2.Request(url, data=post, headers=a)
            usock = urllib2.urlopen(req)
            response=usock.read()
        else:
            usock=opener.open(url,post)
            response=decode(usock)
        usock.close()
    if not enc:
        return response
    return unicode(response, enc,errors='strict')
#    except:
#        return '<b></b>'

class downloadSocket:
    def __init__(self, host, port):
        self.sock = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))        

    def fetch(self, msg):
        self.sock.send(msg)
        return self.sock.makefile().read()
        

class BaseEPG:
    nocheck = False
    def onInit(self):
        pass
    def __init__(self,chan):
        frm = inspect.stack()
        if frm[1][3] != 'listVideos' and frm[2][1].split('/')[-1] != 'update.py' and frm[1][3] != 'getList':
            sys.exit(0)

        self.conn = sqlite3.connect(EPGPATH)
        c=self.conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='epg';")
        
        et=c.fetchone()
        if not et or et[0] == 0:
            c.execute('''create table epg
            (title text, start int, end int, description text, thumb text,
            chan text, module text)''')
        c.close()
        
        cn = chan.split('|')
        self.chan=cn[0]
        if 'nochk' in cn: self.nocheck = True
        self.onInit()
    
    def hasDetails(self,title,start,end):
        module=self.__class__.__name__
        c=self.conn.cursor()
        c.execute("SELECT thumb,description from epg WHERE title=? AND start=? AND end = ? AND chan = ? AND module = ?", (title, time.mktime(start.timetuple()), time.mktime(end.timetuple()), self.chan, module))
        e=c.fetchone()
        c.close()
        if e:
            return (e[0]!='',e[1]!='')
        else:
            return (False,False)
    
    def insertIntoDB(self, listOfEntries,au=False):
        module=self.__class__.__name__
        c=self.conn.cursor()
        for l in listOfEntries:
            c.execute("SELECT count(start) from epg WHERE title=? AND start=? AND end = ? AND chan = ? AND module = ?", (l[0], time.mktime(l[1].timetuple()), time.mktime(l[2].timetuple()), self.chan, module))
            e=c.fetchone()
            if not e or e[0] < 1 or e == None:
                desc = ''
                thumb = ''
                if len(l) > 3:
                    desc = l[3]
                if len(l) > 4:
                    thumb = l[4]
                c.execute("INSERT INTO epg VALUES (?,?,?,?,?,?,?);", (l[0], time.mktime(l[1].timetuple()), time.mktime(l[2].timetuple()) ,desc,thumb, self.chan, module))
                self.conn.commit()
            elif au:
                desc = l[0]
                thumb = 'NT'
                if len(l) > 3:
                    desc = l[3]
                if len(l) > 4:
                    thumb = l[4]
                    
                c.execute('UPDATE epg SET thumb=?, description=? WHERE title=? AND start=? AND end = ? AND chan = ? AND module = ?;', (thumb,desc,l[0], int(time.mktime(l[1].timetuple())), int(time.mktime(l[2].timetuple())), self.chan, module))                
                self.conn.commit()
        c.close()
        
    def fetchEPG(self,day=0,limit=5):
        c=self.conn.cursor()
        nowDateTime = datetime.now(LocalTimezone)+timedelta(days=day)
        module=self.__class__.__name__
        
        c.execute("SELECT * from epg WHERE module=? AND chan=? AND start > ? AND end > ? ORDER BY end LIMIT ?", (module,self.chan,time.mktime((nowDateTime-timedelta(days=1)).timetuple()),time.mktime(nowDateTime.timetuple()),limit))
        es=c.fetchall()
        c.close()
        return es
        
    def getEPGForDays(self,days=3,limit=5,next=0,au=False):
        if next < days:
            es=self.fetchEPG(next,limit)
            if len(es) < limit and ((not self.nocheck) or au):
                self.getList(self.chan,offset=next*(-1),au=au)
                self.getEPGForDays(limit=limit, days=days,next=next+1,au=au)
        else:
            return self.fetchEPG()
    
    def getEntries(self,limit=5,next=0):
        nowDateTime = datetime.now(LocalTimezone)
        self.update()
        self.getEPGForDays(2)
        es=self.fetchEPG(limit=limit)
        tepg=[]
        for l in es:
            start=nowDateTime.fromtimestamp(l[1],LocalTimezone)
            end=nowDateTime.fromtimestamp(l[2],LocalTimezone)
            tepg.append([l[0],start,end,l[3],l[4]])
        return tepg
        
        
    def update(self):
        nowDateTime = time.mktime(datetime.now(LocalTimezone).timetuple())
        c=self.conn.cursor()
        c.execute("DELETE FROM epg WHERE end < ?",(str(nowDateTime),))
        self.conn.commit()
        c.close()
        

            
class XMLTVEPG(BaseEPG):
    def addClause(self, c1, c2):
        return c1 == c2
    def titlePreadd(self,title):
        return title
        
    def insertIntoDB(self, listOfEntries,au=False):
        module=self.__class__.__name__
        c=self.conn.cursor()
        for i,l in enumerate(listOfEntries):
            c.execute("SELECT count(start) from epg WHERE title=? AND start=? AND end = ? AND chan = ? AND module = ?", (l[0], time.mktime(l[1].timetuple()), time.mktime(l[2].timetuple()), l[4], module))
            e=c.fetchone()
            if not e or e[0] < 1 or e == None:
                thumb = 'NT'
                chan = l[4]
                desc = l[3]
                c.execute("INSERT INTO epg VALUES (?,?,?,?,?,?,?);", (l[0], time.mktime(l[1].timetuple()), time.mktime(l[2].timetuple()) ,desc,thumb, chan, module))
        self.conn.commit()
        c.close()
    
    def parseTree(self,zfp,au=False):
        tree = ElementTree.parse(zfp).getroot()
        listings=tree.findall('programme')
        tepg=[]
        nowDateTime = datetime.now(LocalTimezone)
        for l in listings:
            if not self.addClause(l.attrib.get('channel'), self.chan):
                continue
                
            minutes = (int(l.attrib.get('stop').split(' ')[1][-2:])+(int(l.attrib.get('stop').split(' ')[1][1:-2])*60))*(int(l.attrib.get('stop').split(' ')[1][0]+'1'))
            tzEnd = USTimeZone.FixedOffset(minutes,'XML')
            end=datetime.fromtimestamp(time.mktime(time.strptime(l.attrib.get('stop').split(' ')[0], "%Y%m%d%H%M%S"))).replace(tzinfo=tzEnd).astimezone(LocalTimezone)
            if end < nowDateTime:
                continue
            
            minutes = (int(l.attrib.get('start').split(' ')[1][-2:])+(int(l.attrib.get('start').split(' ')[1][1:-2])*60))*(int(l.attrib.get('start').split(' ')[1][0]+'1'))
            tzStart = USTimeZone.FixedOffset(minutes,'XML')
            start=datetime.fromtimestamp(time.mktime(time.strptime(l.attrib.get('start').split(' ')[0], "%Y%m%d%H%M%S"))).replace(tzinfo=tzStart).astimezone(LocalTimezone)
            
            try:
                title = self.titlePreadd(l.findtext('title'))
            except:
                continue
            desc = l.findtext('desc')
            tepg.append([title, start,end,desc,self.chan])
        self.insertIntoDB(tepg,au=au)

