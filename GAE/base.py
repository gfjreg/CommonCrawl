#!/usr/bin/env python
import os,logging,json,webapp2,jinja2
from google.appengine.api import memcache
from google.appengine.api import users
#from keys import AWS_KEY,AWS_SECRET

jinja = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

try:
    LOCAL = os.environ['SERVER_SOFTWARE'].startswith('Dev')
except:
    LOCAL = False





class BaseRequestHandler(webapp2.RequestHandler):
    def generate(self, template_name, template_values=None,cache=True):
        user = users.GetCurrentUser()
        if template_values ==  None:
            template_values = {}
        values = {
          'request': self.request,
          'user': user,
          'login_url': users.CreateLoginURL(self.request.uri),
          'logout_url': users.CreateLogoutURL(self.request.uri),
          'application_name': 'Data_Mining_Hobby',
          'entry_values':template_values,
        }
        values.update(template_values)
        template = jinja.get_template(template_name)
        output = template.render(values, debug=LOCAL)
        if cache:
            try:
                memcache.add(self.request.uri,output,4*3600)
            except:
                logging.error('Error while adding to memcache key: '+self.request.uri)
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(output)

    def generate_json(self,output):
        self.response.headers['Content-Type'] = 'data/json'
        self.response.out.write(json.dumps(output))



            

