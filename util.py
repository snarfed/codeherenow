#!/usr/bin/python
"""Misc utilities.
"""

__author__ = ['Ryan Barrett <codeherenow@ryanb.org>']

try:
  import json
except ImportError:
  import simplejson as json
import logging

from webob import exc

from google.appengine.api import urlfetch


class Struct(object):

  def __init__(self, **kwargs):
    """Keyword args are set as attrs on this object."""
    for key, val in kwargs.items():
      setattr(self, key, val)

  def __eq__(self, other):
    return vars(self) == vars(other)


def jsonfetch(url, **kwargs):
  """Wraps urlfetch and converts to JSON.

  Passes error responses through to the client by raising HTTPException.

  Args:
    url: str
    kwargs: passed through to urlfetch.fetch()

  Returns:
    JSON object
  """
  logging.debug('Fetching %s with kwargs %s', url, kwargs)
  resp = urlfetch.fetch(url, deadline=999, **kwargs)

  if resp.status_code == 200:
    return json.loads(resp.content)
  else:
    logging.warning('GET %s returned %d:\n%s',
                    url, resp.status_code, resp.content)
    # self.handler.response.headers.update(resp.headers)
    # self.handler.response.out.write(resp.content)
    raise exc.status_map.get(resp.status_code)(resp.content)
