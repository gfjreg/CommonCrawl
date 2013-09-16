__author__ = 'aub3'
from base import *
from models import *

def get_status():
    status = {}
    status['indexer_list'] = []
    status['project_list'] = {}
    project_entries_count = defaultdict(int)
    project_indexer_count = defaultdict(int)
    project_files_count = defaultdict(int)
    current_time = datetime.datetime.now()
    status['current_time'] = current_time
    status['projects_query_status'] = []
    for i in Indexer.query():
        minutes,seconds = divmod((i.last_contact - current_time).total_seconds(),60)
        status['indexer_list'].append((i.project_name,i.pid,"%s minutes and %s seconds ago"%(str(-1*minutes),str(int(round(seconds,0)))),len(i.files_processed),i.entries))
        if i.entries:
            project_entries_count[i.project_name] += i.entries
            project_files_count[i.project_name] += len(i.files_processed)
            project_indexer_count[i.project_name] += 1
    for q in Queue.query():
        status['project_list'][q.project_name]=(q.project_name,q.project_type,q.current_position,project_indexer_count[q.project_name],project_files_count[q.project_name],project_entries_count[q.project_name])
        if q.query_status:
            status['projects_query_status'].append(q.project_name)
    return status





class Add(BaseRequestHandler):
    def post(self):
        if PASSCODE == self.request.get("pass"):
            project_name = self.request.get("project_name")
            project_type = self.request.get("project_type")
            queue_status = self.request.get("queue_status")
            pid = increment_indexer_count()
            create_indexer(pid,project_name,project_type,queue_status)
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


indexer_routes= [('/Indexer/Add',Add),('/Indexer/Heartbeat',Heartbeat)]
