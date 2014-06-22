__author__ = 'aub3'
import logging
from collections import defaultdict
from cclib import commoncrawl
from filequeue import FileQueue
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import json

from config import OUTPUT_S3_BUCKET, JOB_QUEUE, CRAWL_ID

logging.basicConfig(filename='worker.log',level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('boto').setLevel(logging.CRITICAL)

CONN = S3Connection()
BUCKET = CONN.get_bucket(OUTPUT_S3_BUCKET,validate=False)

def store_S3(fname,data):
    try:
        item = Key(BUCKET)
        item.key = str(hash(fname))+'.json'
        item.set_contents_from_string(json.dumps(data),reduced_redundancy=True) # reduced_redundancy=True to save costs
    except:
        logging.exception("error while storing data on S3")


def process_queue(queue,crawl,test=False):
    logging.debug("starting queue "+JOB_QUEUE)
    for m in queue:
        fname = m.get_body()
        logging.debug("starting "+fname)
        data = process_file(crawl.get_file(fname),fname,test)
        store_S3(fname,data)
        if test:
            logging.debug("did not delete the message")
            break # stop after processing one message
        else:
            queue.delete_message(m)
        logging.debug("finished "+fname)
    logging.debug("finished queue "+JOB_QUEUE)


def process_file(fileobj,filename,test=False):
    count = 0
    counts = defaultdict(int)
    amazon = []
    error = False
    try:
        for line in fileobj:
            line = line.strip()
            if line.startswith('WARC-Target-URI'):
                count += 1
                if "http://" in line:
                    counts[line.split('http://')[1].split('/')[0]] += 1
                    if "amazon.com" in line.lower():
                        amazon.append(line.split('WARC-Target-URI:')[1].strip())
    except:
        logging.exception("error while processing file")
        error =True
        pass
    return {'metdata_lines':count,
            'amazon':amazon,
            'counts':[(k,v) for k,v in counts.iteritems() if v>10],
            "filename":filename,
            "error":error
            }

if __name__ == '__main__':
    import sys
    if "test" in sys.argv:
        test = True
    else:
        test = False
    crawl = commoncrawl.CommonCrawl(CRAWL_ID)
    queue = FileQueue(JOB_QUEUE,files=None)
    process_queue(queue,crawl,test)