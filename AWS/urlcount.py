__author__ = 'aub3'
from cclib import commoncrawl13
from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message

SQS = SQSConnection()



if __name__ == '__main__':
    crawl = commoncrawl13.CommonCrawl13()
