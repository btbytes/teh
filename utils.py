from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users
import os
import functools

class Config(db.Expando):
    title = db.StringProperty(required=True)

class TehRequestHandler(webapp.RequestHandler):    
    def __init__(self,**kw):
        webapp.RequestHandler.__init__(TehRequestHandler, **kw)
        
    def render(self, tmpl, **kw):
        template_values = dict(**kw)
        config = Config.all()
        config = config.fetch(1)[0]
        template_values.update({'config': config})
        template_values.update({'user': users.get_current_user()})
        template_values.update({'users': users})
        path = os.path.join(os.path.dirname(__file__), tmpl)
        self.response.out.write(template.render(path, template_values))

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
