# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: db.py
# CREATED: 15:21:15 14/03/2012
# MODIFIED: 12:18:47 06/04/2012

import sqlite3
import datetime

class TreeholesDB(object):
    def __init__(self):
        pass
    def __enter__(self):
        self._conn = sqlite3.connect('treeholes.db')
        self._conn.row_factory = sqlite3.Row
        return self
    def __exit__(self, type, value, traceback):
        self._conn.close()
    def _cur(self):
        return self._conn.cursor()
    def execute(self, sql, *args):
        cur = self._cur()
        return cur.execute(sql, args)
    def query(self, sql, *args):
        cur = self._cur()
        cur.execute(sql, args)
        return cur.fetchall()
    def commit(self):
        return self._conn.commit()
    def create_table(self):
        self.execute("CREATE TABLE `status`(`id` INTEGER PRIMARY KEY AUTOINCREMENT, `status` TEXT, `sent` INTEGER DEFAULT 0)")
        self.execute("CREATE TABLE `member`(`id` INTEGER PRIMARY KEY AUTOINCREMENT, `username` TEXT, `last_time` DATETIME)")
    def drop_table(self):
        self.execute("DROP TABLE IF EXISTS `status`")
        self.execute("DROP TABLE IF EXISTS `member`")
    def insert_status(self, status):
        self.execute("INSERT INTO `status`(`status`) VALUES(?)", status)
    def insert_member(self, username):
        self.execute("INSERT INTO `member`(`username`, `last_time`) VALUES(?, ?)", username, datetime.datetime.now())
    def update_status_sent(self, status_id):
        self.execute("UPDATE `status` SET sent = 1 WHERE id = ?", status_id)
    def update_sender_time(self, username):
        self.execute("UPDATE `member` SET `last_time` = ? WHERE `username` = ?", username)
    def select_unsent_status(self):
        return self.query("SELECT * FROM `status` WHERE `sent` = 0 LIMIT 5")
    def select_member_by_username(self, username):
        return self.query("SELECT * FROM `member` WHERE `username` = ?", username)

