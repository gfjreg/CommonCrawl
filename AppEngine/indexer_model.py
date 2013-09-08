__author__ = 'aub3'
from google.appengine.ext import ndb

class Indexer(ndb.Model):
  pid = ndb.IntegerProperty()
  last_contact = ndb.StringProperty()
  files_processed = ndb.StringProperty(repeated=True)
