__author__ = 'aub3'
#!/usr/bin/env python
from base import *
from indexer_model import *
from collections import defaultdict
import datetime
QUERY_QUEUES = {}

def get_status():
    status = {}
    status['indexer_list'] = []
    status['project_list'] = {}
    project_entries_count = defaultdict(int)
    project_files_count = defaultdict(int)
    current_time = datetime.datetime.now()
    status['current_time'] = current_time
    for i in Indexer.query():
        minutes,seconds = divmod((i.last_contact - current_time).total_seconds(),60)
        status['indexer_list'].append((i.project_name,i.pid,"%s minutes and %s seconds ago"%(str(-1*minutes),str(int(round(seconds,0)))),len(i.files_processed),i.entries))
        if i.entries:
            project_entries_count[i.project_name] += i.entries
            project_files_count[i.project_name] += len(i.files_processed)
    for q in Queue.query():
        status['project_list'][q.project_name]=(q.project_name,q.current_position,len(project_files_count),project_files_count[q.project_name],project_entries_count[q.project_name])
    return status

class Admin(BaseRequestHandler):
    def get(self):
        status = get_status()
        self.generate('admin.html',status)
        return

    def post(self):
        status = get_status()
        try:
            num = int(self.request.get('num',0))
            if add_files_queue(num):
                status['status_success'] = "Added "+str(num)+" files to the queue"
            else:
                status['status_error'] = "Error while adding files to the queue"
        except:
            status['status_error'] = "Error while adding files to the queue"
        self.generate('admin.html',status)
        return

class UpdateQueue(BaseRequestHandler):
    def get(self):
        num = 10
        if add_files_queue(num,project_name=None):
            self.generate_json({'num':num})
        else:
            self.generate_json({'num':False})




class IndexerDelete(BaseRequestHandler):
    def get(self,pid):
        i = Indexer.get_by_id(str(pid))
        status = {}
        if i:
            i.key.delete()
            if pid not in QUERY_QUEUES:
                QUERY_QUEUES[pid] = SQS.get_queue("datamininghobby_query_"+str(pid))
            if QUERY_QUEUES[pid]:
                QUERY_QUEUES[pid].clear()
                QUERY_QUEUES[pid].delete()
            del QUERY_QUEUES[pid]
            status['status_success'] = 'Deleted indexer '+pid
        else:
            status['status_error'] = 'Could not find indexer '+pid
        status.update(get_status())
        self.generate('admin.html',status)
        return


class IndexerInfo(BaseRequestHandler):
    def get(self,pid):
        i = Indexer.get_by_id(str(pid))
        status = {}
        if i:
            status = {'indexer':(i.pid,i.last_contact,i.files_processed,i.entries)}
        else:
            status['status_error'] = 'Could not find indexer '+pid
        status.update(get_status())
        self.generate('admin.html',status)


if LOCAL:
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.getLogger().setLevel(logging.INFO)

Routes = [
    ('/',Admin),
    ('/Admin/',Admin),
    ('/Admin/Queue/',UpdateQueue),
    ('/Admin/Delete/(.*)',IndexerDelete),
    ('/Admin/Info/(.*)',IndexerInfo),
    ]
app = webapp2.WSGIApplication(Routes,debug = LOCAL)


