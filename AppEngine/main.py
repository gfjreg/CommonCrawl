#!/usr/bin/env python
from base import *
from indexer import *
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
    all_files_indexed = []
    for i in Indexer.query():
        status['indexer_list'].append((i.pid,i.last_contact,len(i.files_processed),i.entries))
        all_files_indexed.append(i.last_contact)
    status['totat_metadata'] = len(METADATA_FILES)
    status['processed_metadata'] = len(all_files_indexed)
    status['inprocess_metadata'] = len(METADATA_FILES)-len(all_files_indexed)
    return status

class Admin(BaseRequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            if users.is_current_user_admin():
                self.generate('admin.html',get_status())
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
                self.generate('admin.html',get_status())
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
    ] +Indexer_Routes
app = webapp2.WSGIApplication(Routes,debug = LOCAL)


