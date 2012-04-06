# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: update.py
# CREATED: 15:37:11 14/03/2012
# MODIFIED: 15:43:56 14/03/2012

from db import TreeholesDB
from fanfou import FanfouOAuth

from config import *

def main():
    tree = FanfouOAuth(CONSUMER_KEY, CONSUMER_SECRET)
    tree.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
    with TreeholesDB() as db:
        statuses = db.select_unsent_status()
        for status in statuses:
            tree.fanfou_request("/statuses/update", post_args = {'status' : status['status'].encode("utf-8")})
            db.update_status_sent(status['id'])

if __name__ == '__main__':
    exit(main())
