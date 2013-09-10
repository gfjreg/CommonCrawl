__author__ = 'aub3'
from base import *
from indexer_model import *
from shardcounter import *
from queue_model import *



class Add(BaseRequestHandler):
    def post(self):
        if PASSCODE == self.request.get("pass"):
            increment_indexer_count()
            pid = get_indexer_count()
            create_indexer(pid)
            add_files()
            return self.generate_json({'pid':pid})
        else:
            return self.generate_json("Error: passcode mismatch")

class Heartbeat(BaseRequestHandler):
    def post(self):
        if PASSCODE == self.request.get("pass"):
            pid = int(self.request.get("pid"))
            filename = self.request.get("filename")
            i = Indexer.get_by_id(str(pid))
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


Indexer_Routes = [
    ('/Indexer/Add',Add),
    ('/Indexer/Heartbeat',Heartbeat),
    ('/Indexer/Result',IndexerResult),
    ]