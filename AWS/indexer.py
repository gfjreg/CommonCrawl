#!/usr/bin/env python
from AWS import commoncrawl

__author__ = 'aub3'
import logging,time,requests, marshal,zlib
from settings import AWS_KEY,AWS_SECRET,PASSCODE,STORE_PATH,LOCAL
from boto.sqs.connection import SQSConnection
from boto.s3.connection import S3Connection
from boto.s3.key import Key

if not LOCAL:
    logging.basicConfig(filename='indexer.log',level=logging.ERROR,format='%(asctime)s %(message)s')



class Indexer(object):
    def __init__(self,server,project_name,project_type,query_status):
        self.project_name = project_name
        self.project_type = project_type
        self.query_status = query_status
        self.server = server
        data={'pass':PASSCODE,
              'project_name':self.project_name,
              'project_type':self.project_type,
              'query_status':self.query_status}
        r = requests.post(self.server+'/Indexer/Add',data)
        if r.status_code == 200:
            self.pid = int(r.json()['pid'])
        print "indexer assigned id:",self.pid
        self.SQS = SQSConnection(AWS_KEY,AWS_SECRET)
        self.S3 = S3Connection(AWS_KEY, AWS_SECRET)
        self.bucket = self.S3.create_bucket(project_name.lower()+'_results')
        self.FILES_QUEUE = self.SQS.get_queue(project_name+"_files")
        if self.query_status:
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
        # hook for proecessing queries in query queue
        pass

    def process_query_queue(self):
        # processes at most 10 queries at a time
        query_processed = False
        for query_message in self.QUERY_QUEUE.get_messages(10):
            query_processed = True
            self.process_query(query_message)
            self.QUERY_QUEUE.delete_message(query_message)
        return query_processed

    def process_file(self,file_message):
        if self.project_type == "Metadata":
            self.index_file(commoncrawl.Metadata(file_message.get_body(),STORE_PATH))
        elif self.project_type == "Text":
            self.index_file(commoncrawl.Text(file_message.get_body(),STORE_PATH))
        self.files.append(file_message.get_body())
        print self.pid," indexed ",file_message.get_body()," total entries",self.entry_count
        self.heartbeat(file_message.get_body())
        self.FILES_QUEUE.delete_message(file_message)

    def process_file_queue(self):
        file_processed = False
        for file_message in self.FILES_QUEUE.get_messages(1,visibility_timeout=10*60):
            file_processed = True
            self.process_file(file_message)
        return file_processed

    def work_loop(self):
        while 1:
            query_processed = False
            if self.query_status:
                query_processed = self.process_query_queue()
            file_processed = self.process_file_queue()
            self.counter += 1
            if file_processed:
                self.heartbeat()
            elif not query_processed:
                time.sleep(60) # pause for a minute before checking again for new queries


    def heartbeat(self,fname=""):
        r = requests.post(self.server+'/Indexer/Heartbeat',data={'pass':PASSCODE,'filename':fname,'entries':self.entry_count,'pid':self.pid,'project_name':self.project_name,'project_type':self.project_type})

