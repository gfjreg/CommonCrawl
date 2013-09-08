#!/usr/bin/env python
import logging,time,commoncrawl
from flask import Flask,jsonify,request
from settings import DEBUG,LOCAL,AWS_KEY,AWS_SECRET
from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message
from collections import defaultdict

logging.basicConfig(filename='server.log',level=logging.INFO,format='%(asctime)s %(message)s')

app = Flask(__name__)

SQS = SQSConnection(AWS_KEY,AWS_SECRET)
RESULTS_QUEUE = SQS.create_queue("datamininghobby_results")
RESULTS_QUEUE.clear()

QUERY_QUEUES = {}
Heartbeats = defaultdict(list)

FILES = SQS.create_queue('datamininghobby_files')
FILES.clear()


CRAWL = commoncrawl.CommonCrawl()
METADATA = CRAWL.metadata
del CRAWL


@app.route("/Search/<keyword>")
def search(keyword):
    m = Message()
    m.set_body(keyword)
    for Query_queues in QUERY_QUEUES.itervalues():
        Query_queues.write(m)
    return jsonify(query=keyword)


@app.route("/Add",methods=["POST"])
def add():
    pid = len(QUERY_QUEUES)
    QUERY_QUEUES[len(QUERY_QUEUES)] = SQS.create_queue('datamininghobby_query_'+str(pid))
    for _  in range(25): # 25 files per indexer process
        status = FILES.write(Message(body=METADATA.pop()))
    return jsonify(pid=pid)

@app.route("/Heartbeat/<pid>",methods=["POST"])
def heartbeat(pid):
    Heartbeats[pid].append((time.time(),request.args.get("file")))
    return jsonify(pid=pid)

@app.route("/Remove/<pid>")
def remove(pid):
    del QUERY_QUEUES[pid]
    del Heartbeats[pid]
    return jsonify(pid=pid)




@app.route("/")
def status():
    try:
        return jsonify(status='live',indexers=QUERY_QUEUES.keys())
    except:
        logging.exception('Status could not be reported')
        return ''


if __name__ == "__main__":
    if LOCAL:
        app.run(debug=True,port=8000)
    else:
        app.run(debug=DEBUG,port=80,host='0.0.0.0')








# """
# Examples of SQS
# """
# rs = q.get_messages(5)
# for m in rs:
#     print m.get_body()
#     q.delete_message(m)
# print q.count()
# q.clear() #expensive

# # How to write a message to a queue
# m = Message()
# m.set_body('This is my second message.')
# status = q.write(m)
