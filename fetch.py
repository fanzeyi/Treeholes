# -*- coding: utf-8 -*-

import re
import datetime

from django.utils import simplejson as json

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from oauth import FanfouOAuth

CONSUMER_KEY = ""
CONSUMER_SECRET = ""
ACCESS_TOKEN_KEY = ""
ACCESS_TOKEN_SECRET = ""

class Status(db.Model):
    Content = db.StringProperty(required = True, \
                                multiline = True)
    Sent = db.BooleanProperty(default = False)

class FetchStatus(webapp.RequestHandler):
    def get(self):
        def Check(dm):
            reg_time = datetime.datetime.strptime(dm['sender']['created_at'], "%a %b %d %H:%M:%S +0000 %Y")
            minus = datetime.datetime.now() - reg_time
            if minus.days < 100:
                return False
            text = dm['text']
            urlre = re.compile(r"[http|ftp]://(.*)[com|net|cn|org|gd|ly|me|info]")
            if len(urlre.findall(text)) != 0:
                return False
            numre = re.compile(r"13[0-9]|14[57]|15[0-35-9]|18[0-26-9]\d{8}")
            if len(numre.findall(text)) != 0:
                return False
            return True
        self.response.headers['Content-Type'] = 'text/html'
        print 'Content-Type: text/html\n'
        tree = FanfouOAuth(CONSUMER_KEY, CONSUMER_SECRET)
        tree.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
        dms = json.loads(tree.fanfou_request("/direct_messages/inbox"))
        for dm in dms:
            if Check(dm):
                status = Status(Content = dm['text'])
                status.put()
            tree.fanfou_request("/direct_messages/destroy", post_args = {'id' : dm['id']})

class SendStatus(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        print 'Content-Type: text/html\n'
        statuses = db.GqlQuery("SELECT * FROM Status WHERE Sent = False LIMIT 5")
        if statuses.count() == 0:
            return 0
        tree = FanfouOAuth(CONSUMER_KEY, CONSUMER_SECRET)
        tree.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
        for status in statuses:
            tree.fanfou_request("/statuses/update", post_args = {'status' : status.Content.encode("utf-8")})
            status.Sent = True
            status.put()

app = webapp.WSGIApplication(
		[('/fetch', FetchStatus), \
         ('/send', SendStatus)],
		debug=True)

run_wsgi_app(app)
