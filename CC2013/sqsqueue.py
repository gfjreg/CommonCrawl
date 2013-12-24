__author__ = 'aub3'
from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message
from settings import AWS_KEY,AWS_SECRET

class FileQueue(object):
    """
    A queue of files stored on SQS.
    """
    SQS = SQSConnection(AWS_KEY,AWS_SECRET)

    def __init__(self,name,files,N=1):
        """
        Requires list of files and queue name and optionally number of files per entry
        """
        self.name = name
        self.files = files
        self.N = N
        self.queue = FileQueue.SQS.create_queue(self.name)


if __name__ == '__main__':
    import commoncrawl13
    crawl = commoncrawl13.CommonCrawl13('data/crawl_index.gz')
    wat_queue = FileQueue()

