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
from google.appengine.api import urlfetch
import os
from lib import utils, markdown2, BeautifulSoup
from requesthandler import TehRequestHandler
from blog import Entry
from lib import demjson
from StringIO import StringIO

def make_entry(rec):
    """docstring for make_entry"""
    body = rec.get('body')
    body_html = markdown2.markdown(body)
    rec.update({'body_html': body_html})
    slug = rec.get('slug')
    title = rec.get('title')
    excerpt = rec.get('excerpt')
    markdown = rec.get('markdown') or 'markdown'
    tags = rec.get('tags') or []
    if len(tags) == 0:
        tags = ['general']
    tags = [db.Category(utils.slugify(tag)) for tag in tags if tag]
    
    static = rec.get('static')
    
    if not slug:
        utils.slugify(title)
        
    if not excerpt:
        soup = BeautifulSoup.BeautifulSoup(body_html)
        paras = soup.findAll('p')
        if paras:
            excerpt = paras[0].string
    return Entry(author=users.get_current_user(),
    title=title,
    slug=slug,
    body=body,
    body_html=body_html,
    markdown=markdown,
    excerpt=excerpt,
    tags= tags,
    static=static,
    )
    
class ShooinHandler(TehRequestHandler):
    def get(self,fname):        
        #url = 'http://localhost:8080/static/data/%s.json' % fname
        url = 'http://btbytes.com/default.json'
        response = urlfetch.fetch(url).content
        json = demjson.decode(response)
        titles = [r['title'] for r in json]
        for r in json:
            entry = make_entry(r)
            entry.put()
        
        self.render('templates/shooin.html', fname=fname, titles=titles)
        