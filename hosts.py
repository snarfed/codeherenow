#!/usr/bin/python
"""Classes for fetching events from source code hosting services.
"""

__author__ = ['Ryan Barrett <codeherenow@ryanb.org>']

import cgi
import datetime
import itertools
import logging
import urllib
import urlparse

import appengine_config
import util


class Event(util.Struct):
  """A source repository event, e.g. a commit.

  Attributes:
    json: JSON dict
  """

  def message(self):
    """Extracts and returns the human-readable string message for this event."""
    type = self.json['type']
    payload = self.json['payload']

    # TODO: unit tests for more of these
    # TODO: PullRequestReviewCommentEvent, CommitCommentEvent
    if type == 'PushEvent':
      return '\n'.join(c['message'] for c in payload['commits'])
    elif type == 'IssuesEvent':
      return '\n'.join(payload['issue']['labels'] + [payload['issue']['body']])
    elif type == 'IssueCommentEvent':
      return payload['comment']['body']
    elif type == 'PullRequestEvent':
      return payload['pull_request']['body']

    return None

  def __eq__(self, other):
    return self.json == other.json

  def __repr__(self):
    return repr(self.json)


class Host(object):
  """Abstract base class for a source code hosting provider, e.g. GitHub.

  Concrete subclasses must implement search_users() and get_events().
  """

  @staticmethod
  def search_users(queries):
    """Returns a sequence of string usernames that match the search queries.

    Args:
      queries: sequence of strings
    """
    raise NotImplementedError()

  @staticmethod
  def get_events(usernames):
    """Return a sequence of Events for the given usernames.

    Args:
      usernames: sequence of strings
    """
    raise NotImplementedError()

  @staticmethod
  def search_recent_events(phrase):
    """Return recent events with the given phrase in their message.

    Args:
      phrase: string
    """
    raise NotImplementedError()


class GitHub(Host):
  """Implements GitHub."""

  SEARCH_URL = 'https://github.com/api/v2/json/user/search/%s'
  USER_EVENTS_URL = 'https://api.github.com/users/%s/events/public'
  EVENTS_URL = 'https://api.github.com/events'

  @staticmethod
  def search_users(queries):
    # TODO: parallelize.
    # https://developers.google.com/appengine/docs/python/urlfetch/asynchronousrequests
    resps = [GitHub.jsonfetch(GitHub.SEARCH_URL % q) for q in queries]
    users = itertools.chain(*[r.get('users', []) for r in resps])
    return set([u['username'] for u in users])

  @staticmethod
  def get_events(usernames):
    # TODO: parallelize.
    events = [GitHub.jsonfetch(GitHub.USER_EVENTS_URL % u) for u in usernames]
    return [Event(json=e) for e in itertools.chain(*events)]

  @staticmethod
  def search_recent_events(phrase):
    events_json = GitHub.jsonfetch(GitHub.EVENTS_URL)
    events = [Event(json=e) for e in events_json]
    logging.warning('@@ %r' % e.message())
    return [e for e in events if phrase in str(e.message())]

  @staticmethod
  def jsonfetch(url):
    """Wraps util.jsonfetch() and adds the access_token query param."""
    parsed = list(urlparse.urlparse(url))
    # query params are in index 4
    # TODO: when this is on python 2.7, switch to urlparse.parse_qsl
    params = cgi.parse_qsl(parsed[4]) + [
        ('access_token', appengine_config.GITHUB_ACCESS_TOKEN)]
    parsed[4] = urllib.urlencode(params)
    url = urlparse.urlunparse(parsed)
    return util.jsonfetch(url)
