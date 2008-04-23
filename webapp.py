#!/usr/bin/env python
# encoding: utf-8
"""
webapp.py

Created by Pradeep Gowda on 2008-04-23.
Copyright (c) 2008 Yashotech. All rights reserved.
"""
import wsgiref.handlers

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users
import functools
import os
import utils

class Entry(db.Model):
    author = db.UserProperty()
    title = db.StringProperty(required=True)
    slug = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    published = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)

class TehRequestHandler(webapp.RequestHandler):
    
    def __init__(self,**kw):
        webapp.RequestHandler.__init__(TehRequestHandler, **kw)
        
    def render(self, tmpl, **kw):
        template_values = dict(**kw)
        path = os.path.join(os.path.dirname(__file__), tmpl)
        self.response.out.write(template.render(path, template_values))
        
class MainPageHandler(TehRequestHandler):
    def get(self):
        entries = db.Query(Entry).order('-published').fetch(limit=5)
        self.render("templates/main.html", entries=entries, users=users)

class EntryIndexHandler(TehRequestHandler):
    def get(self):
        entries = db.Query(Entry).order('-published').fetch(limit=5)
        self.render("templates/entryindex.html", entries=entries, users=users)

class EntryHandler(TehRequestHandler):
    def get(self, slug):
        entry = db.Query(Entry).filter("slug =", slug).get()
        if not entry:
            raise webapp.Error(404)
        self.render("templates/entry.html", entry=entry)

class FeedHandler(TehRequestHandler):
    def get(self):
        entries = db.Query(Entry).order('-published').fetch(limit=10)
        self.set_header("Content-Type", "application/atom+xml")
        self.render("templates/atom.xml", entries=entries)

def administrator(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        user = users.get_current_user()
        if not user:
            if self.request.method == "GET":
                self.redirect(users.create_login_url(self.request.uri))
                return
        if not users.is_current_user_admin():
            raise webapp.Error(403)
        else:
            return method(self, *args, **kwargs)
    return wrapper

class NewEntryHandler(TehRequestHandler):
    @administrator
    def get(self):
        self.render("templates/new.html")

    @administrator
    def post(self):
        title = self.request.get("title")
        entry = Entry(
            author=users.get_current_user(),
            title=title,
            slug=utils.slugify(title),
            body=self.request.get("body"),
        )
        entry.put()
        self.redirect("/entry/" + entry.slug)

class LoginHandler(TehRequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
        else:
            self.redirect('/')

class LogoutHandler(TehRequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            self.redirect(users.create_logout_url('/'))
        else:
            self.redirect('/')

def main():
    application = webapp.WSGIApplication([
        (r"/", MainPageHandler),
        (r"/entries", EntryIndexHandler),
        (r"/feed", FeedHandler),
        (r"/entry/([^/]+)", EntryHandler),
        (r"/new", NewEntryHandler),
        (r"/login", LoginHandler),
        (r"/logout", LogoutHandler),
        ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()