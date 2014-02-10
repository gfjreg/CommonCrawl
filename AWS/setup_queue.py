__author__ = 'aub3'
import sys
from boto.S3.connection import S3Connection
from cclib.commoncrawl13 import CommonCrawl13
from cclib.queue import FileQueue
from example_config import OUTPUT_S3_BUCKET, JOB_QUEUE




if __name__ == '__main__':
    crawl = CommonCrawl13()
    wat_queue = FileQueue(JOB_QUEUE,crawl.wat)
    wat_queue.add_files(1)
    conn = S3Connection()
    conn.create_bucket(OUTPUT_S3_BUCKET)
