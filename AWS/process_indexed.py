#!/usr/bin/env python
__author__ = 'aub3'
import logging,time,requests,json,commoncrawl,marshal,zlib
from settings import AWS_KEY,AWS_SECRET,PASSCODE,STORE_PATH,LOCAL
from boto.sqs.connection import SQSConnection
from boto.s3.connection import S3Connection
from boto.s3.key import Key

if not LOCAL:
    logging.basicConfig(filename='indexer.log',level=logging.ERROR,format='%(asctime)s %(message)s')

S3 = S3Connection(AWS_KEY, AWS_SECRET)



