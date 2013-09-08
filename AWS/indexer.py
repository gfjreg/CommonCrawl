#!/usr/bin/env python
__author__ = 'aub3'
import logging,time,requests,sys,json,commoncrawl
from settings import AWS_KEY,AWS_SECRET
from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message
from settings import STORE_PATH

logging.basicConfig(filename='indexer.log',level=logging.ERROR,format='%(asctime)s %(message)s')
SQS = SQSConnection(AWS_KEY,AWS_SECRET)
RESULTS_QUEUE = SQS.get_queue("datamininghobby_results")
FILES_QUEUE = SQS.get_queue("datamininghobby_files")
Data = {}

def index_file(metadata_file):
    Data[metadata_file.path] = []
    try:
        for url,json_string in metadata_file.parse():
            if 'amazon.com' in json_string.lower():
                entry = commoncrawl.Metadata.extract_json(url,json_string)
                if entry:
                    Data[metadata_file.path].append((entry['url'],entry['url'],entry['title']))
                    for link in entry['links']:
                        Data[metadata_file.path].append((entry['url'],link[0],link[1]))
        metadata_file.clear()
    except:
        logging.exception(metadata_file.path)

def Search(q):
    " a naive search method"
    for data in Data.itervalues():
        count = 0
        for link1,link2,anchortext in data:
            if q in link1 or q in link2 or q in anchortext:
                count += 1
                if count > 5:
                    break
                else:
                    yield (link1,link2,anchortext)

def main_worker():
    r = requests.post(sys.argv[1]+'/Add')
    if r.status_code == 200:
        pid = int(r.json()['pid'])
    else:
        raise IOError
    print "indexer assigned id:",pid
    while 1:
        query_queue = SQS.get_queue("datamininghobby_query_"+str(pid))
        queries = query_queue.get_messages(10) # processes at most 10 queries at a time
        for query_message in queries:
            print "indexer",pid,query_message.get_body()
            query_queue.delete_message(query_message)
            q = query_message.get_body()
            result = ['\t'.join(k) for k in Search(q)]
            m = Message()
            m.set_body(json.dumps({'q':q,'results':result[:5]}))
            RESULTS_QUEUE.write(m)
            # there are numerous things which you can do here such as store data on S3 etc.
        file_messages = FILES_QUEUE.get_messages(1,5*60) # processes at most 1 file at a time
        params = {}
        for file_message in file_messages:
            metadata_file = commoncrawl.Metadata(file_message.get_body(),STORE_PATH)
            index_file(metadata_file)
            params={'file':file_message.get_body()}
            FILES_QUEUE.delete_message(file_message)
            r = requests.post(sys.argv[1]+'/Heartbeat/'+str(pid),params=params)
            if r.status_code != 200:
                raise IOError
        time.sleep(10)

if __name__ == '__main__':
        main_worker()
