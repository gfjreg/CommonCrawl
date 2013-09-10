__author__ = 'aub3'
from google.appengine.ext import ndb
from indexer_model import *
from base import *

class Queue(ndb.Model):
    """
    List of files in queue or processed
    """
    files = ndb.StringProperty(repeated=True)


@ndb.transactional
def queue_files(add,remove,exclude,max_add=None):
    q = Queue.get_by_id("1")
    if q == None:
        q = Queue(id = "1")
    if add:
        current = set(q.files)
        add = add.difference(exclude) # excludes are stopped from being added
        if max_add and len(add) > max_add:
            new_files = list(add.difference(current))[:max_add]
            for fname in new_files:
                FILES.write(Message(body=fname))
            if q.files:
                q.files += new_files
            else:
                q.files = new_files
    if remove:
        current = set(q.files)
        q.files = list(current.difference_update(remove))
    q.put()

def get_queue_size():
    q = Queue.get_by_id("1")
    if q:
        return len(q.files)
    else:
        return 0


def add_files(remove=None,num=100):
    exclude = []
    for i in Indexer.query():
        exclude += i.files_processed
    queue_files(METADATA_FILES,set(),set(exclude),num)
