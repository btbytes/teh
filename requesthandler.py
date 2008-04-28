from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users
import os

class TehRequestHandler(webapp.RequestHandler):
    
    def __init__(self,**kw):
        webapp.RequestHandler.__init__(TehRequestHandler, **kw)
        
    def render(self, tmpl, **kw):
        template_values = dict(**kw)
        template_values.update({'user': users.get_current_user()})
        template_values.update({'users': users})
        path = os.path.join(os.path.dirname(__file__), tmpl)
        self.response.out.write(template.render(path, template_values))
