#!/usr/bin/python
"""Unit tests for search.py.
"""

__author__ = ['Ryan Barrett <codeherenow@ryanb.org>']

try:
  import json
except ImportError:
  import simplejson as json
import mox

import checkins
import checkins_test
import hosts
import hosts_test
import search
import testutil


class FakeSource(checkins.Source):
  expected_queries = None
  expected_usernames = None

  @staticmethod
  def get_checkins_near(lat, lon, radius_miles):
    return []

  @staticmethod
  def search_checkins(queries):
    return []


class FakeHost(hosts.Host):
  expected_queries = None
  expected_usernames = None

  @staticmethod
  def search_users(queries):
    return []

  @staticmethod
  def get_events(usernames):
    return []


# setup
search.Handler.SOURCES = [FakeSource]
search.Handler.HOSTS = [FakeHost]


class EventsNearTest(testutil.HandlerTest):

  def setUp(self):
    super(EventsNearTest, self).setUp(application=search.application)
    self.reset()

  def reset(self):
    self.mox.UnsetStubs()
    self.mox.ResetAll()
    self.mox.StubOutWithMock(FakeSource, 'get_checkins_near')
    self.mox.StubOutWithMock(FakeSource, 'search_checkins')
    self.mox.StubOutWithMock(FakeHost, 'search_users')
    self.mox.StubOutWithMock(FakeHost, 'get_events')

  def check_request(self, url, expected, *args, **kwargs):
    resp = self.application.get_response(url, *args, **kwargs)
    self.assertEquals(200, resp.status_int)
    self.assert_equals(expected, resp.body)

  def test_get_events_near(self):
    FakeSource.get_checkins_near(1.23, -4.56, .5)\
        .AndReturn([checkins_test.TWEET_CHECKIN])
    FakeHost.search_users(['snarfed_org', 'Ryan Barrett'])\
        .AndReturn(['snarfed', 'ryan'])
    FakeHost.get_events(['snarfed', 'ryan'])\
        .AndReturn(hosts_test.EVENTS)
    self.mox.ReplayAll()

    self.check_request('/events_near?lat=1.23&lon=-4.56&radius=.5',
                       json.dumps([e.json for e in hosts_test.EVENTS]))
