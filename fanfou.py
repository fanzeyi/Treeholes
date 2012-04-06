# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: fanfou.py
# CREATED: 14:03:51 14/03/2012
# MODIFIED: 14:05:16 14/03/2012

import uuid
import hmac
import time
import urllib
import hashlib
import binascii
import urlparse
import requests


try:
    from urlparse import parse_qs  # Python 2.6+
except ImportError:
    from cgi import parse_qs

if str is unicode:
    def b(s):
        return s.encode('latin1')
    bytes_type = bytes
else:
    def b(s):
        return s
    bytes_type = str

def _oauth_escape(val):
    if isinstance(val, unicode):
        val = val.encode("utf-8")
    return urllib.quote(val, safe="~")

_UTF8_TYPES = (type(None))
def escape_utf8(value):
    if isinstance(value, _UTF8_TYPES):
        return value
    # assert isinstance(value, unicode)
    return value.encode("utf-8")

def _signature_request(consumer_token, method, url, args = {}, token = None):
    parts = urlparse.urlparse(url)
    scheme, netloc, path = parts[:3]
    normalized_url = scheme.lower() + "://" + netloc.lower() + path

    base_elems = []
    base_elems.append(method.upper())
    base_elems.append(normalized_url)
    base_elems.append("&".join("%s=%s" % (k, _oauth_escape(str(v)))
                               for k, v in sorted(args.items())))
    
    base_string =  "&".join(_oauth_escape(e) for e in base_elems)
    key_elems = [escape_utf8(urllib.quote(consumer_token["secret"], safe='~'))]
    key_elems.append(escape_utf8(urllib.quote(token["secret"], safe='~') if token else ""))
    key = b("&").join(key_elems)

    hash = hmac.new(key, escape_utf8(base_string), hashlib.sha1)
    return binascii.b2a_base64(hash.digest())[:-1]

class FanfouOAuth(object):
    _API_BASE_URL = "http://api.fanfou.com"
    _REQUEST_TOKEN_URL = "http://fanfou.com/oauth/request_token"
    _AUTHENTICATE_URL = "http://fanfou.com/oauth/authenticate"
    _ACCESS_TOKEN_URL = "http://fanfou.com/oauth/access_token"
    def __init__(self, key, secret, callback = None):
        self.key = key
        self.secret = secret
        self.callback = callback
    def _get_consumer_token(self):
        return dict(key    = self.key, 
                    secret = self.secret)
    def _get_access_token(self):
        if self._ACCESS_TOKEN_KEY and self._ACCESS_TOKEN_SECRET:
            return dict( key = self._ACCESS_TOKEN_KEY, 
                         secret = self._ACCESS_TOKEN_SECRET)
        return None
    def _oauth_request_parameters(self, url, access_token, parameters={},
                                  method="GET"):
        consumer_token = self._get_consumer_token()
        base_args = dict(
            oauth_consumer_key     = consumer_token["key"],
            oauth_token            = access_token["key"],
            oauth_signature_method = "HMAC-SHA1",
            oauth_timestamp        = str(int(time.time())),
            oauth_nonce            = binascii.b2a_hex(uuid.uuid4().bytes),
            oauth_version          = "1.0a", 
        )
        args = {}
        args.update(base_args)
        args.update(parameters)
        signature = _signature_request(consumer_token, method, url, args,
                                       access_token)
        base_args["oauth_signature"] = signature
        return base_args
    def set_access_token(self, key, secret):
        self._ACCESS_TOKEN_KEY = key
        self._ACCESS_TOKEN_SECRET = secret
    def fanfou_request(self, path, access_token = None, \
                       post_args = None, **args):
        url = self._API_BASE_URL + path + ".json"
        if not access_token:
            access_token = self._get_access_token()
        if access_token:
            all_args = {}
            all_args.update(args)
            all_args.update(post_args or {})
            method = "POST" if post_args is not None else "GET"
            oauth = self._oauth_request_parameters(url, access_token, all_args, method = method)
            args.update(oauth)
        if args: url += "?" + urllib.urlencode(args)
        if method == "GET":
            result = requests.get(url)
        else:
            result = requests.post(url, data = post_args)
        return result.content
