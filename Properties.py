__author__ = 'rohan'
GOOGLE_REQUEST_TOKEN_URL = 'https://www.google.com/accounts/OAuthGetRequestToken'
GOOGLE_ACCESS_TOKEN_URL = 'https://www.google.com/accounts/OAuthGetAccessToken'
GOOGLE_AUTHORIZATION_URL = 'https://www.google.com/accounts/OAuthAuthorizeToken'
GOOGLE_CALLBACK_URL = 'http://k4nu.com/campaigns/g/oauth'
GOOGLE_CONSUMER_KEY = "anonymous"
GOOGLE_CONSUMER_SECRET = "anonymous"
GOOGLE_SCOPE = "https://mail.google.com/"
GOOGLE_RESOURCE_URL = "https://mail.google.com/mail/b/%s/imap/"
TWITTER_REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
TWITTER_ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
TWITTER_AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'
TWITTER_CALLBACK_URL = 'http://k4nu.com/campaigns/t/oauth'
TWITTER_CONSUMER_KEY = "jL2l985ZHPYiRC5I4IOlzg"
TWITTER_CONSUMER_SECRET = "hcVxPzghKsZNyHDy8YSzTyiFhIJ7S30Ajw7KX4Bas"


def setTwitterCallback(callback):
    global TWITTER_CALLBACK_URL
    TWITTER_CALLBACK_URL = callback
def setGoogleCallback(callback):
    global GOOGLE_CALLBACK_URL
    GOOGLE_CALLBACK_URL=callback