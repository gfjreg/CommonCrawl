#!/usr/bin/env python
from base import *
from indexer import *



# # RESULTS_QUEUE.clear()
# QUERY_QUEUES = {}
# Heartbeats = {}
#
# SQS = SQSConnection(AWS_KEY,AWS_SECRET)
# FILES = SQS.get_queue('datamininghobby_files')


# def set_current_server(location):
#     server = Server_Location(key=Server_Key,location='http://'+location.replace('http://','').strip())
#     server.put()
#
# def get_current_server():
#     return Server_Key.get().location


RESULTS_QUEUE = SQS.create_queue("datamininghobby_results")
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



class Admin(BaseRequestHandler):
    def get(self):
        user = users.get_current_user()
        if user and users.is_current_user_admin():
            self.generate('admin.html')
            return
        else:
            self.redirect(users.CreateLoginURL("/"))
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


