#!/usr/bin/python
"""Unit tests for hosts.py.
"""

__author__ = ['Ryan Barrett <codeherenow@ryanb.org>']

try:
  import json
except ImportError:
  import simplejson as json

import appengine_config
import hosts
import testutil

# test data
USERS = {u'users': [
    {'created': '2011-05-10T00:39:24Z',
     'created_at': '2011-05-10T00:39:24Z',
     'fullname': 'Ryan',
     'gravatar_id': 'fcbd5a34b3f555462d01c81755e7676b',
     'id': 'user-778068',
     'language': 'Python',
     'location': '',
     'login': 'snarfed',
     'name': 'Ryan',
     'type': 'user',
     'username': 'snarfed',
     },
    {'gravatar_id': '95de8e3290f060e1c219cf20d688955e',
     'id': 'user-883206',
     'login': 'alice',
     'type': 'user',
     'username': 'alice',
    }
    ]}
EVENTS = [
  hosts.Event(json={
    'type': 'PushEvent',
    'created_at': '2012-03-29T22:26:05Z',
    'repo': {
      'url': 'https://api.github.com/repos/soupmatt/codebreaker',
      'id': 3870276,
      'name': 'soupmatt/codebreaker'
    },
    'actor': {
      'gravatar_id': '52de1d1ba453387ebabe84e52b14af8a',
      'url': 'https://api.github.com/users/soupmatt',
      'id': 263409,
      'login': 'soupmatt'
    },
    'id': '1535825395',
    'payload': {
      'head': '348ac3a2506b2ae5f144add0ad7f684b7cc415ff',
      'size': 1,
      'push_id': 70108266,
      'commits': [
        {
          'sha': '348ac3a2506b2ae5f144add0ad7f684b7cc415ff',
          'author': {
            'name': 'Matt Campbell',
            'email': 'matt@soupmatt.com'
          },
          'url': 'https://api.github.com/repos/soupmatt/codebreaker/commits/348ac3a2506b2ae5f144add0ad7f684b7cc415ff',
          'distinct': True,
          'message': 'hacking at #shbp!'
        }
      ],
      'ref': 'refs/heads/master'
    }
  }),
  hosts.Event(json={
    'type': 'IssueCommentEvent',
    'created_at': '2012-03-29T22:26:04Z',
    'repo': {
      'url': 'https://api.github.com/repos/christkv/node-mongodb-native',
      'id': 462292,
      'name': 'christkv/node-mongodb-native'
    },
    'actor': {
      'gravatar_id': 'd1bf2ff368596018547b521e94211dbe',
      'url': 'https://api.github.com/users/d1april',
      'id': 1254892,
      'login': 'd1april'
    },
    'id': '1535825391',
    'payload': {
      'comment': {
        'created_at': '2012-03-29T22:26:03Z',
        'body': 'I tested it and it seems to work correctly now.\r\nIt trys to reconnect and gives up after some time and closed the connections.\r\n\r\nThat\'s ok. Thank you.',
        'updated_at': '2012-03-29T22:26:03Z',
        'url': 'https://api.github.com/repos/christkv/node-mongodb-native/issues/comments/4832692',
        'id': 4832692,
        'user': {
          'avatar_url': 'https://secure.gravatar.com/avatar/d1bf2ff368596018547b521e94211dbe?d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-140.png',
          'gravatar_id': 'd1bf2ff368596018547b521e94211dbe',
          'url': 'https://api.github.com/users/d1april',
          'id': 1254892,
          'login': 'd1april'
        }
      },
      'action': 'created',
    }
  }),
]


class GitHubTest(testutil.HandlerTest):

  def setUp(self):
    super(GitHubTest, self).setUp()
    appengine_config.GITHUB_ACCESS_TOKEN = 'my_token'

  def test_search_users(self):
    for query in 'foo', 'bar':
      url = 'https://github.com/api/v2/json/user/search/%s?access_token=my_token'
      self.expect_urlfetch(url % query, json.dumps(USERS))
    self.mox.ReplayAll()

    self.assert_equals(set(('snarfed', 'alice')),
                       hosts.GitHub.search_users(['foo', 'bar']))

  # def test_get_events(self):
  #   for username, event in zip(['x', 'y'], EVENTS):
  #     url = 'https://api.github.com/users/%s/events/public?access_token=my_token'
  #     self.expect_urlfetch(url % username, json.dumps([event.json]))
  #   self.mox.ReplayAll()

  #   self.assert_equals(EVENTS, hosts.GitHub.get_events(['x', 'y']))

  def test_search_recent_events(self):
    self.expect_urlfetch('https://api.github.com/events?access_token=my_token',
                         json.dumps([e.json for e in EVENTS]))
    self.mox.ReplayAll()
    self.assert_equals([EVENTS[0]], hosts.GitHub.search_recent_events('#shbp'))
