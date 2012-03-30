#!/usr/bin/python
"""Unit tests for util.py.
"""

__author__ = ['Ryan Barrett <codeherenow@ryanb.org>']

from webob import exc

import testutil
import util


class UtilTest(testutil.HandlerTest):

  def test_urlfetch(self):
    self.expect_urlfetch('http://my/url', 'hello', foo='bar')
    self.mox.ReplayAll()
    self.assertEquals('hello', util.urlfetch('http://my/url', foo='bar'))

  def test_urlfetch_error_passes_through(self):
    self.expect_urlfetch('http://my/url', 'my error', status=408)
    self.mox.ReplayAll()

    try:
      util.urlfetch('http://my/url')
    except exc.HTTPException, e:
      self.assertEquals(408, e.status_int)
      # self.assertEquals('my error', self.response.body)
