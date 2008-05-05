#!/usr/bin/env python
# encoding: utf-8
"""
admin.py

Created by Pradeep Gowda on 2008-05-04.
Copyright (c) 2008 Yashotech. All rights reserved.
"""
import wsgiref.handlers

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users
from utils import TehRequestHandler, administrator

class AdminHandler(TehRequestHandler):
    @administrator
    def get(self):
        self.render("templates/admin.html")

class EntryListHandler(TehRequestHandler):
    @administrator
    def get(self):
        self.render("templates/admin_entrylist.html")

class ConfigHandler(TehRequestHandler):
    @administrator
    def get(self):
        self.render("templates/config.html")
    @administrator    
    def post(self):
        config = Config.all()
        config = config.fetch(1)[0]
        config.title = self.request.get("title")
        config.disqus = self.request.get("disqus")
        config.put()
        self.redirect('/')

