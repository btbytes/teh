from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os

class TehRequestHandler(webapp.RequestHandler):
    
    def __init__(self,**kw):
        webapp.RequestHandler.__init__(TehRequestHandler, **kw)
        
    def render(self, tmpl, **kw):
        template_values = dict(**kw)
        path = os.path.join(os.path.dirname(__file__), tmpl)
        self.response.out.write(template.render(path, template_values))
