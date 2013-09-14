__author__ = 'aub3'
from google.appengine.ext import ndb
from base import *
from queue_model import *



class IndexCounter(ndb.Model):
    count = ndb.IntegerProperty(default=0)


def get_indexer_count():
    total = 0
    for counter in IndexCounter.query():
        total += counter.count
    return total



@ndb.transactional
def increment_indexer_count():
    counter = IndexCounter.get_by_id("0")
    if counter is None:
        counter = IndexCounter(id="0")
    counter.count += 1
    counter.put()
    return counter.count

class Indexer(ndb.Model):
  pid = ndb.IntegerProperty()
  last_contact = ndb.DateTimeProperty(auto_now=True)
  files_processed = ndb.StringProperty(repeated=True)
  project_name = ndb.StringProperty()
  entries = ndb.IntegerProperty()



def create_indexer(pid,project_name,project_type):
    q = Queue.get_by_id(project_name)
    if q is None:
        initialize_queue(project_name,project_type)
    i = Indexer.get_by_id(str(pid))
    if i is None:
        i = Indexer(id=str(pid))
    i.pid = pid
    i.project_name = project_name
    i.files_processed = []
    i.put()
    queue = SQS.create_queue(project_name+'_query_'+str(pid))
    queue.clear()

