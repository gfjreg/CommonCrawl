#!/usr/bin/env python
from base import *
from indexer_model import *
import datetime
from collections import defaultdict

QUERY_QUEUES = {}

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






class Add(BaseRequestHandler):
    def post(self):
        if PASSCODE == self.request.get("pass"):
            project_name = self.request.get("project_name")
            project_type = self.request.get("project_type")
            pid = increment_indexer_count()
            create_indexer(pid,project_name,project_type)
            add_files_queue(5,project_name)
            return self.generate_json({'pid':pid})
        else:
            return self.generate_json("Error: passcode mismatch")

class Heartbeat(BaseRequestHandler):
    def post(self):
        if PASSCODE == self.request.get("pass"):
            pid = int(self.request.get("pid"))
            filename = self.request.get("filename","")
            i = Indexer.get_by_id(str(pid))
            if filename.strip() == "":
                add_files_queue(50,i.project_name)
            else:
                i.entries = int(self.request.get("entries"))
                if filename.strip():
                    i.files_processed.append(filename)
                i.put()
            return self.generate_json({'pid':pid})
        else:
            return self.generate_json("Error: passcode mismatch")

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


class Home(BaseRequestHandler):
    def get(self):
        user = users.get_current_user()
        self.generate('home.html',get_status())

class Search(BaseRequestHandler):
    def get(self):
        query = self.request.get('q')
        for i in Indexer.query():
            if i.pid not in QUERY_QUEUES:
                QUERY_QUEUES[i.pid] = SQS.create_queue("datamininghobby_query_"+str(i.pid))
            QUERY_QUEUES[i.pid].write(Message(body=query))
        self.generate_json("success")



if LOCAL:
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.getLogger().setLevel(logging.INFO)

Routes = [('/',Home),
          ('/Search/',Search),
          ('/Indexer/Add',Add),
          ('/Indexer/Heartbeat',Heartbeat),
          ('/Indexer/Result',IndexerResult),
        ]
app = webapp2.WSGIApplication(Routes,debug = LOCAL)


