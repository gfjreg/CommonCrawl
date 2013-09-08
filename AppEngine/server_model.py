__author__ = 'aub3'
from google.appengine.ext import ndb

class Server_Location(ndb.Model):
  location = ndb.StringProperty()

Server_Key = ndb.Key(Server_Location, 'EC2')
