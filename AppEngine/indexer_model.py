__author__ = 'aub3'
from google.appengine.ext import ndb
from base import *

FILES = SQS.create_queue('datamininghobby_files')

class Indexer(ndb.Model):
  pid = ndb.IntegerProperty()
  last_contact = ndb.DateTimeProperty(auto_now=True)
  files_processed = ndb.StringProperty(repeated=True)
  entries = ndb.IntegerProperty()



def create_indexer(pid):
    i = Indexer.get_by_id(str(pid))
    if i is None:
        i = Indexer(id=str(pid))
    i.pid = pid
    queue = SQS.create_queue('datamininghobby_query_'+str(pid))
    queue.clear()
    i.files_processed = []
    i.put()
