__author__ = 'aub3'
from cclib import commoncrawl13
from cclib.queue import FileQueue
from example_config import OUTPUT_S3_BUCKET, JOB_QUEUE
from boto.S3.connection import S3Connection


def process_queue(queue,crawl):
    for m in queue:
        process_file(crawl.get_file(m.get_body()))
        queue.delete_message(m)

def process_file(fileobj):
    count = 1
    for line in fileobj:
        if line[0]=='{' and 'tumblr.com' in line:
            print count,line
            count +=1

if __name__ == '__main__':
    crawl = commoncrawl13.CommonCrawl13()
    queue = FileQueue(JOB_QUEUE)
    process_queue(queue,crawl)