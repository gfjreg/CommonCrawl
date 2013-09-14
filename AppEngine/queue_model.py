__author__ = 'aub3'
from google.appengine.ext import ndb
from indexer_model import *
from base import *

class Queue(ndb.Model):
    """
    List of files in queue or processed
    """
    current_position = ndb.IntegerProperty()
    project_name = ndb.StringProperty()

def initialize_queue(project_name):
    q = Queue(id = project_name)
    q.current_position = 0
    q.project_name = project_name
    file_queue = SQS.create_queue(project_name+'_files')
    file_queue.clear()
    q.put()

@ndb.transactional
def get_current_position(num,project_name):
    q = Queue.get_by_id(project_name)
    if q == None:
        initialize_queue()
    if q.current_position == None:
        q.current_position = 0
    current_position = q.current_position
    q.current_position = q.current_position+num
    q.put()
    return current_position

def add_files_queue(num,project_name=None):
    if project_name:
        current_position = get_current_position(num,project_name)
        file_queue = SQS.get_queue(project_name+'_files')
        if current_position < len(METADATA_FILES):
            for fname in METADATA_FILES[current_position:num+current_position]:
                file_queue.write(Message(body=fname))
    else:
        project_list = []
        for q in Queue.query.get():
            project_list.append(q.project_name)
        for project_name in project_list:
            current_position = get_current_position(num,project_name)
            file_queue = SQS.get_queue(project_name+'_files')
            if current_position < len(METADATA_FILES):
                for fname in METADATA_FILES[current_position:num+current_position]:
                    file_queue.write(Message(body=fname))




