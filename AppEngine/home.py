__author__ = 'aub3'
from base import *
from models import *

QUERY_QUEUES = {}
class Home(BaseRequestHandler):
    def get(self):
        user = users.get_current_user()
        self.generate('home.html',get_status())

class Search(BaseRequestHandler):
    def get(self):
        query = self.request.get('q')
        project_name = self.request('project_name')
        for i in Indexer.query():
            if i.pid not in QUERY_QUEUES and i.queue_status and i.project_name == project_name:
                QUERY_QUEUES[i.pid] = SQS.create_queue("datamininghobby_query_"+str(i.pid))
            if i.queue_status:
                QUERY_QUEUES[i.pid].write(Message(body=query))
        self.generate_json("success")


home_routes = [('/',Home),('/Search/',Search),]
