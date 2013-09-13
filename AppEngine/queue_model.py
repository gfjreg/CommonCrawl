__author__ = 'aub3'
from google.appengine.ext import ndb
from indexer_model import *
from base import *

class Queue(ndb.Model):
    """
    List of files in queue or processed
    """
    current_position = ndb.IntegerProperty()

def initialize_queue():
    FILES.clear()
    q = Queue(id = "1")
    q.current_position = 0
    q.put()

@ndb.transactional
def get_current_position(num):
    q = Queue.get_by_id("1")
    if q == None:
        initialize_queue()
    if q.current_position == None:
        q.current_position = 0
    current_position = q.current_position
    q.current_position = q.current_position+num
    q.put()
    return current_position

def add_files_queue(num):
    current_position = get_current_position(num)
    if current_position < len(METADATA_FILES):
        for fname in METADATA_FILES[current_position:num+current_position]:
            FILES.write(Message(body=fname))
    else:
        return False





