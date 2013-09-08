__author__ = 'aub3'
from google.appengine.ext import ndb
class Indexer(ndb.Model):
  pid = ndb.IntegerProperty()
  last_contact = ndb.DateTimeProperty(auto_now=True)
  files = ndb.StringProperty(repeated=True)
