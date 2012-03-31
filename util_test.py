#!/usr/bin/python
"""Unit tests for util.py.
"""

__author__ = ['Ryan Barrett <codeherenow@ryanb.org>']

from webob import exc

import testutil
import util


class UtilTest(testutil.HandlerTest):

  def test_jsonfetch(self):
    self.expect_urlfetch('http://my/url', '["x", "y"]', foo='bar')
    self.mox.ReplayAll()
    self.assertEquals(['x', 'y'], util.jsonfetch('http://my/url', foo='bar'))

  def test_jsonfetch_error_passes_through(self):
    self.expect_urlfetch('http://my/url', 'my error', status=408)
    self.mox.ReplayAll()

    try:
      util.jsonfetch('http://my/url')
    except exc.HTTPException, e:
      self.assertEquals(408, e.status_int)
      # self.assertEquals('my error', self.response.body)
