#!/usr/bin/python
"""Misc utilities.
"""

__author__ = ['Ryan Barrett <codeherenow@ryanb.org>']

import logging

from webob import exc

from google.appengine.api import urlfetch as gae_urlfetch


def urlfetch(url, **kwargs):
  """Wraps urlfetch. Passes error responses through to the client.

  ...by raising HTTPException.

  Args:
    url: str
    kwargs: passed through to urlfetch.fetch()

  Returns:
    the HTTP response body
  """
  logging.debug('Fetching %s with kwargs %s', url, kwargs)
  resp = gae_urlfetch.fetch(url, deadline=999, **kwargs)

  if resp.status_code == 200:
    return resp.content
  else:
    logging.warning('GET %s returned %d:\n%s',
                    url, resp.status_code, resp.content)
    # self.handler.response.headers.update(resp.headers)
    # self.handler.response.out.write(resp.content)
    raise exc.status_map.get(resp.status_code)(resp.content)
