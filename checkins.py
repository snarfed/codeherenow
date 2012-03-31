#!/usr/bin/python
"""Classes and code for fetching recent checkins.
"""

__author__ = ['Ryan Barrett <codeherenow@ryanb.org>']

import cgi
import datetime
import itertools
import logging
import re
import urllib
import urlparse
from webob import exc

import appengine_config
import tweepy
import util


TWITTER_SEARCH_URL = ('http://search.twitter.com/search.json?'
                      'result_type=recent&include_entities=1&%s')
# USERS_LOOKUP_URL = ('http://api.twitter.com/1/users/lookup.json?'
#                     'include_entities=true&screen_names=%s')


class Checkin(util.Struct):
  """Abstract base class for a checkin.

  Concrete subclasses should override username(), name(), url(), etc.
  """

  def username():
    raise NotImplementedError()

  def name():
    raise NotImplementedError()

  def url():
    raise NotImplementedError()


class Source(object):
  """Abstract base class for a checkin source. (e.g. Twitter, Facebook)

  Concrete subclasses must override the class constants below and implement
  get_checkins_near() and/or search_checkins().

  Attributes:
    handler: the current RequestHandler
  """

  def __init__(self, handler):
    self.handler = handler

  @staticmethod
  def get_checkins_near(lat, lon, radius_miles):
    """Returns a list of recent Checkins near a location.

    Args:
      lat: float
      lon: float
      radius_miles: float
    """
    raise NotImplementedError()

  @staticmethod
  def search_checkins(query):
    """Returns a list of recent Checkins that match a search query.

    Args:
      query: string
    """
    raise NotImplementedError()


class Twitter(Source):

  @staticmethod
  def get_checkins_near(lat, lon, radius_miles):
    """Returns a list of recent Checkins near a location.

    Args:
      lat: float
      lon: float
      radius_miles: float
    """
    url = TWITTER_SEARCH_URL % ('geocode=%g,%g,%gmi' % (lat, lon, radius_miles))
    return Twitter.get_tweets(url)

  @staticmethod
  def search_checkins(query):
    """Returns a list of recent Checkins that match a search query.

    Args:
      query: string
    """
    return Twitter.get_tweets(
        TWITTER_SEARCH_URL % ('q=%s' % urllib.quote_plus(query)))

  @staticmethod
  def get_tweets(url):
    """Fetches tweets and users from the Twitter API.

    Args:
      url: Twitter API url

    Returns:
      sequence of Tweets
    """
    resp = Twitter.jsonfetch(url).get('results', {})
    # users = Twitter.lookup_users(tweets)
    # return [Tweet(json=tweet, user=users.get(tweet.get(from_user)))
    #         for tweet in resp]
    return [Tweet(tweet=tweet) for tweet in resp]

  # not needed, since JSON tweet include from username and real name, yay!
  # @staticmethod
  # def lookup_users(tweets):
  #   """Returns a list of user JSON dicts for authors and mentions in tweets.

  #   Args:
  #     tweets: dict mapping string username to JSON user dict
  #   """
  #   screen_names = itertools.chain(*[
  #       # author
  #       [tweet.get('from_user')] +
  #       # mentions. twitter screen names are letters, numbers, and underscore.
  #       re.findall('@[A-Za-z0-9_]+', tweet.get('text', ''))
  #       for tweet in tweets])

  #   if not screen_names:
  #     return []

  #   url = USERS_LOOKUP_URL % ','.join(screen_names)
  #   resp = Twitter.jsonfetch(url)
  #   return dict((user.get('screen_name'), user) for user in resp)

  @staticmethod
  def jsonfetch(url, **kwargs):
    """Wraps util.jsonfetch(), signing with OAuth.
    """
    auth = tweepy.OAuthHandler(appengine_config.TWITTER_APP_KEY,
                               appengine_config.TWITTER_APP_SECRET)
    auth.set_access_token(appengine_config.TWITTER_ACCESS_TOKEN,
                               appengine_config.TWITTER_ACCESS_TOKEN_SECRET)
    method = kwargs.get('method', 'GET')
    headers = kwargs.setdefault('headers', {})

    parsed = urlparse.urlparse(url)
    url_without_query = urlparse.urlunparse(list(parsed[0:4]) + ['', ''])
    auth.apply_auth(url_without_query, method, headers,
                    # TODO: switch to urlparse.parse_qsl after python27 runtime
                    dict(cgi.parse_qsl(parsed.query)))
    logging.info('Signed with OAuth, populated Authorization header: %s',
                 headers.get('Authorization'))

    return util.jsonfetch(url, **kwargs)


class Tweet(Checkin):
  """A tweet with a location.

  Attributes:
    tweet: JSON dict with tweet data, including entities
      https://dev.twitter.com/docs/api/1/get/search
      https://dev.twitter.com/docs/tweet-entities
  #  from_user: JSON dict with user data
  #    https://dev.twitter.com/docs/api/1/get/users/lookup
  """

  def username(self):
    return self.tweet.get('from_user')

  def name(self):
    return self.tweet.get('from_user_name')

  def url(self):
    return None

  # def username(self):
  #   return self.user.get('screen_name')

  # def name(self):
  #   return self.user.get('name')

  # def url(self):
  #   return self.user.get('url')
