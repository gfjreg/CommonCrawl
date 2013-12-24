#!/usr/bin/env python
# used for development when the AWS GUI is not sufficient
__author__ = 'aub3'
import logging,json,zlib
from settings import AWS_KEY,AWS_SECRET,PASSCODE,STORE_PATH,LOCAL
from boto.sqs.connection import SQSConnection
from boto.s3.connection import S3Connection
from boto.s3.key import Key

if not LOCAL:
    logging.basicConfig(filename='indexer.log',level=logging.ERROR,format='%(asctime)s %(message)s')

conn = S3Connection(AWS_KEY, AWS_SECRET)

def get_keys(bucket_name):
    bucket = conn.get_bucket(bucket_name)
    for key in bucket:
        yield key

def get_data(bucket_name):
    for key in get_keys(bucket_name):
        yield json.loads(zlib.decompress(key.get_contents_as_string()))



if __name__ == '__main__':
    bucket_name = "example_metadata_amazon_results"
    # size = 0
    # count = 0
    # for key in get_keys(bucket_name):
    #     size += key.size
    #     count += 1
    #     if count % 10000 == 0:
    #         print count,size
    # print count,size
    # 206404 22249666851


    # example for accessing stored data
    for links in get_data(bucket_name):
        for source_url,target_url in links:
            print source_url,'\t',target_url
        break
