__author__ = 'aub3'
from cclib import commoncrawl13
from cclib.queue import FileQueue
from config import OUTPUT_S3_BUCKET, JOB_QUEUE
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import gzip,logging,StringIO
logging.basicConfig(filename='logs/worker.log',level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('boto').setLevel(logging.CRITICAL)

CONN = S3Connection()
BUCKET = CONN.get_bucket(OUTPUT_S3_BUCKET,validate=False)

def Store_S3(fname,data):
    try:
        item = Key(BUCKET)
        item.key = JOB_QUEUE+'_'+str(hash(fname))
        out = StringIO.StringIO()
        payload = '\n'.join(data)
        f = gzip.GzipFile(fileobj=out, mode="w")
        f.write(payload)
        f.close()
        item.set_contents_from_string(out.getvalue(),reduced_redundancy=True) # reduced_redundancy=True to save costs
        out.close()
        logging.info(len(data))
    except:
        logging.exception("error while storing data on S3")


def process_queue(queue,crawl):
    logging.debug("starting queue "+JOB_QUEUE)
    for m in queue:
        fname = m.get_body()
        logging.debug("starting "+fname)
        data = process_file(crawl.get_file(fname))
        Store_S3(fname,data)
        queue.delete_message(m)
        logging.debug("finished "+fname)
    logging.debug("finished queue "+JOB_QUEUE)


def process_file(fileobj):
    try:
        return [line for line in fileobj if line[0] == '{' and 'tumblr.com' in line] # returns all lines with JSON encoding which contains facebook.com
    except:
        logging.exception(" error while processing file")

if __name__ == '__main__':
    crawl = commoncrawl13.CommonCrawl13()
    queue = FileQueue(JOB_QUEUE,files=None)
    process_queue(queue,crawl)