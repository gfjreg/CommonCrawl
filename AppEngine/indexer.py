__author__ = 'aub3'
from base import *
from models import *


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


indexer_routes= [('/Indexer/Add',Add),('/Indexer/Heartbeat',Heartbeat)]
