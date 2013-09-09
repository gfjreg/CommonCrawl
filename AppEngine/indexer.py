__author__ = 'aub3'
from base import *
from google.appengine.ext import ndb
from shardcounter import *

SQS = SQSConnection(AWS_KEY,AWS_SECRET)
FILES = SQS.create_queue('datamininghobby_files')

METADATA_FILES = [line.strip() for line in gzip.open('metadata.gz')]
# TEXT_FILES = [line.strip() for line in gzip.open('text.gz')]
# RAW_FILES = [line.strip() for line in gzip.open('metadata.gz')]

class Indexer(ndb.Model):
  pid = ndb.IntegerProperty()
  last_contact = ndb.DateTimeProperty(auto_now=True)
  files_processed = ndb.StringProperty(repeated=True)
  entries = ndb.IntegerProperty()

def add_files(num=25):
    increment_file_count(num)
    end = get_file_count()
    if end > len(METADATA_FILES)+num:
        end  = end - len(METADATA_FILES)
    start = end - num
    for fname in METADATA_FILES[start:end]:
        FILES.write(Message(body=fname))

def create_indexer(pid):
    i = Indexer.get_by_id(str(pid))
    if i is None:
        i = Indexer(id=str(pid))
    i.pid = pid
    queue = SQS.create_queue('datamininghobby_query_'+str(pid))
    queue.clear()
    i.files_processed = []
    i.put()

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