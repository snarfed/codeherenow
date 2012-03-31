#!/usr/bin/python
"""Serves the /search_* and /events_* endpoints.
"""

__author__ = ['Ryan Barrett <codeherenow@ryanb.org>']

import itertools
try:
  import json
except ImportError:
  import simplejson as json
# import logging
# import re
# import os
# import urllib
import webapp2
# from webob import exc

import appengine_config
import checkins
import hosts
import util

from google.appengine.ext.webapp.util import run_wsgi_app


class Handler(webapp2.RequestHandler):
  """Base handler class.
  """
  SOURCES = [checkins.Twitter]
  HOSTS = [hosts.GitHub]

  def get(self):
    pass


class EventsNear(Handler):
  """Searches for recent local checkins, then for events by those usernames.
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


class SearchEvents(Handler):
  """Searches for events by message.
  """

  def get(self):
    pass


application = webapp2.WSGIApplication(
  # [('/search_events', SearchEvents)],
  [('/events_near', EventsNear)],
  debug=appengine_config.DEBUG)

def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
