#!/usr/bin/env python
import os,gzip,zlib,logging,urllib2,marshal,json,webapp2,jinja2,datetime
from google.appengine.api import mail
from google.appengine.api import memcache
from google.appengine.api import users
from config.keys import AWS_KEY,AWS_SECRET,PASSCODE
from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message
from collections import defaultdict
import cPickle as pickle

QueueFiles = {'Metadata':[line.strip() for line in gzip.open('data/metadata.gz')],'Text':[line.strip() for line in gzip.open('data/text.gz')]}


jinja = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
SQS = SQSConnection(AWS_KEY,AWS_SECRET)

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
          'application_name': 'Common_Crawl_Hobby',
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



            

