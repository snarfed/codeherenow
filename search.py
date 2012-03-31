#!/usr/bin/python
"""Serves the /search_* and /events_* endpoints.
"""

__author__ = ['Ryan Barrett <codeherenow@ryanb.org>']

import itertools
try:
  import json
except ImportError:
  import simplejson as json
import webapp2

import appengine_config
import checkins
import hosts
import util

from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

HEADER = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="content-type" content="text/html; charset=utf-8" />
  <script type="text/javascript" src="/static/ticker.js"></script>
  <link href="/static/style.css" rel="stylesheet" type="text/css" />
  <title>Super Happy Code!</title>
</head>

<body onload="">
<h1>Super Happy Code</h1>
"""

FOOTER = """
</body>
</html>
"""

class Handler(webapp2.RequestHandler):
  """Base handler class.
  """
  SOURCES = [checkins.Twitter]
  HOSTS = [hosts.GitHub]

  def get(self):
    pass


class EventsNear(Handler):
  """Searches for recent local checkins, then for events by those usernames.

  Query params:
    lat: float, latitude of location
    lon: float, longitude of location
    radius_miles: float, max distance from location
  """

  def get(self):
    lat = float(self.request.get('lat'))
    lon = float(self.request.get('lon'))
    radius = float(self.request.get('radius'))

    queries = []
    for source in self.SOURCES:
      for checkin in source.get_checkins_near(lat, lon, radius):
        queries += [checkin.username(), checkin.name()]

    events = []
    for host in self.HOSTS:
      usernames = host.search_users(queries)
      events += host.get_events(usernames)

    self.response.out.write(json.dumps([e.json for e in events]))


class SearchRecentEvents(Handler):
  """Searches for events by message.

  Query params:
    query: string search query
  """

  def get(self):
    query = self.request.get('query')
    event_lists = [host.search_recent_events(query) for host in self.HOSTS]
    events_json = [e.json for e in itertools.chain(*event_lists)]
    self.response.out.write(json.dumps(events_json))


class SearchRecentEvents(Handler):
  """Renders the ticker HTML page."""

  def get(self):
    query = self.request.get('query')
    event_lists = [host.search_recent_events(query) for host in self.HOSTS]
    events_json = [e.json for e in itertools.chain(*event_lists)]
    self.response.out.write(json.dumps(events_json))


class Ticker(Handler):
  """Renders the ticker HTML page."""

  def get(self):
    # High St. btw Hamilton and University, Palo Alto
    LAT = 37.442796
    LON = -122.161466
    RADIUS = 0.5
    QUERY = 'shbp'

    self.response.out.write(HEADER)
    for host in self.HOSTS:
      for events in host.search_recent_events(QUERY):
        self.response.out.write(template.render('templates/host-meta.xrds',
                                                event.json))
    self.response.out.write(FOOTER)


application = webapp2.WSGIApplication(
  [('/search_recent_events', SearchRecentEvents),
   ('/events_near', EventsNear),
   ('/ticker', Ticker),
  ],
  debug=appengine_config.DEBUG)

def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
