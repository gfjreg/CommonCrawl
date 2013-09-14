#!/usr/bin/env python
import os,gzip,zlib,logging,urllib2,marshal,json,webapp2,jinja2
import cPickle as pickle
from google.appengine.api import mail
from google.appengine.api import memcache
from google.appengine.api import users
from keys import AWS_KEY,AWS_SECRET,PASSCODE
from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message

QueueFiles = {'Metadata':[line.strip() for line in gzip.open('metadata.gz')],'Text':[line.strip() for line in gzip.open('text.gz')]}

# RAW_FILES = [line.strip() for line in gzip.open('metadata.gz')]


jinja = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
SQS = SQSConnection(AWS_KEY,AWS_SECRET)

try:
    LOCAL = os.environ['SERVER_SOFTWARE'].startswith('Dev')
except:
    LOCAL = False





class BaseRequestHandler(webapp2.RequestHandler):
    def get(self,*args,**kw):
        user = users.GetCurrentUser()
        self.get_child(*args,**kw)

    def generate(self, template_name, template_values={},cache=True):
        user = users.GetCurrentUser()
        values = {
          'request': self.request,
          'user': user,
          'login_url': users.CreateLoginURL(self.request.uri),
          'logout_url': users.CreateLogoutURL(self.request.uri),
          'application_name': 'Common_Crawl_Hobby',
          'entry_values':template_values,
        }
        values.update(template_values)
        template = jinja.get_template(template_name)
        output = template.render(values, debug=LOCAL)
        if cache:
            try:
##                    memcache.add(self.request.uri, zlib.compress(output),4*3600)
                memcache.add(self.request.uri,output,4*3600)
            except:
                logging.error('Error while adding to memcache key: '+self.request.uri)
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(output)

    def generate_json(self,output):
        self.response.headers['Content-Type'] = 'data/json'
        self.response.out.write(json.dumps(output))



            

