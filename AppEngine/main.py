#!/usr/bin/env python
from base import *
from indexer import *
import datetime
QUERY_QUEUES = {}


class Home(BaseRequestHandler):
    def get(self):
        user = users.get_current_user()
        self.generate('home.html')

class Search(BaseRequestHandler):
    def get(self):
        query = self.request.get('q')
        for i in Indexer.query():
            if i.pid not in QUERY_QUEUES:
                QUERY_QUEUES[i.pid] = SQS.create_queue("datamininghobby_query_"+str(i.pid))
            QUERY_QUEUES[i.pid].write(Message(body=query))
        self.generate_json("success")


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
    status['inprocess_metadata'] = get_queue_size() - len(all_files_indexed)
    return status

class Admin(BaseRequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            if users.is_current_user_admin():
                status = get_status()
                # status['status_success'] = "All is well in the wolrd"
                self.generate('admin.html',status)
                return
            else:
                self.redirect("/")
                return
        else:
            self.redirect(users.CreateLoginURL("/Admin"))
            return

    def post(self):
        user = users.get_current_user()
        if user:
            if users.is_current_user_admin():
                status = get_status()
                try:
                    num = int(self.request.get('num',0))
                    add_files(num)
                    status['status_success'] = "Added "+str(num)+" files to the queue"
                except:
                    status['status_error'] = "Error while adding files to the queue"
                self.generate('admin.html',status)
                return
            else:
                self.redirect("/")
                return
        else:
            self.redirect(users.CreateLoginURL("/Admin"))
            return

class IndexerDelete(BaseRequestHandler):
    def get(self,pid):
        user = users.get_current_user()
        if user:
            if users.is_current_user_admin():
                i = Indexer.get_by_id(str(pid))
                status = {}
                if i:
                    add_files(remove=set(i.files_processed))
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
            else:
                self.redirect("/")
                return
        else:
            self.redirect(users.CreateLoginURL("/Admin"))
            return

class IndexerInfo(BaseRequestHandler):
    def get(self,pid):
        user = users.get_current_user()
        if user:
            if users.is_current_user_admin():
                i = Indexer.get_by_id(str(pid))
                status = {}
                if i:
                    status = {'indexer':(i.pid,i.last_contact,i.files_processed,i.entries)}
                else:
                    status['status_error'] = 'Could not find indexer '+pid
                status.update(get_status())
                self.generate('admin.html',status)
                return
            else:
                self.redirect("/")
                return
        else:
            self.redirect(users.CreateLoginURL("/Admin"))
            return


if LOCAL:
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.getLogger().setLevel(logging.INFO)
Routes = [
    ('/',Home),
    ('/Search/',Search),
    ('/Admin',Admin),
    ('/Admin/Delete/(.*)',IndexerDelete),
    ('/Admin/Info/(.*)',IndexerInfo),
    ] + Indexer_Routes
app = webapp2.WSGIApplication(Routes,debug = LOCAL)


