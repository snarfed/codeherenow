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

  # <link href="https://a248.e.akamai.net/assets.github.com/stylesheets/bundles/github-e2fb92c4dcb5e5b1ce2ffd0e84d6bf80937d9197.css" media="screen" rel="stylesheet" type="text/css" />
  # <link href="https://a248.e.akamai.net/assets.github.com/stylesheets/bundles/github2-98a6177ed18ac7b415e311fdb34652f17ad0038c.css" media="screen" rel="stylesheet" type="text/css" />

  # <script src="https://a248.e.akamai.net/assets.github.com/javascripts/bundles/jquery-225576cef50ef2097c9f9fbcd8953c1572544611.js" type="text/javascript"></script>
  # <script src="https://a248.e.akamai.net/assets.github.com/javascripts/bundles/github-353ded132c604f1bdf010516392d71052f37ffcf.js" type="text/javascript"></script>

HEADER = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="content-type" content="text/html; charset=utf-8" />
  <meta http-equiv="refresh" content="30" />
  <script type="text/javascript" src="/static/ticker.js"></script>
  <link href="/static/style.css" rel="stylesheet" type="text/css" />
  <title>Super Happy Code!</title>

</head>

<body onload="">
<h1>Super Happy Code!</h1>
<h3>(GitHub checkins happening right here, right now)</h3>

<body class="logged_in page-profile mine linux  env-production " data-blob-contribs-enabled="yes">
<div id="wrapper">
<div class="last">
"""

FOOTER = """
</div>
</div>
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
    PHRASES = ('shbp',)

    self.response.out.write(HEADER)
    for host in self.HOSTS:
      for event in host.search_recent_events(PHRASES):
        self.response.out.write(template.render(event.template_file(), event.json))
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
