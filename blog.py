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
from utils import TehRequestHandler, administrator
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
    comments = db.BooleanProperty()
    
    def url(self):
        if self.static == False: return '/entry/'+self.slug
        else: return '/'+self.slug
    
class EntryIndexHandler(TehRequestHandler):
    def get(self):
        entries = Entry.all().filter("static =", False)
        entries.order('-published')
        entries.fetch(999) #XXX: hardcoded; implement pagination
        pages = Entry.all().filter("static =", True)
        pages.order('-published')
        pages.fetch(999) #XXX: hardcoded; implement pagination
        self.render("templates/entryindex.html", entries=entries, pages=pages)

class EntryHandler(TehRequestHandler):
    def get(self, slug):
        admin = users.is_current_user_admin()
        entry = db.Query(Entry).filter("slug =", slug).filter("static = ", False).get()
        if not entry:
            raise webapp.Error(404)
        self.render("templates/entry.html", entry=entry)
        
class EntryDeleteHandler(TehRequestHandler):
        @administrator
        def get(self,slug):
            entry = db.Query(Entry).filter("slug =", slug).get()
            if not entry:
                raise webapp.Error(404)

            self.render("templates/del.html", entry=entry)

        @administrator
        def post(self,slug):
            entry = db.Query(Entry).filter("slug =", slug).get()
            if not entry:
                raise webapp.Error(404)
            delete = self.request.get("del")
            if delete and delete.upper() == 'Y':
                entry.delete()
            self.redirect('/entries')
                
class PageHandler(TehRequestHandler):
    def get(self, slug):
        admin = users.is_current_user_admin()
        entry = db.Query(Entry).filter("slug =", slug).filter("static =", True).get()
        if not entry:
            raise webapp.Error(404)
        self.render("templates/page.html", entry=entry)

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

def to_html(body,markdown):
    if markdown == 'markdown':
        body_html = markdown2.markdown(body)
    else:
        body_html = body
    return body_html
    

class NewEntryHandler(TehRequestHandler):
    @administrator
    def get(self,slug=None):
        if slug:
            entry = db.Query(Entry).filter("slug =", slug).get()
            if not entry:
                raise webapp.Error(404)
            self.render("templates/new.html", entry=entry)
        else: self.render("templates/new.html")
        
    @administrator
    def post(self,slug=None):
        title = self.request.get("title")
        body = self.request.get("body")
        markdown = self.request.get("markup")
        st  = self.request.get("static")
        cm  = self.request.get("comments")
        if st == '1': static = True
        else: static = False
        if cm  == '1': comments = True
        else: comments = False
        
        tags = self.request.get("tags")
        tags = tags.split(' ')
        if len(tags) == 0:
            tags = ['general']
        tags = [db.Category(utils.slugify(tag)) for tag in tags if tag]

        body_html = to_html(body,markdown)

        soup = BeautifulSoup.BeautifulSoup(body_html)
        paras = soup.findAll('p')
        
        if paras:
            excerpt = paras[0].string
        else: excerpt = ''
        
        entry = db.Query(Entry).filter("slug =", slug).get()
        if not entry:
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
                comments=comments,
            )
        else:
            entry.title = title
            entry.body = body
            entry.body_html = body_html
            entry.excerpt = excerpt
            entry.static = static
            entry.tags = tags
            entry.comments = comments
        entry.put()
        if static:
            self.redirect('/'+entry.slug)
        else:
            self.redirect("/entry/" + entry.slug)
