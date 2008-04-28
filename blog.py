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
from lib import utils, markdown2, BeautifulSoup
from requesthandler import TehRequestHandler
import shooin

class Entry(db.Model):
    author = db.UserProperty()
    title = db.StringProperty(required=True)
    slug = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    published = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    markdown = db.TextProperty()
    body_html = db.TextProperty()
    excerpt = db.TextProperty()
    tags = db.ListProperty(db.Category)
    static = db.BooleanProperty()
    
class EntryIndexHandler(TehRequestHandler):
    def get(self):
        entries = Entry.all().filter("static =", False)
        entries.order('-published')
        entries.fetch(limit=5)
        self.render("templates/entryindex.html", entries=entries, users=users)

class EntryHandler(TehRequestHandler):
    def get(self, slug):
        entry = db.Query(Entry).filter("slug =", slug).get()
        if not entry:
            raise webapp.Error(404)
        self.render("templates/entry.html", entry=entry)

class PageHandler(TehRequestHandler):
    def get(self, slug):
        page = db.Query(Entry).filter("slug =", slug).filter("static =", True).get()
        if not page:
            raise webapp.Error(404)
        self.render("templates/page.html", page=page)

class TagHandler(TehRequestHandler):
    def get(self, slug):
        entries = Entry.all().filter("tags =", slug).fetch(limit=10)
        message = 'Entries belonging to tag `%s`' %(slug, )
        if not entries:
            raise webapp.Error(404)
        self.render("templates/entryindex.html", entries=entries, message=message)
        

class FeedHandler(TehRequestHandler):
    def get(self):
        entries = Entry.all().filter("static =", False).order('-published').fetch(limit=10)
        #latest = db.Query(Entry).order('-published').fetch(limit=1)
        if entries:
            latest = entries[0]
        else:
            latest = None
            
        self.response.headers['Content-Type'] = 'application/atom+xml'
        self.render("templates/atom.xml", entries=entries, latest=latest)

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
        body = self.request.get("body")
        markdown = self.request.get("markup")
        excerpt = self.request.get("excerpt")
        st  = self.request.get("static")
        
        if st == '1':
            static = True
        else:
            static = False
            
        tags = self.request.get("tags")
        tags = tags.split(' ')
        if len(tags) == 0:
            tags = ['general']
        tags = [db.Category(utils.slugify(tag)) for tag in tags if tag]

        if markdown == 'markdown':
            body_html = markdown2.markdown(body)
        else:
            body_html = body

        if not excerpt:
            soup = BeautifulSoup.BeautifulSoup(body_html)
            paras = soup.findAll('p')
            if paras:
                excerpt = paras[0].string
                
        entry = Entry(
            author=users.get_current_user(),
            title=title,
            slug=utils.slugify(title),
            body=body,
            body_html=body_html,
            markdown=markdown,
            excerpt=excerpt,
            tags=tags,
            static=static,
        )
        entry.put()
        self.redirect("/entry/" + entry.slug)
