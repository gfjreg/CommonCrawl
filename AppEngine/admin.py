__author__ = 'aub3'
#!/usr/bin/env python
from base import *
from indexer_model import *
from queue_model import *
import datetime
QUERY_QUEUES = {}

def get_status():
    status = {}
    status['indexer_list'] = []
    status['current_time'] = datetime.datetime.now()
    all_files_indexed = []
    for i in Indexer.query():
        status['indexer_list'].append((i.pid,i.last_contact,len(i.files_processed),i.entries))
        all_files_indexed += i.files_processed
    status['totat_metadata'] = len(METADATA_FILES)
    status['processed_metadata'] = len(all_files_indexed)
    # status['inprocess_metadata'] = FILES.count()
    return status

class Admin(BaseRequestHandler):
    def get(self):
        status = get_status()
        # status['status_success'] = "All is well in the wolrd"
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
        num = 500
        if add_files_queue(num):
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


