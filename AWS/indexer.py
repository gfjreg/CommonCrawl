#!/usr/bin/env python
__author__ = 'aub3'
import logging,time,requests,json,commoncrawl,marshal,zlib
from settings import AWS_KEY,AWS_SECRET,PASSCODE,STORE_PATH,LOCAL
from boto.sqs.connection import SQSConnection
from boto.s3.connection import S3Connection
from boto.s3.key import Key

if not LOCAL:
    logging.basicConfig(filename='indexer.log',level=logging.ERROR,format='%(asctime)s %(message)s')



class Indexer(object):
    def __init__(self,server,project_name):
        self.project_name = project_name
        self.server = server
        r = requests.post(self.server+'/Indexer/Add',data={'pass':PASSCODE,'project_name':self.project_name})
        if r.status_code == 200:
            self.pid = int(r.json()['pid'])
        print "indexer assigned id:",self.pid
        self.SQS = SQSConnection(AWS_KEY,AWS_SECRET)
        self.S3 = S3Connection(AWS_KEY, AWS_SECRET)
        self.bucket = self.S3.create_bucket(project_name+'_results')
        self.FILES_QUEUE = self.SQS.get_queue(project_name+"_files")
        self.QUERY_QUEUE = self.SQS.get_queue(project_name+"_query_"+str(self.pid))
        self.counter = 0
        self.files = []
        self.entry_count = 0
        self.backup_path = ""

    def index_file(self,metadata_file):
        # hook for processing files in the index queue
        pass


    def backup_s3(self,key,data):
        if data:
            k = Key(self.bucket)
            k.storage_class = 'REDUCED_REDUNDANCY'
            k.key = key
            k.set_contents_from_string(zlib.compress(marshal.dumps(data)))
            k.close()

    def process_query(self,query_message):
        pass

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
            for file_message in self.FILES_QUEUE.get_messages(1,visibility_timeout=10*60):
                file_processed = True
                self.process_file(file_message)
            self.counter += 1
            if self.counter == 10: # approximately every 3 minutes or an extra call after 10 files
                self.heartbeat()
                self.counter = 0
            if not file_processed: # if no file was processed the sleep for thirty seconds
                time.sleep(30)

    def heartbeat(self,fname=""):

        r = requests.post(self.server+'/Indexer/Heartbeat',data={'pass':PASSCODE,'filename':fname,'entries':self.entry_count,'pid':self.pid,'project_name':self.project_name})

