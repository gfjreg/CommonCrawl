#!/usr/bin/env python
__author__ = 'aub3'
import logging,time,requests,json,commoncrawl
from settings import AWS_KEY,AWS_SECRET,PASSCODE,STORE_PATH,LOCAL
from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message
logging.basicConfig(filename='indexer.log',level=logging.ERROR,format='%(asctime)s %(message)s')



class Indexer:
    def __init__(self,server,selector='amazon.com'):
        self.server = server
        r = requests.post(self.server+'/Indexer/Add',data={'pass':PASSCODE})
        if r.status_code == 200:
            self.pid = int(r.json()['pid'])
        print "indexer assigned id:",self.pid
        self.selector = selector
        self.Data = {}
        SQS = SQSConnection(AWS_KEY,AWS_SECRET)
        self.FILES_QUEUE = SQS.get_queue("datamininghobby_files")
        self.QUERY_QUEUE = SQS.get_queue("datamininghobby_query_"+str(self.pid))
        self.counter = 0
        self.files = [ ]
        self.entry_count = 0
        self.backup_path = ""

    def index_file(self,metadata_file):
        self.Data[metadata_file.path] = []
        try:
            for url,json_string in metadata_file.parse():
                if self.selector in json_string.lower():
                    entry = commoncrawl.Metadata.extract_json(url,json_string)
                    if entry:
                        self.Data[metadata_file.path].append((entry['url'],entry['url'],entry['title']))
                        for link in entry['links']:
                            if self.selector in link[0] or self.selector in link[1]:
                                self.Data[metadata_file.path].append((entry['url'],link[0],link[1]))
            metadata_file.clear()
            self.entry_count += len(self.Data[metadata_file.path])
        except:
            logging.exception(metadata_file.path)

    def Search(self,q):
        " a naive search"
        for data in self.Data.itervalues():
            count = 0
            for link1,link2,anchortext in data:
                if q in link1 or q in link2 or q in anchortext:
                    count += 1
                    if count > 5:
                        break
                    else:
                        yield (link1,link2,anchortext)

    def backup(self):
        pass

    def process_query(self,query_message):
        print "indexer",self.pid,query_message.get_body()
        self.QUERY_QUEUE.delete_message(query_message)
        q = query_message.get_body()
        result = [k for k in self.Search(q)]
        # while we post the results back to server, you can do what ever you would like such as storing huge blobs of results on S3
        r = requests.post(self.server+'/Indexer/Result',data ={'pass':PASSCODE,'pid':self.pid,'q':q,'results':json.dumps(result[:5])})
        del result

    def process_file(self,file_message):
        metadata_file = commoncrawl.Metadata(file_message.get_body(),STORE_PATH)
        self.index_file(metadata_file)
        self.files.append(file_message.get_body())
        print self.pid," indexed ",file_message.get_body()," total entries",self.entry_count
        self.heartbeat(file_message.get_body())
        self.FILES_QUEUE.delete_message(file_message)


    def work_loop(self):
        while 1:
            file_processed = False
            # processes at most 10 queries at a time
            for query_message in self.QUERY_QUEUE.get_messages(10):
                self.process_query(query_message)
            # there are numerous things which you can do here such as store data on S3 etc.
            for file_message in self.FILES_QUEUE.get_messages(1,5*60):
                file_processed = True
                self.process_file(file_message)
            self.counter += 1
            if self.counter == 10: # approximately every 3 minutes or an extra call after 10 files
                self.heartbeat()
                self.counter = 0
            if not file_processed: # if no file was processed the sleep for thirty seconds
                time.sleep(30)

    def heartbeat(self,fname=""):
        r = requests.post(self.server+'/Indexer/Heartbeat',data={'pass':PASSCODE,'filename':fname,'entries':self.entry_count,'pid':self.pid})

if __name__ == '__main__':
    import sys
    try:
        backup_path = sys.argv[1]
    except:
        backup_path = ''
    if LOCAL:
        indexer = Indexer(server="http://localhost:14080")
    else:
        indexer = Indexer(server="http://www.datamininghobby.com",backup_path=backup_path)
    indexer.work_loop()
