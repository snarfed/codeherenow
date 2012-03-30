"""App Engine settings.
"""

from __future__ import with_statement
import logging
import os

# app_identity.get_default_version_hostname() would be better here, but
# it doesn't work in dev_appserver since that doesn't set
# os.environ['DEFAULT_VERSION_HOSTNAME'].
HOST = os.getenv('HTTP_HOST')
SCHEME = 'https' if (os.getenv('HTTPS') == 'on') else 'http'

if not os.environ.get('SERVER_SOFTWARE', '').startswith('Development'):
  DEBUG = False
  # MOCKFACEBOOK = False
  # FACEBOOK_APP_ID_FILE = 'facebook_app_id'
  # FACEBOOK_APP_SECRET_FILE = 'facebook_app_secret'
else:
  DEBUG = True
  # MOCKFACEBOOK = False
  # FACEBOOK_APP_ID_FILE = 'facebook_app_id_local' 
  # FACEBOOK_APP_SECRET_FILE = 'facebook_app_secret_local'


def read(filename):
  """Returns the contents of filename, or None if it doesn't exist."""
  if os.path.exists(filename):
    with open(filename) as f:
      return f.read().strip()
  else:
    logging.warning('%s file not found, cannot authenticate!', filename)


# FACEBOOK_APP_ID = read(FACEBOOK_APP_ID_FILE)
# FACEBOOK_APP_SECRET = read(FACEBOOK_APP_SECRET_FILE)
TWITTER_APP_KEY = read('twitter_app_key')
TWITTER_APP_SECRET = read('twitter_app_secret')
TWITTER_ACCESS_TOKEN = read('twitter_access_token')
TWITTER_ACCESS_TOKEN_SECRET = read('twitter_access_token_secret')
