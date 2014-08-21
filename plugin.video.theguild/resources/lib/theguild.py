#!/usr/bin/env python

import urllib
import demjson
import re

class Video( object ):
  def __init__( self, title, description, video_path, thumb_path, height, width, duration, uuid, season):
    self.title = title
    self.description = description
    self.video_path = video_path
    self.thumb_path = thumb_path
    self.height = height
    self.width = width
    self.duration = duration
    self.uuid = uuid
    self.season = season

# search for msn videos by tag
def tag_search(tag, results=16, lang='us', **kwargs):
  kwargs.update({
      'tag': tag,
      'mk': lang,
      'ns': 'VC_Source',
      'sf': 'Relevance',
      'sd': '-1',
      'ind': '1',
      'ps': results,
      'responseEncoding': 'json'
  })
  TAG_BASE = 'http://edge1.catalog.video.msn.com/VideoByTag.aspx'
  url = TAG_BASE + '?' + urllib.urlencode(kwargs)
  f = urllib.urlopen(url)
  data = f.read()
  f.close()
  return data

def keynat(string):
  r'''A natural sort helper function for sort() and sorted()
  without using regular expression.

  >>> elems = ('Z', 'a', '10', '1', '9')
  >>> sorted(elems)
  ['1', '10', '9', 'Z', 'a']
  >>> sorted(elems, key=keynat)
  ['1', '9', '10', 'Z', 'a']
  '''
  r = []
  for c in string:
    try:
      c = int(c)
      try: r[-1] = r[-1] * 10 + c
      except: r.append(c)
    except:
      r.append(c)
  return r

def get_theguild():
  # initially get just 1 result so that we can find the total number available and then get that total with the next call
  SEARCH_NUM = 1

  # get the json data for all of the guild shows and then decode to pthon data, must use demjson instead of
  # the builtin simpljson because simpljson balks at some of the special characters included in the stream
  json = tag_search(tag='Xbox_Channel:The_Guild', results=SEARCH_NUM)
  pydata = demjson.decode(json)

  # check to see if we got all of the shows available, and if not get the total and get the rest if there are more
  if SEARCH_NUM < pydata["$total"]:
    json = tag_search(tag='Xbox_Channel:The_Guild', results=pydata["$total"])
    pydata = demjson.decode(json)

  # create an re to match the constructed 'SxEy' title format used below
  p = re.compile('S(?P<S>\d+)E\d+')

  # create a list containing Video class objects that hold the title a path to each show
  # reformat the title by changing 'Season n' to 'Sn' and 'Episode n' to 'En'
  shows = []
  for elem in pydata["video"]:
    title = ''
    description = ''
    video_path = ''
    thumb_path = ''
    height = ''
    width = ''
    duration = ''
    season = ''
    title = re.sub(r'Season (?P<S>\d+) - Episode (?P<E>\d+)', r'S\g<S>E\g<E>', elem["title"]["$"])
    title = re.sub(r'Season (?P<S>\d+)', r'S\g<S>', title)
    title = re.sub(r'Episode (?P<E>\d+)', r'E\g<E>', title)
    description = elem["description"]["$"]
    duration = elem["durationSecs"]["$"]
    uuid = elem["uuid"]["$"]
    m = p.match(title)
    if m:
      season = 'Season %s' % m.group(1)
    else:
      season = 'Extras'

    # formatcode 1003 is the flv file
    for video in elem["videoFiles"]["videoFile"]:
      if video["$formatCode"] == '1003':
        video_path = video["uri"]["$"]

    # formatcode 2007 is the path for the smallest thumbnail available, 2001 is the code for the actual
    # heigth and width of the video file iyself
    for file in elem["files"]["file"]:
      if file["$formatCode"] == '2007':
        thumb_path = file["uri"]["$"]
      elif file["$formatCode"] == '2001':
        height = file["$height"]
        width = file["$width"]

    shows.append(Video(title, description, video_path, thumb_path, height, width, duration, uuid, season))

  # sort the list by the title of the show, using a numeric sort order so that 2 would come before 11
  shows.sort(key=lambda obj: keynat(obj.title))

  # separate all the shows out into a nested dictionary of lists based on the season of the show, one list for each season, or 'Extras' if
  # the show was not in a season, and then use the season name as the key for the dictionary
  season = {}
  for video in shows:
    if not season.has_key(video.season):
      season[video.season] = []
    season[video.season].append(video)
  return season
