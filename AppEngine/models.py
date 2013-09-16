__author__ = 'aub3'
from google.appengine.ext import ndb
from base import *

class Queue(ndb.Model):
    """
    List of files in queue or processed
    """
    current_position = ndb.IntegerProperty()
    project_name = ndb.StringProperty()
    project_type = ndb.StringProperty()


def initialize_queue(project_name,project_type):
    q = Queue(id = project_name)
    q.current_position = 0
    q.project_name = project_name
    q.project_type = project_type
    file_queue = SQS.create_queue(project_name+'_files')
    file_queue.clear()
    q.put()

@ndb.transactional
def increment_current_position(num,project_name):
    q = Queue.get_by_id(project_name)
    if q == None:
        initialize_queue()
    if q.current_position == None:
        q.current_position = 0
    current_position = q.current_position
    q.current_position = q.current_position+num
    project_type = q.project_type
    q.put()
    return current_position,project_type



def add_files_queue(num,project_name=None,):
    if project_name:
        current_position,project_type = increment_current_position(num,project_name)
        file_queue = SQS.get_queue(project_name+'_files')
        if current_position < len(QueueFiles[project_type]):
            for fname in QueueFiles[project_type][current_position:num+current_position]:
                file_queue.write(Message(body=fname))
    else:
        project_list = []
        for q in Queue.query():
            project_list.append(q.project_name)
        for project_name in project_list:
            current_position,project_type = increment_current_position(num,project_name)
            file_queue = SQS.get_queue(project_name+'_files')
            if current_position < len(QueueFiles[project_type]):
                for fname in QueueFiles[project_type][current_position:num+current_position]:
                    file_queue.write(Message(body=fname))

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

def delete_indexer(pid):
    i = Indexer.get_by_id(str(pid))
    i.key().delete()

def get_status():
    status = {}
    status['indexer_list'] = []
    status['project_list'] = {}
    project_entries_count = defaultdict(int)
    project_indexer_count = defaultdict(int)
    project_files_count = defaultdict(int)
    current_time = datetime.datetime.now()
    status['current_time'] = current_time
    for i in Indexer.query():
        minutes,seconds = divmod((i.last_contact - current_time).total_seconds(),60)
        status['indexer_list'].append((i.project_name,i.pid,"%s minutes and %s seconds ago"%(str(-1*minutes),str(int(round(seconds,0)))),len(i.files_processed),i.entries))
        if i.entries:
            project_entries_count[i.project_name] += i.entries
            project_files_count[i.project_name] += len(i.files_processed)
            project_indexer_count[i.project_name] += 1
    for q in Queue.query():
        status['project_list'][q.project_name]=(q.project_name,q.project_type,q.current_position,project_indexer_count[q.project_name],project_files_count[q.project_name],project_entries_count[q.project_name])
    return status
