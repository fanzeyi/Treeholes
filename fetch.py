# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: fetch.py
# CREATED: 14:08:26 14/03/2012
# MODIFIED: 12:22:03 06/04/2012

import re
import datetime
import simplejson as json

from db import TreeholesDB
from fanfou import FanfouOAuth

from config import *

ALLOW_USER = ["fanzeyi"]

def Check(dm):
    if dm['sender']['id'] in ALLOW_USER:
        return True
    reg_time = datetime.datetime.strptime(dm['sender']['created_at'], "%a %b %d %H:%M:%S +0000 %Y")
    minus = datetime.datetime.now() - reg_time
    if minus.days < 50:
        return False
    text = dm['text']
    urlre = re.compile(r"[http|ftp]://(.*)[com|net|cn|org|gd|ly|me|info]")
    if len(urlre.findall(text)) != 0:
        return False
    numre = re.compile(r"13[0-9]|14[57]|15[0-35-9]|18[0-26-9]\d{8}")
    if len(numre.findall(text)) != 0:
        return False
    if '@' in text:
        return False
    return True

def main():
    tree = FanfouOAuth(CONSUMER_KEY, CONSUMER_SECRET)
    tree.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
    dms = json.loads(tree.fanfou_request("/direct_messages/inbox"))
    vaild_dms = []
    for dm in dms:
        if Check(dm):
            vaild_dms.append(dm)
        tree.fanfou_request("/direct_messages/destroy", post_args = {'id' : dm['id']})
    with TreeholesDB() as db:
        for dm in vaild_dms:
            # check 24 hour
            member = db.select_member_by_username(dm['sender']['id'])
            if member:
                delta_time = datetime.datetime.now() - datetime.datetime.strptime(member[0]["last_time"], "%Y-%m-%d %H:%M:%S.%f")
                if delta_time.days:
                    db.insert_status(dm['text'])
                    db.update_sender_time(dm['sender']['id'])
            else:
                db.insert_status(dm['text'])
                db.insert_member(dm['sender']['id'])
        db.commit()

if __name__ == '__main__':
    exit(main())
