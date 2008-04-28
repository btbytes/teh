#!/usr/bin/env python
# encoding: utf-8
"""
shooin.py

Created by Pradeep Gowda on 2008-04-24.
Copyright (c) 2008 Yashotech. All rights reserved.
"""

import wsgiref.handlers

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.api.urlfetch import fetch
import os
from lib import utils, markdown2, BeautifulSoup
from requesthandler import TehRequestHandler
from blog import Entry
from lib import demjson

class ShooinHandler(TehRequestHandler):
    def get(self,fname):

        data = demjson.encode(e, compactly=False)
        self.render('templates/shooin.html', fname=fname, data=data)
        