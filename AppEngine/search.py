__author__ = 'aub3'
from models import *
QUERY_QUEUES = {}

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


class IndexerResult(BaseRequestHandler):
    def post(self):
        if PASSCODE == self.request.get("pass"):
            pid = int(self.request.get("pid"))
            results = json.loads(self.request.get("results"))
            q = self.request.get('q')
            data_string = memcache.get("q/"+q)
            if data_string == None:
                data = {pid:results}
            else:
                data = json.loads(data_string)
                data[pid] = results
            memcache.set("q/"+q,json.dumps(data),3600*4)
            return self.generate_json([q,pid])
        else:
            return self.generate_json("Error: passcode mismatch")


search = [('/Search/',Search),]
