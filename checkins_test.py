#!/usr/bin/python
"""Unit tests for checkins.py.
"""

__author__ = ['Ryan Barrett <codeherenow@ryanb.org>']

try:
  import json
except ImportError:
  import simplejson as json

import mox

import checkins
import testutil


# test data
TWEET_JSON = {
  'created_at': 'Wed Feb 22 20:26:41 +0000 2012',
  'id': 172417043893731329,
  'text': 'portablecontacts-unofficial: PortableContacts for Facebook and Twitter! http://t.co/SuqMPgp3 cc @alice',
  'from_user': 'snarfed_org',
  'from_user_name': 'Ryan Barrett',
  'entities': {'media': [{'media_url': 'http://p.twimg.com/AnJ54akCAAAHnfd.jpg'}]},
  }
# USERS = [
#     {'name': 'Ryan Barrett',
#      'screen_name': 'snarfed_org',
#      'url': 'http://snarfed.org/'
#      },
#     {'name': 'Alice',
#      'screen_name': 'alice',
#      'url': 'http://alice.com/'
#      },
#     ]
TWEET_CHECKIN = checkins.Tweet(tweet=TWEET_JSON)
# TWEET_CHECKINS = [checkins.Tweet(tweet=TWEET_JSON, user=u) for u in USERS]


class TwitterTest(testutil.HandlerTest):
  def check_authorization_header(self, headers):
    """We should include OAuth Authorization headers in Twitter requests."""
    self.assertTrue(headers['Authorization'])
    return True

  def test_get_checkins_near(self):
    self.expect_urlfetch(
        'http://search.twitter.com/search.json?'
        'result_type=recent&include_entities=1&geocode=1.23,-4.56,0.5mi',
        json.dumps({'results': [TWEET_JSON, TWEET_JSON]}),
        headers=mox.Func(self.check_authorization_header))
    self.mox.ReplayAll()
    self.assert_equals([TWEET_CHECKIN, TWEET_CHECKIN],
                       checkins.Twitter.get_checkins_near(1.23, -4.56, .5))

  def test_search_checkins(self):
    self.expect_urlfetch(
        'http://search.twitter.com/search.json?'
        'result_type=recent&include_entities=1&q=foo+bar',
        json.dumps({'results': [TWEET_JSON, TWEET_JSON]}),
        headers=mox.Func(self.check_authorization_header))
    self.mox.ReplayAll()
    self.assert_equals([TWEET_CHECKIN, TWEET_CHECKIN],
                       checkins.Twitter.search_checkins('foo bar'))


class TweetTest(testutil.HandlerTest):

  def test_username(self):
    self.assert_equals('snarfed_org', TWEET_CHECKIN.username())

  def test_name(self):
    self.assert_equals('Ryan Barrett', TWEET_CHECKIN.name())

  # def test_url(self):
  #   self.assert_equals('http://snarfed.org/', TWEET_CHECKIN.url())

  # def test_search_checkins(self):
  #   self.expect_urlfetch(
  #       'http://search.twitter.com/search.json?'
  #       'result_type=recent&include_entities=1&q=foo+bar',
  #       json.dumps({'results': [TWEET_JSON, TWEET_JSON]}),
  #       headers=mox.Func(self.check_authorization_header))
  #   self.mox.ReplayAll()
  #   self.assert_equals([TWEET_CHECKIN, TWEET_CHECKIN],
  #                      checkins.Twitter.search_checkins('foo bar'))
