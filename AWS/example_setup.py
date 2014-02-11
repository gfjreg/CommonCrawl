__author__ = 'aub3'
import sys,logging
from boto.s3.connection import S3Connection
from cclib.commoncrawl13 import CommonCrawl13
from cclib.queue import FileQueue
from example_config import OUTPUT_S3_BUCKET, JOB_QUEUE
logging.basicConfig(filename='logs/setup.log',level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('boto').setLevel(logging.CRITICAL)



if __name__ == '__main__':
    crawl = CommonCrawl13()
    file_list = crawl.wat
    wat_queue = FileQueue(JOB_QUEUE,file_list)
    logging.debug("Adding "+str(len(file_list))+" files to queue "+JOB_QUEUE)
    wat_queue.add_files()
    conn = S3Connection()
    logging.debug("Creating bucket "+OUTPUT_S3_BUCKET)
    conn.create_bucket(OUTPUT_S3_BUCKET)
